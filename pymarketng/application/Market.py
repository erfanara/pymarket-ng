import inspect
from typing import Callable, Generator, List, Type

from pymarketng.application.BidManager import BidManager
from pymarketng.application.Mechanism import Average_Mechanism_Multi, Mechanism
from pymarketng.application.TransactionManager import TransactionManager
from pymarketng.domain.Bid import Bid

import pandas as pd
import numpy as np


def check_typing(a: Callable, b: Callable):
    a_sign = inspect.signature(a)
    b_sign = inspect.signature(b)
    return a_sign == b_sign


class Market:
    def __init__(
        self,
        mechanism_selector: Callable,
        bids_selector: Callable,
        all_bids,
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
        self.bm_list: List[BidManager] = []
        self.tm_list: List[TransactionManager] = []
        # Create a BidManager for the first round
        self.bm_list.append(BidManager())

    # generator: no return needed
    @staticmethod
    def mechanism_selctor_template(
        bm_list: List[BidManager], tm_list: List[TransactionManager], *args, **kwargs
    ) -> Generator[type[Mechanism], None, None]:
        yield Mechanism

    @staticmethod
    def bids_selctor_template(all_bids, *args, **kwargs) -> Generator[List[Bid], None, None]:
        yield []

    def run(self):        
        current_bm = self.bm_list[-1]
        bids_iterator = self.bids_selector(self.all_bids, *self.args, **self.kwargs)
        mechanism_iterator = self.mechanism_selector(self.bm_list, self.tm_list, *self.args, **self.kwargs)
        for bids in bids_iterator:
            # print(bids)
            # for each round, first add the bids, and then run the mechanism
            current_bm.add_bid(*bids)
            bm_new, tm = current_bm.run(next(mechanism_iterator))
            print(tm.get_df())

            self.bm_list.append(bm_new)
            self.tm_list.append(tm)
            current_bm = bm_new


def mechanism_selctor_avg(
    bm_list: List[BidManager], tm_list: List[TransactionManager], *args, **kwargs
) -> Generator[Type[Mechanism], None, None]:
    while True:
        yield Average_Mechanism_Multi


# TODO: this type of function is not suitable for our work, i guess iterator is what we need
# TODO: it's not obvious that all_bids is a List[Bid] or Dataframe
def bid_selector_1h(all_bids, *args, **kwargs) -> Generator[List[Bid], None, None]:
    df = pd.DataFrame(all_bids)
    df["time"] = pd.to_datetime(df["time"])

    # loop through each unique date
    for date in np.sort(df["time"].dt.date.unique()):
        # filter the dataframe for the current date
        date_df = df[df["time"].dt.date == date]
        # loop through each hour
        for hour in np.sort(date_df["time"].dt.hour.unique()):
            # filter the dataframe for the current hour
            hourly_df = date_df[(date_df["time"].dt.hour == hour)]

            # TODO: why converting df to Bids? 
            # (There is a bug in entire project that we convert
            #  data to Bids and then Dataframes consequently and
            #  there is no such a law to obeoy in entire project)
            bids = []
            for i, row in hourly_df.iterrows():
                bids.append(
                    Bid(
                        user_id=row["user"],
                        price=row["price"],
                        quantity=row["quantity"],
                        buying=not row["buying"],
                        time=row["time"],
                    )
                )
            yield bids
