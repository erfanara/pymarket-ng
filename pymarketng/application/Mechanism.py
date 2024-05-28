from pymarketng.application.BidManager import BidManager
from pymarketng.application.TransactionManager import TransactionManager
from pymarketng.domain.Transaction import Transaction

# import pandas as pd
# from typing import Type


# TODO delete bids that no need for them
class Mechanism(TransactionManager):
    def __init__(self, bm: BidManager) -> None:
        super().__init__()
        bm.sort()
        self.bm = bm
        self.breakeven = bm.get_breakeven_index()

    # order match first k players
    # TODO: lambda for buy_price and sell_price
    def single_unit_order_match(self, k, buy_price, sell_price):
        for i in range(k):
            t = Transaction(
                buyyer_bid=self.bm.buyyers[i],
                seller_bid=self.bm.sellers[i],
                buy_price=buy_price,
                sell_price=sell_price,
            )
            self.add_transaction(t)

    def launch(self):
        pass

    def plot(self):
        pass

    def stat(self):
        pass


class Average_Mechanism(Mechanism):
    def launch(self):
        price = (
            self.bm.sellers[self.breakeven] + self.bm.buyyers[self.breakeven]
        ) / 2.0
        self.single_unit_order_match(self.breakeven, price, price)


class VCG_Mechanism(Mechanism):
    # TODO: auctioneer stats
    def launch(self):
        # FIX: MAX or MIN?
        buy_price = max(
            self.bm.sellers[self.breakeven].price, self.bm.buyyers[self.breakeven + 1].price
        )
        sell_price = max(
            self.bm.buyyers[self.breakeven].price, self.bm.sellers[self.breakeven + 1].price
        )
        self.single_unit_order_match(self.breakeven, buy_price, sell_price)


class TradeReduction_mechanism(Mechanism):
    def launch(self):
        sell_price = self.bm.sellers[self.breakeven].price
        buy_price = self.bm.buyyers[self.breakeven].price
        self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Macafee_mechanism(Mechanism):
    def launch(self):
        price = (
            self.bm.sellers[self.breakeven + 1] + self.bm.buyyers[self.breakeven + 1]
        ) / 2.0
        if self.bm.sellers[self.breakeven].price <= price <= self.bm.buyyers[self.breakeven].price:
            # order match first k sellers and buyyers with price p
            self.single_unit_order_match(self.breakeven, price, price)
        else:
            # order match like trade reduction
            sell_price = self.bm.sellers[self.breakeven]
            buy_price = self.bm.buyyers[self.breakeven]
            self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)
