""" smoke tests """

from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.Market import Market, bid_selector_1h, MechanismSelectorStatic, Average_Mechanism_Multi
from tests.utils.Datasets import generate_rounds_simple

import pandas as pd
# import fireducks.pandas as pd

def test_Market():
    """ simple test for Market class """

    buyers, sellers = generate_rounds_simple(100)
    df = pd.merge(buyers, sellers)

    m = Market(MechanismSelectorStatic, bid_selector_1h, df, Average_Mechanism_Multi)
    m.run()