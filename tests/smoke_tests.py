""" smoke tests """

from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.Market import Market, bid_selector_1h, mechanism_selctor_avg
from tests.utils.Datasets import generate_rounds_simple

import pandas as pd

def test_Market():
    """ simple test for Market class """

    buyers, sellers = generate_rounds_simple(10000)
    df = pd.merge(buyers, sellers)

    m = Market(mechanism_selector=mechanism_selctor_avg, all_bids=df, bids_selector=bid_selector_1h)
    m.run()