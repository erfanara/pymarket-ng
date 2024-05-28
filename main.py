from pymarketng.application.Mechanism import Average_Mechanism, BidManager, Macafee_mechanism, TradeReduction_mechanism, VCG_Mechanism
from pymarketng.application.Plot import plot_demand_curves
from pymarketng.domain.Bid import Bid

import numpy as np


bm = BidManager()

bm.add_bid(Bid(10.0, 0))
bm.add_bid(Bid(20.0, 1))
bm.add_bid(Bid(30.0, 2))
bm.add_bid(Bid(40.0, 3))
bm.add_bid(Bid(50.0, 4))
bm.add_bid(Bid(51.0, 5))
bm.add_bid(Bid(52.0, 6))
bm.add_bid(Bid(53.0, 7))
bm.add_bid(Bid(54.0, 8))
bm.add_bid(Bid(55.0, 9))
bm.add_bid(Bid(56.0, 10))
bm.add_bid(Bid(57.0, 11))
bm.add_bid(Bid(58.0, 12))
bm.add_bid(Bid(59.0, 13))
bm.add_bid(Bid(60.0, 14))
bm.add_bid(Bid(41.0, 15, buying=False))
bm.add_bid(Bid(42.0, 16, buying=False))
bm.add_bid(Bid(43.0, 17, buying=False))
bm.add_bid(Bid(43.0, 18, buying=False))
bm.add_bid(Bid(44.0, 19, buying=False))
bm.add_bid(Bid(45.0, 20, buying=False))
bm.add_bid(Bid(51.0, 21, buying=False))
bm.add_bid(Bid(52.0, 22, buying=False))
bm.add_bid(Bid(53.0, 23, buying=False))
bm.add_bid(Bid(58.0, 24, buying=False))
bm.add_bid(Bid(59.0, 25, buying=False))
bm.add_bid(Bid(72.0, 26, buying=False))
bm.add_bid(Bid(75.0, 27, buying=False))
bm.add_bid(Bid(79.0, 28, buying=False))
bm.add_bid(Bid(81.0, 29, buying=False))
bm.add_bid(Bid(84.0, 30, buying=False))


print(bm.get_breakeven_index())

m=bm.run(Average_Mechanism)
print(m.get_df())

m=bm.run(VCG_Mechanism)
print(m.get_df())

m=bm.run(TradeReduction_mechanism)
print(m.get_df())

m=bm.run(Macafee_mechanism)
print(m.get_df())

plot_demand_curves(bm)
