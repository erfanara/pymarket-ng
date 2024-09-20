from pymarketng.application.Market import Market, bid_selector_1h, mechanism_selctor_avg, mechanism_selector_auctionner_profit
from pymarketng.application.Mechanism import *
from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.Plot import plot_demand_curves, plot_trades_as_graph

from pymarketng.application.Statistics import maximum_aggregated_utility
from pymarketng.domain import User
from pymarketng.domain.Bid import Bid
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import inspect
from typing import Callable, List, Type

# 1 Round of auction dataframe
n = 100
sellers = {
    "user": np.random.randint(1, 21, n),
    "type": np.random.randint(1, 4, n),
    # "unit": np.random.randint(1, 100, n),
    "unit": 100.0,
    "price": np.random.uniform(0, 200, n),
    # "is_buying": np.random.choice([True, False], n) ,
    "is_buying": False ,
    "time": np.datetime64('2022-01-01T00:00:00', 'ns'),
    # "time": sorted([
    #     datetime.datetime(
    #         2022,
    #         np.random.randint(1, 13),
    #         np.random.randint(1, 28),
    #         np.random.randint(0, 24),
    #         np.random.randint(0, 60),
    #         np.random.randint(0, 60),
    #     )
    #     for _ in range(n)
    # ]),
}
buyers = {
    "user": np.random.randint(1, 21, n),
    "type": np.random.randint(1, 4, n),
    # "unit": np.random.randint(1, 100, n),
    "unit": 100.0,
    "price": np.random.uniform(200, 300, n),
    # "is_buying": np.random.choice([True, False], n) ,
    "is_buying": True,
    "time": np.datetime64('2022-01-01T00:00:00', 'ns'),
    # "time": sorted([
    #     datetime.datetime(
    #         2022,
    #         np.random.randint(1, 13),
    #         np.random.randint(1, 28),
    #         np.random.randint(0, 24),
    #         np.random.randint(0, 60),
    #         np.random.randint(0, 60),
    #     )
    #     for _ in range(n)
    # ]),
}

buyers = pd.DataFrame(buyers)
sellers = pd.DataFrame(sellers)

bm = BidsManager()
bm.add_bids(buyers)
bm.add_bids(sellers)

# # create bids from df
# for index, row in df.iterrows():
#     bm.add_bid(Bid(row["price"],row["user"],row["unit"],row["is_buying"],row["time"]))

# bm.add_bid(Bid(178.0, 20, 84))
# bm.add_bid(Bid(128.0, 20, 54, False))
# bm.add_bid(Bid(132.0, 7, 13))
# bm.add_bid(Bid(56.0, 7, 51))


"""
BUG: VCG percentage welfare 102%

  user  buying  price  unit  remaining_unit                time  divisible
0    6    True    192        42                  42 2022-01-10 22:12:18       True
1   12    True    183        28                  28 2022-05-15 23:50:47       True
2   16    True    171        99                  99 2022-06-09 05:03:11       True
3   13    True     55        15                  15 2022-08-16 09:58:06       True
4   18    True    142        39                  39 2022-11-23 05:20:40       True
5    9   False     76        28                  28 2022-05-04 06:17:34       True
6   11   False    139         7                   7 2022-06-03 21:49:55       True
7   17   False    105        88                  88 2022-06-05 21:18:07       True
8    2   False     17        52                  52 2022-09-01 12:15:36       True
9    1   False    197        25                  25 2022-10-17 10:29:51       True 
"""
# bm.add(192,6,42)
# bm.add(183,12,28)
# bm.add(171,16,99)
# bm.add(55,13,15)
# bm.add(142,18,39)
# bm.add(76,9,28,False)
# bm.add(139,11,7,False)
# bm.add(105,17,88,False)
# bm.add(17,2,52,False)
# bm.add(197,1,25,False)
# # print(bm.get_df())

bm.sort()
print(bm.buyers)
print(bm.sellers)
print(bm.get_breakeven_index())


bm_new, tm = bm.run(VCG_Mechanism_Multi)
print(tm.get_df()[["mechanism.buy_price", "mechanism.sell_price", "mechanism.unit", "buyer.price", "seller.price", "buyer.id", "seller.id"]])
print(bm_new.get_df())
print(tm.get_stats())

# mechanisms = [VCG_Mechanism_Multi, Average_Mechanism_Multi, TradeReduction_Mechanism_Multi, Macafee_Mechanism_Multi]

# for m in mechanisms:
#     bm_new ,tm = bm.run(m)
#     print(tm.get_stats())





# print("Bids users")
# for b in bm.buyers:
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

# ----
# m=Market(mechanism_selector_auctionner_profit, bid_selector_1h, bm.get_df(), 0.7)
# m.run(100,100)

# print("------ bm stats:")
# print(m.get_BMs_stats())

# print("------ tm stats:")
# print(m.get_TMs_stats())
# df = m.get_TMs_stats()[["mechanism","auctioneer_profit" ,"percentage_traded" ,"percentage_welfare"]]
# print(df.to_string())

# for bm in m.bm_list:
#     if len(bm.buyers) > 0 and len(bm.sellers) >0:
#         bm.plot_demand_curves()

# vcg test
# new_bm , tm = bm.run(VCG_Mechanism_Multi)
# print(new_bm.get_df())
# print(tm.get_df()[["mechanism.buy_price", "mechanism.sell_price", "mechanism.unit", "buyer.price", "seller.price", "buyer.id", "seller.id"]])
# print(tm.get_auctioneer_profit())
# print(bm.get_df_buyers()[:bm.get_breakeven_index()])
# print(bm.get_df_sellers()[:bm.get_breakeven_index()])