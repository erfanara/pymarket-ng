from pymarketng.application.BidsManager import BidsManager

# from pymarketng.application.TransactionManager import TransactionManager
from pymarketng.domain.User import User

# from pymarketng.domain.Bid import Bid
from pymarketng.domain.Transaction import Transaction

import pandas as pd
# import fireducks.pandas as pd
import numpy as np
# from typing import Type
import line_profiler


class MC(type):
    def __repr__(cls) -> str:
        return cls.__name__


class Mechanism(metaclass=MC):
    def __init__(self, bm: BidsManager, time=0) -> None:
        bm.sort()
        self.bm = bm
        self.trans = []
        self.breakeven = bm.get_breakeven_single()
        # TODO: slow
        # self.maximum_aggregated_utility = self.bm.get_maximum_aggregated_utility()
        # self.maximum_traded_volume = self.bm.get_maximum_traded_volume()
        # updated on post-launch
        # self.percentage_welfare = 0
        # self.percentage_traded = 0

    def __repr__(self) -> str:
        return self.__class__.__name__

    # order match first k players
    # TODO: feature req: lambda for buy_price and sell_price
    def single_unit_order_match(self, k: int, buy_price: float, sell_price: float):
        for i in range(k):
            t = Transaction(
                buyer_bid=self.bm.buyers.iloc[i],
                seller_bid=self.bm.sellers.iloc[i],
                buy_price=buy_price,
                sell_price=sell_price,
                mechanism_name=repr(self),
            )
            self.trans.append(t)

        # remove matching bids from bm
        for _ in range(k):
            self.bm.buyers.pop(0)
            self.bm.sellers.pop(0)

    @line_profiler.profile
    def multi_unit_order_match(
        self, buyers_k: int, sellers_k: int, buy_price: float, sell_price: float
    ):
        i = 0
        j = 0
        buyers_to_drop = []
        sellers_to_drop = []
        while i < buyers_k and j < sellers_k:
            buyer = self.bm.buyers.iloc[i]
            seller = self.bm.sellers.iloc[j]

            q = min(
                buyer.remaining_unit,
                seller.remaining_unit,
            )
            t = Transaction(
                buyer_bid=buyer,
                seller_bid=seller,
                buy_price=buy_price,
                sell_price=sell_price,
                unit=q,
                mechanism_name=repr(self),
            )
            self.trans.append(t)

            # update remaining_unit
            self.bm.buyers.at[i, "remaining_unit"] -= q
            self.bm.sellers.at[j, "remaining_unit"] -= q

            if self.bm.buyers.at[i, "remaining_unit"] == 0:
                buyers_to_drop.append(i)
                i += 1
            if self.bm.sellers.at[j, "remaining_unit"] == 0:
                sellers_to_drop.append(j)
                j += 1

        self.bm.buyers.drop(index=buyers_to_drop, inplace=True)
        self.bm.sellers.drop(index=sellers_to_drop, inplace=True)

        self.bm.sellers.reset_index(drop=True, inplace=True)
        self.bm.buyers.reset_index(drop=True, inplace=True)

    def update_users_participation_num(self):
        for u in self.bm.um.users:
            u.num_of_participations += 1

    def run(self, *args):
        self.pre_launch(*args)
        self.launch(*args)
        self.post_launch(*args)

    def pre_launch(self, *args):
        self.update_users_participation_num()

    def post_launch(self, *args):
        pass
        # self.update_users_transactions_num()
        # try:
        #     self.percentage_welfare = (
        #         self.get_players_total_trade_profit() / self.maximum_aggregated_utility
        #     )
        # except ZeroDivisionError:
        #     self.percentage_welfare = None

        # try:
        #     self.percentage_traded = (
        #         self.get_players_total_trade_unit() / self.maximum_traded_volume
        #     )
        # except ZeroDivisionError:
        #     self.percentage_traded = None

    # should be implemented in child classes
    def launch(self, *args):
        pass

    # should be implemented in child classes
    def plot(self):
        pass

    # def get_percentage_traded(self):
    #     return self.percentage_traded

    # def get_percentage_welfare(self):
    #     return self.percentage_welfare

    def get_stats(self):
        return {
            "mechanism": repr(self),
            # **super().get_stats(),
            # "maximum_aggregated_utility": self.maximum_aggregated_utility,
            # "maximum_traded_volume": self.maximum_traded_volume,
            # "percentage_traded": self.get_percentage_traded(),
            # "percentage_welfare": self.get_percentage_welfare(),
        }

    def get_transactions(self):
        return self.trans

    def get_name(self):
        return repr(self)


class Average_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_single() == 0:
            return

        price = (
            self.bm.sellers.iloc[self.breakeven - 1].price
            + self.bm.buyers.iloc[self.breakeven - 1].price
        ) / 2.0
        self.single_unit_order_match(self.breakeven, price, price)


class Average_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        i, j = self.bm.get_breakeven_multi()
        if i == 0 or j == 0:
            return

        price = (
            self.bm.buyers.iloc[i - 1].price + self.bm.sellers.iloc[j - 1].price
        ) / 2.0
        self.multi_unit_order_match(i, j, price, price)


class VCG_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_single() == 0:
            return

        buy_price = max(
            self.bm.sellers.iloc[self.breakeven - 1].price,
            self.bm.buyers.iloc[min(self.breakeven, len(self.bm.buyers) - 1)].price,
        )
        sell_price = min(
            self.bm.buyers.iloc[self.breakeven - 1].price,
            self.bm.sellers.iloc[min(self.breakeven, len(self.bm.sellers) - 1)].price,
        )
        self.single_unit_order_match(self.breakeven, buy_price, sell_price)


class VCG_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        i, j = self.bm.get_breakeven_multi()
        if i == 0 or j == 0:
            return

        # buy_price = max(
        #     self.bm.sellers.iloc[j - 1].price,
        #     self.bm.buyers.iloc[min(i, len(self.bm.buyers) - 1)].price,
        # )
        # sell_price = min(
        #     self.bm.buyers.iloc[i - 1].price,
        #     self.bm.sellers.iloc[min(j, len(self.bm.sellers) - 1)].price,
        # )
        buy_price = self.bm.sellers.iloc[j - 1].price
        sell_price = self.bm.buyers.iloc[i - 1].price

        self.multi_unit_order_match(i, j, buy_price, sell_price)


class TradeReduction_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_single() == 0:
            return

        buy_price = self.bm.buyers.iloc[self.breakeven - 1].price
        sell_price = self.bm.sellers.iloc[self.breakeven - 1].price
        self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class TradeReduction_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        i, j = self.bm.get_breakeven_multi()
        if i == 0 or j == 0:
            return

        buy_price = self.bm.buyers.iloc[i - 1].price
        sell_price = self.bm.sellers.iloc[j - 1].price
        self.multi_unit_order_match(i - 1, j - 1, buy_price, sell_price)


# TODO: rename needed
class Macafee_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_single() == 0:
            return

        price = (
            self.bm.sellers.iloc[self.breakeven + 1].price
            + self.bm.buyers.iloc[self.breakeven + 1].price
        ) / 2.0
        if (
            self.bm.sellers.iloc[self.breakeven - 1].price
            <= price
            <= self.bm.buyers.iloc[self.breakeven - 1].price
        ):
            # order match first k sellers and buyers with price p
            self.single_unit_order_match(self.breakeven, price, price)
        else:
            # order match like trade reduction
            sell_price = self.bm.sellers.iloc[self.breakeven - 1].price
            buy_price = self.bm.buyers.iloc[self.breakeven - 1].price
            self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Macafee_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        i, j = self.bm.get_breakeven_multi()
        if i == 0 or j == 0:
            return

        i_index = min(i + 1, len(self.bm.buyers) - 1)
        j_index = min(j + 1, len(self.bm.sellers) - 1)
        price = (
            self.bm.buyers.iloc[i_index].price + self.bm.sellers.iloc[j_index].price
        ) / 2.0
        if (
            self.bm.sellers.iloc[self.breakeven - 1].price
            <= price
            <= self.bm.buyers.iloc[self.breakeven - 1].price
        ):
            # order match first k sellers and buyers with price p
            self.multi_unit_order_match(i, j, price, price)
        else:
            # order match like trade reduction
            buy_price = self.bm.buyers.iloc[i - 1].price
            sell_price = self.bm.sellers.iloc[j - 1].price
            self.multi_unit_order_match(i - 1, j - 1, buy_price, sell_price)


class Leftover_Clear(Mechanism):
    def launch(self, *args):
        base_buy_price = args[0]
        base_sell_price = args[1]
        base_buy_bid = pd.DataFrame(
            {
                "time": 0,
                "price": [base_buy_price],
                "user": [-1],
                "unit": [np.inf],
                "is_buying": [True],
                "remaining_unit": [np.inf],
            }
        ).iloc[0]
        base_sell_bid = pd.DataFrame(
            {
                "time": 0,
                "price": [base_sell_price],
                "user": [-1],
                "unit": [np.inf],
                "is_buying": [False],
                "remaining_unit": [np.inf],
            }
        ).iloc[0]

        for i, b in self.bm.buyers.iterrows():
            t = Transaction(
                buyer_bid=b,
                seller_bid=base_sell_bid,
                buy_price=base_sell_price,
                sell_price=base_sell_price,
                unit=b.remaining_unit,
                mechanism_name=repr(self),
            )
            self.trans.append(t)
        for i, s in self.bm.sellers.iterrows():
            t = Transaction(
                buyer_bid=base_buy_bid,
                seller_bid=s,
                buy_price=base_buy_price,
                sell_price=base_buy_price,
                unit=s.remaining_unit,
                mechanism_name=repr(self),
            )
            self.trans.append(t)

        # clear dataframes but keep columns
        self.bm.buyers = pd.DataFrame(columns=self.bm.buyers.columns)
        self.bm.sellers = pd.DataFrame(columns=self.bm.sellers.columns)

    # override
    def update_users_participation_num(self):
        pass
