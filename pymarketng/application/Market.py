import inspect
from typing import Callable, Generator, List, Type, Tuple
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
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
        for bids_df in bids_iterator:
            current_bm = self.bm_list[-1]

            # for each BidsManager, first add the bids, and then run the mechanism
            current_bm.add_bids(bids_df)
            results = current_bm.run(next(mechanism_iterator), *args)

            self.bm_list.extend([r[0] for r in results])
            self.tm_list.extend([r[1] for r in results])

    def run_parallel(self, *args):
        bids_iterator = self.bids_selector(self.all_bids, *self.args, **self.kwargs)

        mechanism_iterator = self.mechanism_selector(
            self.bm_list, self.tm_list, *self.args, **self.kwargs
        ).select()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {}
            for bids_df in bids_iterator:
                current_bm = self.bm_list[-1]

                # for each BidsManager, first add the bids, and then run the mechanism
                current_bm.add_bids(bids_df)
                mc = next(mechanism_iterator)
                futures[executor.submit(current_bm.run, mc, *args)] = (current_bm, mc)

                # add a new BidManager for the next round
                self.bm_list.append(BidsManager())
            for future in as_completed(futures):
                result = future.result()
                self.tm_list.extend([r[1] for r in result])

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
    grouped = all_bids.groupby([all_bids['time'].dt.date, all_bids['time'].dt.hour])
    for (date, hour), group in grouped:
        print(date, hour)
        yield group.copy()
        yield pd.DataFrame(BidsManager.df_template)