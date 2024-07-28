from pymarketng.application.Market import Market, bid_selector_1h, mechanism_selctor_avg, mechanism_selector_auctionner_profit
from pymarketng.application.Mechanism import *
from pymarketng.application.BidManager import BidManager
from pymarketng.application.Plot import plot_demand_curves, plot_trades_as_graph

from pymarketng.domain.Bid import Bid
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import inspect
from typing import Callable, List, Type

# 1 Round of auction dataframe
n = 10
data = {
    "user": np.random.randint(1, 21, n),
    "type": np.random.randint(1, 4, n),
    "unit": np.random.randint(1, 100, n),
    "price": np.random.randint(0, 200, n),
    "buying": np.random.choice([True, False], n) ,
    "time": sorted([
        datetime.datetime(
            2022,
            np.random.randint(1, 13),
            np.random.randint(1, 28),
            np.random.randint(0, 24),
            np.random.randint(0, 60),
            np.random.randint(0, 60),
        )
        for _ in range(n)
    ]),
}
df = pd.DataFrame(data)

bm = BidManager()

# create bids from df
for index, row in df.iterrows():
    bm.add_bid(Bid(row["price"],row["user"],row["unit"],row["buying"],row["time"]))

# bm.add_bid(Bid(178.0, 20, 84))
# bm.add_bid(Bid(128.0, 20, 54, False))
# bm.add_bid(Bid(132.0, 7, 13))
# bm.add_bid(Bid(56.0, 7, 51))

print(bm.get_df())
# print("Bids users")
# for b in bm.buyyers:
#     print("b", b.user)
# for s in bm.sellers:
#     print("s", s.user)

# print("after add_bids bm")
# for k,v in bm.um.users.items():
#     print(v)

# # print(bm.get_df())
# bm_new,tm=bm.run(Average_Mechanism_Multi)

# print("after mechanism bm_new")
# for k,v in bm_new.um.users.items():
#     print(v)
# # print(bm.um.get_df())
# # print(bm_new.um.get_df())

# # tm.get_df()
# # bm_new.get_df()
# # bm_new.um.get_df()

# TODO: what is this bm.get_df() thing here ?! There is no need for such a thing
m=Market(mechanism_selector_auctionner_profit, bid_selector_1h, bm.get_df(), 0.7)
m.run()

print("------ bm stats:")
print(m.get_BMs_stats())

print("------ tm stats:")
# print(m.get_TMs_stats())
df = m.get_TMs_stats()[["mechanism","auctioneer_profit" ,"percentage_traded" ,"percentage_welfare"]]
print(df.to_string())

# for bm in m.bm_list:
#     if len(bm.buyyers) > 0 and len(bm.sellers) >0:
#         bm.plot_demand_curves()

# vcg test
# new_bm , tm = bm.run(VCG_Mechanism_Multi)
# print(new_bm.get_df())
# print(tm.get_df()[["mechanism.buy_price", "mechanism.sell_price", "mechanism.quantity", "buyer.price", "seller.price", "buyer.id", "seller.id"]])
# print(tm.get_auctioneer_profit())
# print(bm.get_df_buyyers()[:bm.get_breakeven_index()])
# print(bm.get_df_sellers()[:bm.get_breakeven_index()])