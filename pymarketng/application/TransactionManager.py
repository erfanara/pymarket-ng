from typing import List
import pandas as pd
# import fireducks.pandas as pd
import numpy as np

from pymarketng.domain.Transaction import Transaction
from pymarketng.domain.User import User
# from pymarketng.application.Mechanism import Mechanism


class TransactionManager:
    """
    indicates the result of auction round.
    """

    def __init__(self, mechanism_name, time=0) -> None:
        self.mechanism_name = mechanism_name
        self.trans: List[Transaction] = []
        self.time = time

    def add_transactions_from_mechanism(self, mech):
        self.add_transactions(mech.get_transactions())

    def add_transactions(self, transactions: List[Transaction]):
        self.trans.extend(transactions)

    def add(self, *args):
        t = Transaction(*args)
        self.add_transactions([t])

    # def update_users_transactions_num(self):
    #     for t in self.trans:
    #         buyer = User(t.buyer_bid.user)
    #         seller = User(t.seller_bid.user)
    #         buyer.num_of_transactions_taken_via_p2p += 1
    #         seller.num_of_transactions_taken_via_p2p += 1

    # override (lefover clear)
    # def update_users_transactions_num(self):
    #     for t in self.trans:
    #         buyer = User(t.buyer_bid.user)
    #         seller = User(t.seller_bid.user)
    #         buyer.num_of_transactions_taken_via_infra += 1
    #         seller.num_of_transactions_taken_via_infra += 1

    def get_df(self):
        return pd.json_normalize([t.as_dict() for t in self.trans])

    def get_players_total_trade_profit(self):
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

    # TODO: add to stats (quest: can this be automated? yes, using decorators)
    def get_total_traded_unit_p2p(self):
        return sum([t.unit for t in self.trans if t.mechanism_name != "Leftover_Clear"])

    def get_auctioneer_profit(self):
        return sum([t.unit * (t.buy_price - t.sell_price) for t in self.trans])

    def get_average_score_of_users(self):
        scores = [t.buyer.score for t in self.trans]
        scores.extend([t.seller.score for t in self.trans])
        return np.mean(scores) if len(scores) > 0 else 0

    def get_score_of_user(self, id):
        return User(id).score

    def get_players_profit_p2p_vs_infra(self, p_G, p_feat):
        sum = 0
        for t in self.trans:
            if t.seller_bid.user != -1 and t.buyer_bid.user != -1:
                # p2p transaction
                sum += t.unit * ((p_G - t.buy_price) + (t.sell_price - p_feat))
            else:
                # infra transaction
                pass
        return sum

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
