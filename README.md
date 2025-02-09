

# PYMARKET-NG
pymarket-ng is a simulation framework designed for exploring and analyzing market double auction mechanisms. By providing a flexible and modular environment, this project enables users to simulate trading scenarios, study market dynamics, and conduct experiments on auction strategies. Whether you're a researcher, student, or enthusiast, pymarket-ng offers the tools to gain a deeper understanding of how double auctions operate in varied market conditions.

# Simple Usage

1. Install dependencies:

```
pip install -r ./requirements.txt
```

2. Create a python file and simulate your scenario

For ex. here is a scenario of running the Average Mechanism in a single round of auction.

```python
from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.Mechanism import Average_Mechanism_Multi

bm = BidsManager()
bm.add(price=1.0, user_id=0, unit=10.0, is_buying=True)
bm.add(price=1.0, user_id=1, unit=10.0, is_buying=True)
bm.add(price=1.0, user_id=2, unit=10.0, is_buying=False)
bm.add(price=1.0, user_id=3, unit=10.0, is_buying=False)
bm.add(price=1.0, user_id=4, unit=10.0, is_buying=False)
bm_new, tm = bm.run((Average_Mechanism_Multi,))

print(tm.get_total_traded_unit_p2p())
print(tm.get_players_total_trade_unit())
print(tm.get_stats())
```

# TODO
- write a comperehensive doc

# Acknowledgements
- https://github.com/kiedanski/pymarket, By studying their well-structured and thoughtful code, I was able to gain valuable insights that helped me significantly improve the design and implementation of pymarket-ng. 