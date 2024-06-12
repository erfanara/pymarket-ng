import pandas as pd

from pymarketng.domain.Transaction import Transaction


class TransactionManager:
    def __init__(self) -> None:
        self.trans = []

    def add(self,*args):
        t=Transaction(*args)
        self.add_transaction(t)

    def add_transaction(self, *transactions: Transaction):
        self.trans.extend(transactions)

    def get_df(self):
        return pd.json_normalize([t.as_dict() for t in self.trans])

    def get_players_total_profit(self):
        return sum([t.quantity * ((t.buyyer_bid.price - t.buy_price)+(t.sell_price - t.seller_bid.price)) for t in self.trans])

    def get_players_total_quantity(self):
        return sum([t.quantity for t in self.trans])

    def get_auctineer_profit(self):
        return sum([t.quantity * (t.buy_price - t.sell_price) for t in self.trans])

    def stats(self):
        pass
