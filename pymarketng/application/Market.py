import inspect
from typing import Callable, Generator, List, Type

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

import pandas as pd
import numpy as np
import seaborn as sns


def check_typing(a: Callable, b: Callable):
    a_sign = inspect.signature(a)
    b_sign = inspect.signature(b)
    return a_sign == b_sign

# TODO: what is the type of all_bids? it can be a list or maybe a dataframe, but for now we assume it's dataframe
class Market:
    def __init__(
        self,
        mechanism_selector: Callable,
        bids_selector: Callable,
        all_bids: pd.DataFrame,
        *args,
        **kwargs,
    ) -> None:
        check_typing(mechanism_selector, Market.mechanism_selctor_template)
        check_typing(bids_selector, Market.bids_selctor_template)
        self.args = args
        self.kwargs = kwargs
        self.all_bids = all_bids
        self.mechanism_selector = mechanism_selector
        self.bids_selector = bids_selector
        self.bm_list: List[BidsManager] = []
        self.tm_list: List[TransactionManager] = []
        # Create a BidManager for the first BidsManager
        self.bm_list.append(BidsManager())

    # generator: no return needed
    @staticmethod
    def mechanism_selctor_template(
        bm_list: List[BidsManager], tm_list: List[TransactionManager], *args, **kwargs
    ) -> Generator[type[Mechanism], None, None]:
        yield Mechanism

    @staticmethod
    def bids_selctor_template(
        all_bids: pd.DataFrame, *args, **kwargs
    ) -> Generator[pd.DataFrame, None, None]:
        yield pd.DataFrame()

    def run(self, *args):
        current_bm = self.bm_list[-1]
        bids_iterator = self.bids_selector(self.all_bids, *self.args, **self.kwargs)
        mechanism_iterator = self.mechanism_selector(
            self.bm_list, self.tm_list, *self.args, **self.kwargs
        )
        for bids_df in bids_iterator:
            # for each BidsManager, first add the bids, and then run the mechanism
            current_bm.add_bids(bids_df)
            bm_new, tm = current_bm.run(next(mechanism_iterator), *args)

            self.bm_list.append(bm_new)
            self.tm_list.append(tm)
            current_bm = bm_new

    
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
        """
def mechanism_selctor_equal(
    bm_list: List[BidManager], tm_list: List[TransactionManager]
) -> Type[Mechanism]:
    previous_auctioneer_profit=0.0
    if len(tm_list) != 0:
        previous_auctioneer_profit=tm_list[-2].get_auctioneer_profit()
    incoming_BidsManager_vcg_auctioneer_profit=bm_list[-1].run(VCG_Mechanism_Multi)[1].get_auctioneer_profit()

    print(previous_auctioneer_profit, incoming_BidsManager_vcg_auctioneer_profit)
    if equal_weightings(values_lists, weight_list, len(tm_list)-1):
        return TradeReduction_Mechanism_Multi
    else:
        if Is_Affordable(previous_auctioneer_profit,incoming_BidsManager_vcg_auctioneer_profit):
            return VCG_Mechanism_Multi
        else:
            return Average_Mechanism_Multi
        """


# TODO: score for every user (peak and non-peak)

def mechanism_selector_auctionner_profit(
    bm_list: List[BidsManager], tm_list: List[TransactionManager], *args, **kwargs
)-> Generator[Type[Mechanism], None, None]:
    # our options: vcg, tr, macafee
    # strategy: TODO ...
    beta = args[0]

    auctioneer_total_profit = 0 
    incoming_BidsManager_vcg_auctioneer_profit = 0
    while True:
        print("t ",auctioneer_total_profit, incoming_BidsManager_vcg_auctioneer_profit)
        # TODO: TRM never selected. if auctioneer is on loss, then launch `TradeReduction` for the remedy
        if auctioneer_total_profit < 0.0:
            yield TradeReduction_Mechanism_Multi
        else:
            # simulate running vcg on the next BidsManager
            incoming_BidsManager_vcg_auctioneer_profit = (
                bm_list[-1].run(VCG_Mechanism_Multi)[1].get_auctioneer_profit()
            )
            # print("v ", incoming_BidsManager_vcg_auctioneer_profit)
            if incoming_BidsManager_vcg_auctioneer_profit + auctioneer_total_profit > 0.0:
                yield VCG_Mechanism_Multi
            else:
                # default option: macafee
                yield Macafee_Mechanism_Multi
        auctioneer_total_profit += tm_list[-1].get_auctioneer_profit()
        yield Leftover_Clear

def mechanism_selctor_avg(
    bm_list: List[BidsManager], tm_list: List[TransactionManager], *args, **kwargs
) -> Generator[Type[Mechanism], None, None]:
    while True:
        yield Average_Mechanism_Multi


# TODO: why not using pandas queries?
def bid_selector_1h(all_bids: pd.DataFrame, *args, **kwargs) -> Generator[pd.DataFrame, None, None]:
    df = all_bids
    # df["time"] = pd.to_datetime(df["time"])

    # loop through each unique date
    for date in np.sort(df["time"].dt.date.unique()):
        # filter the dataframe for the current date
        date_times = df.loc[df["time"].dt.date == date, "time"]
        # loop through each hour
        for hour in np.sort(date_times.dt.hour.unique()):
            # filter the dataframe for the current hour
            hourly_df = df.loc[(df["time"].dt.date == date) & (df["time"].dt.hour == hour)]

            yield hourly_df.copy()
            # yield a empty dataframe TODO: needs more explanation on why
            yield pd.DataFrame(BidsManager.df_template)