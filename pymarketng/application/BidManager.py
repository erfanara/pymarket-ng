import pandas as pd


from pymarketng.domain.Bid import Bid


class BidManager:
    def __init__(self) -> None:
        self.buyyers = []
        self.sellers = []

    def add_bid(self, *bids: Bid):
        for b in bids:
            if b.price != 0 and b.quantity !=0:
                if b.buying:
                    self.buyyers.append(b)
                else:
                    self.sellers.append(b)

    def add_bids(self, bids: list[Bid]):
        for b in bids:
            if b.price != 0 and b.quantity !=0:
                if b.buying:
                    self.buyyers.append(b)
                else:
                    self.sellers.append(b)

    def get_df(self):
        return pd.DataFrame([b.as_dict() for b in self.buyyers + self.sellers])

    def get_df_buyyers(self):
        return pd.DataFrame([b.as_dict() for b in self.buyyers])
    
    def get_df_sellers(self):
        return pd.DataFrame([b.as_dict() for b in self.sellers])

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

    def run(self, Mechanism_class):
        m = Mechanism_class(self)
        m.launch()
        return m

    def plot(self):
        from pymarketng.application.Plot import plot_demand_curves
        plot_demand_curves(self)