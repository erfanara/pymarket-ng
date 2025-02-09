"""Module providing functions to create random datasets just for testing purposes"""

import numpy as np
import pandas as pd
# import fireducks.pandas as pd


def generate_one_round(
    number_of_buyers,
    number_of_buy_bids,
    mean_buy_unit,
    stdev_buy_unit,
    mean_buy_price,
    stdev_buy_price,
    number_of_sellers,
    number_of_sell_bids,
    mean_sell_unit,
    stdev_sell_unit,
    mean_sell_price,
    stdev_sell_price,
) -> (pd.DataFrame, pd.DataFrame):
    """
    generate random bids for a round
    note that no "time" is included within the generated dataframes
    """
    sellers = {
        "user": np.random.randint(1, number_of_sellers, number_of_sell_bids),
        "unit": np.random.normal(mean_sell_unit, stdev_sell_unit, number_of_sell_bids),
        "price": np.random.normal(
            mean_sell_price, stdev_sell_price, number_of_sell_bids
        ),
        "is_buying": False,
    }
    buyers = {
        "user": np.random.randint(1, number_of_buyers, number_of_buy_bids),
        "unit": np.random.normal(mean_buy_unit, stdev_buy_unit, number_of_buy_bids),
        "price": np.random.normal(mean_buy_price, stdev_buy_price, number_of_buy_bids),
        "is_buying": True,
    }

    buyers = pd.DataFrame(buyers)
    sellers = pd.DataFrame(sellers)
    return buyers, sellers


def generate_rounds_simple(number_of_rounds) -> (pd.DataFrame, pd.DataFrame):
    """
    Generates multiple rounds using `generate_round()` function to achive a simple random dataset,
    just for testing purposes. The input parameter for `generate_round()` is predefined whithin this function.
    """
    buyers_dfs = []
    sellers_dfs = []
    time = pd.to_datetime("2022-01-01 12:00:00")
    for _ in range(number_of_rounds):
        buyers, sellers = generate_one_round(
            number_of_buyers=100,
            number_of_buy_bids=100,
            mean_buy_unit=100,
            stdev_buy_unit=30,
            mean_buy_price=100,
            stdev_buy_price=30,
            number_of_sellers=100,
            number_of_sell_bids=100,
            mean_sell_unit=100,
            stdev_sell_unit=30,
            mean_sell_price=100,
            stdev_sell_price=30,
        )
        buyers["time"] = time
        sellers["time"] = time
        buyers_dfs.append(buyers)
        sellers_dfs.append(sellers)

        time += pd.Timedelta(hours=1)
    return pd.concat(buyers_dfs, ignore_index=True), pd.concat(
        sellers_dfs, ignore_index=True
    )


if __name__ == "__main__":
    b, s = generate_rounds_simple(100)
    print(b)
    print(s)
