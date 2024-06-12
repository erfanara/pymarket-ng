from typing import List
import pandas as pd
import copy


from pymarketng.application.UserManager import UserManager
from pymarketng.domain.Bid import Bid

class BidManager:
    def __init__(self) -> None:
        self.buyyers: List[Bid] = []
        self.sellers: List[Bid] = []
        self.um = UserManager()

    def add(self, *args):
        b=Bid(*args)
        self.add_bid(b)

    def add_bid(self, *bids: Bid):
        for b in bids:
            if b.price != 0 and b.quantity !=0:
                if b.buying:
                    self.buyyers.append(b)
                    self.um.add_user(b.user)
                else:
                    self.sellers.append(b)
                    self.um.add_user(b.user)

    # TODO: cache this dataframe (performance issue)
    def get_df(self):
        return pd.json_normalize([b.as_dict() for b in self.buyyers + self.sellers])

    def get_df_buyyers(self):
        return pd.json_normalize([b.as_dict() for b in self.buyyers])
    
    def get_df_sellers(self):
        return pd.json_normalize([b.as_dict() for b in self.sellers])

    def get_breakeven_index(self):
        self.sort()
        m = min(len(self.buyyers), len(self.sellers))
        for i in range(m):
            if self.buyyers[i].price < self.sellers[i].price:
                return i
        return m

    def sort(self):
        self.buyyers.sort(reverse=True)
        self.sellers.sort()

    def run(self, Mechanism_class, *args):
        bm_copy = copy.deepcopy(self)
        tm = Mechanism_class(bm_copy)
        tm.run(*args)
        return bm_copy, tm

    def plot(self):
        from pymarketng.application.Plot import plot_demand_curves
        plot_demand_curves(self)