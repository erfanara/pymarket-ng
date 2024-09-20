import pandas as pd


# from pymarketng.application.Statistics import (
#     maximum_aggregated_utility,
#     maximum_traded_volume,
# )
from pymarketng.application.UserManager import UserManager
# from pymarketng.domain.Bid import Bid

# TODO: adding time
# BidsManager AKA Round
class BidsManager:
    df_template = {
        "time": pd.Series(dtype="datetime64[ns]"),
        "price": pd.Series(dtype="float"),
        "unit": pd.Series(dtype="float"),
        "is_buying": pd.Series(dtype="bool"),
        "user": pd.Series(dtype="int"),
    }
    tmp_df = pd.DataFrame(df_template)


    def __init__(
        self,
        buyers=pd.DataFrame(df_template),
        sellers=pd.DataFrame(df_template),
    ) -> None:
        # TODO: validation
        self.sellers: pd.DataFrame = sellers
        self.buyers: pd.DataFrame = buyers
        self.um = UserManager()


    def validate_df(self, bids_df: pd.DataFrame):
        columns_validated = [col in bids_df.columns for col in self.tmp_df.columns]
        types_validated = [bids_df[col].dtype == self.tmp_df[col].dtype for col in self.tmp_df.columns]
        if not all(columns_validated):
            wrong_columns = [col for col, b in zip(self.tmp_df.columns, columns_validated) if not b]
            raise Exception(f"Columns not exist in bids DataFrame: {wrong_columns}")
        if not all(types_validated):
            wrong_dtypes_columns = [(col, t) for col, t, b in zip(self.tmp_df.columns, self.tmp_df.dtypes, types_validated) if not b]
            raise Exception(f"Wrong types in bids DataFrame, please set these types: {wrong_dtypes_columns}")

    def add(self, price: float, user_id: int, unit=1.0, is_buying=True, time=0):
        new_row = pd.DataFrame(
            {
                "time": [time],
                "price": [price],
                "unit": [unit],
                "remaining_unit": [unit],
                "is_buying": [is_buying],
                "user": [user_id],
            },
        )
        if is_buying:
            self.buyers = pd.concat([self.buyers, new_row], ignore_index=True)
        else:
            self.sellers = pd.concat([self.sellers, new_row], ignore_index=True)

    def add_bids(self, bids_df: pd.DataFrame):
        self.validate_df(bids_df)
        #
        if "remaining_unit" not in bids_df.columns:
            bids_df["remaining_unit"] = bids_df["unit"]

        new_sellers = bids_df.loc[bids_df["is_buying"] == False]
        new_buyers = bids_df.loc[bids_df["is_buying"] == True]

        # Concatenate the filtered DataFrames if not empty
        sellers_df_list = [df for df in [self.sellers, new_sellers] if not df.empty]
        buyers_df_list = [df for df in [self.buyers, new_buyers] if not df.empty]
        if len(sellers_df_list) > 0:
            self.sellers = pd.concat(sellers_df_list, ignore_index=True)
        if len(buyers_df_list) > 0:
            self.buyers = pd.concat(buyers_df_list, ignore_index=True)

    def get_df(self):
        df_list = [df for df in [self.sellers, self.buyers] if not df.empty]
        if len(df_list) > 0:
            return pd.concat(df_list, ignore_index=True)
        else:
            # return an empty dataframe
            return pd.DataFrame(self.df_template)

    def get_breakeven_index(self):
        self.sort()
        m = min(len(self.buyers), len(self.sellers))
        for i in range(m):
            if self.buyers.iloc[i].price < self.sellers.iloc[i].price:
                return i
        return m

    def get_number_of_participants(self):
        return len(self.buyers) + len(self.sellers)

    def sort(self):
        self.sellers.sort_values(by=["price"], inplace=True, ignore_index=True)
        self.buyers.sort_values(
            by=["price"], ascending=False, inplace=True, ignore_index=True
        )

    def clone(self):
        sellers_copy = self.sellers.copy()
        buyers_copy = self.buyers.copy()
        bm_copy = BidsManager(buyers_copy, sellers_copy)
        return bm_copy

    def run(self, Mechanism_class, *args):
        bm_copy = self.clone()
        tm = Mechanism_class(bm_copy)
        tm.run(*args)
        return bm_copy, tm

    def plot_demand_curves(self):
        from pymarketng.application.Plot import plot_demand_curves

        plot_demand_curves(self)

    # TODO: slow
    # def get_maximum_aggregated_utility(self):
    #     result = maximum_aggregated_utility(self.get_df())[1]
    #     return float(result if result is not None else 0)

    # TODO: slow
    # def get_maximum_traded_volume(self):
    #     result = maximum_traded_volume(self.get_df())[1]
    #     return float(result if result is not None else 0)

    def get_stats(self):
        return {
            "breakeven": self.get_breakeven_index()
            # "maximum_aggregated_utility": self.get_maximum_aggregated_utility(),
            # "maximum_traded_volume": self.get_maximum_traded_volume(),
        }
