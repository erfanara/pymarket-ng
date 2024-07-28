from pymarketng.application.BidManager import BidManager
from pymarketng.application.Statistics import percentage_traded
from pymarketng.application.TransactionManager import TransactionManager
from pymarketng.domain.Bid import Bid
from pymarketng.domain.Transaction import Transaction

# import pandas as pd
# from typing import Type

class MC(type):
    def __repr__(self) -> str:
        return self.__name__

class Mechanism(TransactionManager, metaclass=MC):
    def __init__(self, bm: BidManager) -> None:
        super().__init__()
        bm.sort()
        self.bm = bm
        self.breakeven = bm.get_breakeven_index()
        # TODO: slow
        self.maximum_aggregated_utility = self.bm.get_maximum_aggregated_utility()
        self.maximum_traded_volume = self.bm.get_maximum_traded_volume()
        # updated on post-launch
        self.percentage_welfare = 0
        self.percentage_traded = 0

    def __repr__(self) -> str:
        return self.__class__.__name__

    # order match first k players
    # TODO: lambda for buy_price and sell_price
    def single_unit_order_match(self, k: int, buy_price: float, sell_price: float):
        for i in range(k):
            t = Transaction(
                buyyer_bid=self.bm.buyyers[i],
                seller_bid=self.bm.sellers[i],
                buy_price=buy_price,
                sell_price=sell_price,
            )
            self.add_transaction(t)

        # remove matching bids from bm TODO: prohibit direct access
        for _ in range(k):
            self.bm.buyyers.pop(0)
            self.bm.sellers.pop(0)

    def multi_unit_order_match(self, k: int, buy_price: float, sell_price: float):
        i = 0
        j = 0
        while i < k and j < k:
            q = min(
                self.bm.buyyers[i].remaining_quantity,
                self.bm.sellers[j].remaining_quantity,
            )
            t = Transaction(
                buyyer_bid=self.bm.buyyers[i],
                seller_bid=self.bm.sellers[j],
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=q,
            )
            self.add_transaction(t)

            if self.bm.buyyers[i].remaining_quantity == 0:
                i += 1
            if self.bm.sellers[j].remaining_quantity == 0:
                j += 1

        # remove bids with remaining_quantity==0 from bm TODO: prohibit direct access
        for _ in range(i):
            self.bm.buyyers.pop(0)
        for _ in range(j):
            self.bm.sellers.pop(0)

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
        try:
            self.percentage_welfare = (
                self.get_players_total_trade_profit() / self.maximum_aggregated_utility
            )
        except ZeroDivisionError:
            self.percentage_welfare = None

        try:
            self.percentage_traded = (
                self.get_players_total_trade_quantity() / self.maximum_traded_volume
            )
        except ZeroDivisionError:
            self.percentage_traded = None

    # should be implemented in child classes
    def launch(self, *args):
        pass

    # should be implemented in child classes
    def plot(self):
        pass

    def get_percentage_traded(self):
        return self.percentage_traded

    def get_percentage_welfare(self):
        return self.percentage_welfare

    def get_stats(self):
        return {
            "mechanism": self.__repr__(),
            **super().get_stats(),
            "maximum_aggregated_utility": self.maximum_aggregated_utility,
            "maximum_traded_volume": self.maximum_traded_volume,
            "percentage_traded": self.get_percentage_traded(),
            "percentage_welfare": self.get_percentage_welfare(),
        }


class Average_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven - 1].price
            + self.bm.buyyers[self.breakeven - 1].price
        ) / 2.0
        self.single_unit_order_match(self.breakeven, price, price)


class Average_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven - 1].price
            + self.bm.buyyers[self.breakeven - 1].price
        ) / 2.0
        self.multi_unit_order_match(self.breakeven, price, price)


class VCG_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        # TODO: Offset is okay for VCG mechanism?
        buy_price = max(
            self.bm.sellers[self.breakeven - 1].price,
            self.bm.buyyers[min(self.breakeven, len(self.bm.buyyers) - 1)].price,
        )
        sell_price = min(
            self.bm.buyyers[self.breakeven - 1].price,
            self.bm.sellers[min(self.breakeven, len(self.bm.sellers) - 1)].price,
        )
        self.single_unit_order_match(self.breakeven, buy_price, sell_price)


class VCG_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        # TODO: Offset is okay for VCG mechanism?
        buy_price = max(
            self.bm.sellers[self.breakeven - 1].price,
            self.bm.buyyers[min(self.breakeven, len(self.bm.buyyers) - 1)].price,
        )
        sell_price = min(
            self.bm.buyyers[self.breakeven - 1].price,
            self.bm.sellers[min(self.breakeven, len(self.bm.sellers) - 1)].price,
        )
        # TODO: idk why but sometimes when all of the buyers/sellers are in the breakeven, then buy_price > sell_price.
        # if buy_price > sell_price:
        #     print(self.breakeven, len(self.bm.buyyers), len(self.bm.sellers))
        #     print(
        #         self.bm.sellers[self.breakeven - 1].price,
        #         self.bm.buyyers[min(self.breakeven, len(self.bm.buyyers) - 1)].price,
        #         self.bm.buyyers[self.breakeven - 1].price,
        #         self.bm.sellers[min(self.breakeven, len(self.bm.sellers) - 1)].price,
        #     )
        #     tmp=buy_price
        #     buy_price=sell_price
        #     sell_price=tmp

        self.multi_unit_order_match(self.breakeven, buy_price, sell_price)


class TradeReduction_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        sell_price = self.bm.sellers[self.breakeven - 1].price
        buy_price = self.bm.buyyers[self.breakeven - 1].price
        self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class TradeReduction_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        sell_price = self.bm.sellers[self.breakeven - 1].price
        buy_price = self.bm.buyyers[self.breakeven - 1].price
        self.multi_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Macafee_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven + 1].price
            + self.bm.buyyers[self.breakeven + 1].price
        ) / 2.0
        if (
            self.bm.sellers[self.breakeven - 1].price
            <= price
            <= self.bm.buyyers[self.breakeven - 1].price
        ):
            # order match first k sellers and buyyers with price p
            self.single_unit_order_match(self.breakeven, price, price)
        else:
            # order match like trade reduction
            sell_price = self.bm.sellers[self.breakeven - 1].price
            buy_price = self.bm.buyyers[self.breakeven - 1].price
            self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Macafee_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        index = min(
            self.breakeven + 1, len(self.bm.sellers) - 1, len(self.bm.buyyers) - 1
        )
        price = (self.bm.sellers[index].price + self.bm.buyyers[index].price) / 2.0
        if (
            self.bm.sellers[self.breakeven - 1].price
            <= price
            <= self.bm.buyyers[self.breakeven - 1].price
        ):
            # order match first k sellers and buyyers with price p
            self.multi_unit_order_match(self.breakeven, price, price)
        else:
            # order match like trade reduction
            sell_price = self.bm.sellers[self.breakeven - 1].price
            buy_price = self.bm.buyyers[self.breakeven - 1].price
            self.multi_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Leftover_Clear(Mechanism):
    def launch(self, *args):
        base_buy_price = args[0]
        base_sell_price = args[1]
        base_buy_bid = Bid(price=base_buy_price, user_id=-1, quantity=-1, buying=True)
        base_sell_bid = Bid(
            price=base_sell_price, user_id=-1, quantity=-1, buying=False
        )

        for b in self.bm.buyyers:
            t = Transaction(
                buyyer_bid=b,
                seller_bid=base_sell_bid,
                buy_price=base_sell_price,
                sell_price=base_sell_price,
                quantity=b.quantity,
            )
            self.add_transaction(t)
        for s in self.bm.sellers:
            t = Transaction(
                buyyer_bid=base_buy_bid,
                seller_bid=s,
                buy_price=base_buy_price,
                sell_price=base_buy_price,
                quantity=s.quantity,
            )
            self.add_transaction(t)

        self.bm.buyyers.clear()
        self.bm.sellers.clear()
