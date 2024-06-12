from pymarketng.application.BidManager import BidManager
from pymarketng.application.TransactionManager import TransactionManager
from pymarketng.domain.Bid import Bid
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

        # remove matching bids from bm TODO: prohibit direct access
        for _ in range(k):
            self.bm.buyyers.pop(0)
            self.bm.sellers.pop(0)

    def multi_unit_order_match(self, k, buy_price, sell_price):
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

            # update remaining_quantity
            self.bm.sellers[j].remaining_quantity -= q
            self.bm.buyyers[i].remaining_quantity -= q

            if self.bm.buyyers[i].remaining_quantity == 0:
                i += 1
            if self.bm.sellers[j].remaining_quantity == 0:
                j += 1

        # remove bids with remaining_quantity==0 from bm TODO: prohibit direct access
        for _ in range(i):
            self.bm.buyyers.pop(0)
        for _ in range(j):
            self.bm.sellers.pop(0)

    # should be implemented in child classes
    def launch(self, *args):
        pass

    # should be implemented in child classes
    def plot(self):
        pass

    # should be implemented in child classes
    def stat(self):
        pass


class Average_Mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven - 1] + self.bm.buyyers[self.breakeven - 1]
        ) / 2.0
        self.single_unit_order_match(self.breakeven, price, price)


class Average_Mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven - 1] + self.bm.buyyers[self.breakeven - 1]
        ) / 2.0
        self.multi_unit_order_match(self.breakeven, price, price)


class VCG_Mechanism(Mechanism):
    # TODO: auctioneer stats
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        # FIX: MAX or MIN?
        buy_price = max(
            self.bm.sellers[self.breakeven - 1].price,
            self.bm.buyyers[self.breakeven].price,
        )
        sell_price = max(
            self.bm.buyyers[self.breakeven - 1].price,
            self.bm.sellers[self.breakeven].price,
        )
        self.single_unit_order_match(self.breakeven, buy_price, sell_price)


class VCG_Mechanism_Multi(Mechanism):
    # TODO: auctioneer stats
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        # FIX: MAX or MIN?
        buy_price = max(
            self.bm.sellers[self.breakeven - 1].price,
            self.bm.buyyers[self.breakeven].price,
        )
        sell_price = max(
            self.bm.buyyers[self.breakeven - 1].price,
            self.bm.sellers[self.breakeven].price,
        )
        self.multi_unit_order_match(self.breakeven, buy_price, sell_price)


class TradeReduction_mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        sell_price = self.bm.sellers[self.breakeven - 1].price
        buy_price = self.bm.buyyers[self.breakeven - 1].price
        self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class TradeReduction_mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        sell_price = self.bm.sellers[self.breakeven - 1].price
        buy_price = self.bm.buyyers[self.breakeven - 1].price
        self.multi_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Macafee_mechanism(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven + 1] + self.bm.buyyers[self.breakeven + 1]
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
            sell_price = self.bm.sellers[self.breakeven - 1]
            buy_price = self.bm.buyyers[self.breakeven - 1]
            self.single_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Macafee_mechanism_Multi(Mechanism):
    def launch(self, *args):
        if self.bm.get_breakeven_index() == 0:
            return

        price = (
            self.bm.sellers[self.breakeven + 1] + self.bm.buyyers[self.breakeven + 1]
        ) / 2.0
        if (
            self.bm.sellers[self.breakeven - 1].price
            <= price
            <= self.bm.buyyers[self.breakeven - 1].price
        ):
            # order match first k sellers and buyyers with price p
            self.multi_unit_order_match(self.breakeven, price, price)
        else:
            # order match like trade reduction
            sell_price = self.bm.sellers[self.breakeven - 1]
            buy_price = self.bm.buyyers[self.breakeven - 1]
            self.multi_unit_order_match(self.breakeven - 1, buy_price, sell_price)


class Leftover_Clear(Mechanism):
    def launch(self, *args):
        print(args)
        base_buy_price = args[0]
        base_sell_price = args[1]
        base_buy_bid = Bid(price=base_buy_price, user_id=-1, quantity=-1, buying=True)
        base_sell_bid = Bid(price=base_sell_price, user_id=-1, quantity=-1, buying=False)

        for b in self.bm.buyyers:
            t = Transaction(
                buyyer_bid=b,
                seller_bid=base_sell_bid,
                buy_price=base_sell_price,
                sell_price=base_sell_price,
                quantity=b.quantity,
            )
            print(b)
            self.add_transaction(t)
        for s in self.bm.sellers:
            t = Transaction(
                buyyer_bid=base_buy_bid,
                seller_bid=s,
                buy_price=base_buy_bid,
                sell_price=base_buy_bid,
                quantity=s.quantity,
            )
            print(s)
            self.add_transaction(t)
        
        self.bm.buyyers.clear()
        self.bm.sellers.clear()