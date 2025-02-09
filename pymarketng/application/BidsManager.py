from typing import Any, Tuple, Type
import pandas as pd
# import fireducks.pandas as pd

# from pymarketng.application.Statistics import (
#     maximum_aggregated_utility,
#     maximum_traded_volume,
# )
# from pymarketng.application.Mechanism import Mechanism
from pymarketng.application.TransactionManager import TransactionManager
from pymarketng.application.UserManager import UserManager
# from pymarketng.domain.Bid import Bid


# TODO: adding time
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
        types_validated = [
            bids_df[col].dtype == self.tmp_df[col].dtype for col in self.tmp_df.columns
        ]
        if not all(columns_validated):
            wrong_columns = [
                col for col, b in zip(self.tmp_df.columns, columns_validated) if not b
            ]
            raise Exception(f"Columns not exist in bids DataFrame: {wrong_columns}")
        if not all(types_validated):
            wrong_dtypes_columns = [
                (col, t)
                for col, t, b in zip(
                    self.tmp_df.columns, self.tmp_df.dtypes, types_validated
                )
                if not b
            ]
            raise Exception(
                f"Wrong types in bids DataFrame, please set these types: {wrong_dtypes_columns}"
            )

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

    def get_breakeven_single(self) -> int:
        """Returns breakeven index for single-unit double auctions"""
        self.sort()
        m = min(len(self.buyers), len(self.sellers))

        # Use vectorized comparison to find the breakeven index
        buyer_prices = self.buyers.iloc[:m].price
        seller_prices = self.sellers.iloc[:m].price

        if len(buyer_prices) > 0 and len(seller_prices) > 0:
            # Find the first index where buyer price is less than seller price
            breakeven_index = (buyer_prices < seller_prices).idxmax()
            return (
                breakeven_index
                if buyer_prices[breakeven_index] < seller_prices[breakeven_index]
                else m
            )
        else:
            return m

    def get_breakeven_multi(self) -> (int, int):
        """Returns breakeven index for multi-unit double auctions.
        This function returns an two different index for each buyers and sellers.
        """
        self.sort()
        i = 0
        j = 0
        while i < len(self.buyers) and j < len(self.sellers):
            buyer = self.buyers.iloc[i]
            seller = self.sellers.iloc[j]

            # breakeven
            if buyer.price < seller.price:
                break

            q = min(
                buyer.remaining_unit,
                seller.remaining_unit,
            )

            if self.buyers.at[i, "remaining_unit"] - q == 0:
                i += 1
            if self.sellers.at[j, "remaining_unit"] - q == 0:
                j += 1

        if i == len(self.buyers) and j < len(self.sellers):
            j += 1
        if j == len(self.sellers) and i < len(self.buyers):
            i += 1
        return (i, j)

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

    def run(self, mechanism_classes, *args) -> ('BidsManager', TransactionManager):
        # TODO: TransactionManager mechanism name
        tm = TransactionManager(repr(mechanism_classes[0]))
        bm_copy = self.clone()
        for m_class in mechanism_classes:
            m = m_class(bm_copy)
            m.run(*args)

            tm.add_transactions_from_mechanism(m)
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
            "breakeven": self.get_breakeven_single()
            # "maximum_aggregated_utility": self.get_maximum_aggregated_utility(),
            # "maximum_traded_volume": self.get_maximum_traded_volume(),
        }
