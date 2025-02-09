import inspect
import random
import os
from typing import Callable, Generator, List, Type, Tuple
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

# import fireducks.pandas as pd
import seaborn as sns

from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.Mechanism import (
    Average_Mechanism_Multi,
    Leftover_Clear,
    Macafee_Mechanism_Multi,
    Mechanism,
    TradeReduction_Mechanism_Multi,
    VCG_Mechanism_Multi,
)
from pymarketng.application.TransactionManager import TransactionManager


def is_typing_equal(a: Callable, b: Callable):
    a_sign = inspect.signature(a)
    b_sign = inspect.signature(b)
    return a_sign == b_sign


class MechanismSelector(ABC):
    """
    An abstract class that describes how to create a Mechanism selector.
    To select a mechanism for each round, we have a select() function.
    """

    def __init__(
        self,
        bm_list: List[BidsManager],
        tm_list: List[TransactionManager],
        *args,
        **kwargs,
    ):
        self.bm_list = bm_list
        self.tm_list = tm_list
        self.args = args
        self.kwargs = kwargs

    # features
    parallel_run = False

    @abstractmethod
    def select(self) -> Generator[Tuple[Type[Mechanism], ...], None, None]:
        """
        This function is a generator that can be used as iterator,
        Functionality: It should yield a Mechanism for each iteration.

        This function is useful for users to implement their logic of
        Mechanism selction over multiple rounds whithin the market.
        """
        yield (Mechanism,)


class Market:
    def __init__(
        self,
        mechanism_selector: Type[MechanismSelector],
        bids_selector: Callable,
        all_bids: pd.DataFrame,
        *args,
        **kwargs,
    ) -> None:
        is_typing_equal(bids_selector, Market.bids_selctor_template)
        self.args = args
        self.kwargs = kwargs
        self.all_bids = all_bids
        self.mechanism_selector = mechanism_selector
        self.bids_selector = bids_selector
        self.bm_list: List[BidsManager] = []
        self.tm_list: List[TransactionManager] = []
        # Create a BidManager for the first BidsManager
        self.bm_list.append(BidsManager())

    # @staticmethod
    # def mechanism_selctor_template(
    #     bm_list: List[BidsManager], tm_list: List[TransactionManager], *args, **kwargs
    # ) -> Generator[type[Mechanism], None, None]:
    #     yield Mechanism

    @staticmethod
    def bids_selctor_template(
        all_bids: pd.DataFrame, *args, **kwargs
    ) -> Generator[pd.DataFrame, None, None]:
        yield pd.DataFrame()

    def run_serial(self, *args):
        bids_iterator = self.bids_selector(self.all_bids, *self.args, **self.kwargs)

        mechanism_iterator = self.mechanism_selector(
            self.bm_list, self.tm_list, *self.args, **self.kwargs
        ).select()
        for i, bids_df in enumerate(bids_iterator):
            current_bm = self.bm_list[-1]

            # for each BidsManager, first add the bids, and then run the mechanism
            current_bm.add_bids(bids_df)
            new_bm, tm = current_bm.run(next(mechanism_iterator), *args)

            self.bm_list.append(new_bm)
            self.tm_list.append(tm)

    def run_parallel(self, *args):
        bids_iterator = self.bids_selector(self.all_bids, *self.args, **self.kwargs)

        mechanism_iterator = self.mechanism_selector(
            self.bm_list, self.tm_list, *self.args, **self.kwargs
        ).select()

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []
            for bids_df in bids_iterator:
                current_bm = self.bm_list[-1]

                # for each BidsManager, first add the bids, and then run the mechanism
                current_bm.add_bids(bids_df)
                mc = next(mechanism_iterator)
                futures.append(executor.submit(current_bm.run, mc, *args))

                # add a new BidManager for the next round
                self.bm_list.append(BidsManager())
            for i, future in enumerate(as_completed(futures)):
                print("done", i)
                _, tm = future.result()
                self.tm_list.append(tm)

    def run(self, *args):
        if self.mechanism_selector.parallel_run:
            self.run_parallel(*args)
        else:
            self.run_serial(*args)

    # TODO: get users total profit

    # each bm/tm have stats (return them at once)
    def get_BMs_stats(self):
        return pd.json_normalize([bm.get_stats() for bm in self.bm_list])

    def get_TMs_stats(self):
        return pd.json_normalize([tm.get_stats() for tm in self.tm_list])

    def get_total_traded_unit_p2p(self):
        return sum([tm.get_total_traded_unit_p2p() for tm in self.tm_list])

    def get_players_total_trade_unit(self):
        return sum([tm.get_players_total_trade_unit() for tm in self.tm_list])

    def get_players_profit_p2p_vs_infra(self, p_G, p_feat):
        return sum(
            [tm.get_players_profit_p2p_vs_infra(p_G, p_feat) for tm in self.tm_list]
        )

    def get_auctioneer_profit(self):
        return sum([tm.get_auctioneer_profit() for tm in self.tm_list])

    def get_num_of_p2p_transactions(self):
        return sum(
            [
                len([t for t in tm.trans if t.mechanism_name != "Leftover_Clear"])
                for tm in self.tm_list
            ]
        )

    def get_num_of_infra_transactions(self):
        return sum(
            [
                len([t for t in tm.trans if t.mechanism_name == "Leftover_Clear"])
                for tm in self.tm_list
            ]
        )

    def get_percentage_of_p2p_transactions(self):
        x = self.get_num_of_p2p_transactions()
        y = self.get_num_of_infra_transactions()
        return x / (x + y)

        # TODO: number of sellers/buyers in each BidsManager is not whithin stats
        # TODO: ploting
        # ploting (each BM/TM have it's plot methods)
        # ploting (stats from BMs/TMs)
        # count all of sellers and buyers
        # ploting (BM data as a whole)
        # boxplots
        # mean of price over time (sellers vs buyers)
        # heatmap
        # ploting (TM data as a whole)

        # guess we need another file to create new functions for anomaly detection
        # number of participants (threshold: alpha*previous_BidsManager_participants)
        # Compare each number of units with its average from start to current BidsManager_time
        # Normilizing
        # values_lists = [NormalizeData(sum_units_list), NormalizeData(sum_participant_list), NormalizeData(diff_units_list)]
        # num_diff_units = abs(1/(num_units_buyers - num_units_sellers))
        # decision theory
        # Equal weighting
        # direct ranking
        # swing weighting
        # things we need at the end
        # is vcg affordable


def bid_selector_1h(
    all_bids: pd.DataFrame, *args, **kwargs
) -> Generator[pd.DataFrame, None, None]:
    grouped = all_bids.groupby([all_bids["time"].dt.date, all_bids["time"].dt.hour])
    for (date, hour), group in grouped:
        yield group.copy()
        # yield pd.DataFrame(BidsManager.df_template)


class MechanismSelectorStatic(MechanismSelector):
    parallel_run = True

    def select(self) -> Generator[Tuple[Type[Mechanism], ...], None, None]:
        while True:
            yield (self.args[0], Leftover_Clear)


class MechanismSelectorRandom(MechanismSelector):
    parallel_run = True

    def select(self) -> Generator[Tuple[Type[Mechanism], ...], None, None]:
        while True:
            items = list(self.args[0].keys())
            weights = list(self.args[0].values())
            mc = random.choices(items, weights=weights, k=1)[0]
            print(mc)
            yield (mc, Leftover_Clear)
