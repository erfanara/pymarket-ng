from typing import List
import pandas as pd
import numpy as np

from pymarketng.domain.Transaction import Transaction
from pymarketng.domain.User import User


class TransactionManager:
    def __init__(self, time=0) -> None:
        self.trans: List[Transaction] = []
        self.time = time

    def add(self, *args):
        t = Transaction(*args)
        self.add_transaction(t)

    def add_transaction(self, *transactions: Transaction):
        self.trans.extend(transactions)

    def get_df(self):
        return pd.json_normalize([t.as_dict() for t in self.trans])

    def get_players_total_trade_profit(self):
        # TODO: is this correct?
        return sum(
            [
                t.buyer_total_trade_p2p
                + t.seller_total_trade_p2p
                + t.buyer_total_trade_infra
                + t.seller_total_trade_infra
                for t in self.trans
            ]
        )

    def get_players_total_trade_unit(self):
        return sum([t.unit for t in self.trans])

    def get_auctioneer_profit(self):
        return sum([t.unit * (t.buy_price - t.sell_price) for t in self.trans])

    def get_average_score_of_users(self):
        scores = [t.buyer.score for t in self.trans]
        scores.extend([t.seller.score for t in self.trans])
        return np.mean(scores) if len(scores) > 0 else 0
    
    def get_score_of_user(self, id):
        return User(id).score

    def get_stats(self):
        return {
            "players_total_trade_profit": self.get_players_total_trade_profit(),
            "players_total_trade_unit": self.get_players_total_trade_unit(),
            "auctioneer_profit": self.get_auctioneer_profit(),
            "number_of_transactions": len(self.trans),
            "average_score_of_users": self.get_average_score_of_users(),
            "time": self.time,
        }
        # TODO: k, i think we need more ...
        # TODO: what mechanism yields the maximum_aggregated_utility without any condition.
