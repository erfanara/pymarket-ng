import pandas as pd
import numpy as np
import pulp

from collections import OrderedDict

# welfare
# maximum traded vol
# maximum traded money
# auctioneer profit
# maximum_aggregated_utility
# profits


def maximum_aggregated_utility(bids, *args, reservation_prices=None):
    if reservation_prices is None:
        reservation_prices = OrderedDict()
    
    if len(bids) == 0:
        return pulp.LpStatusNotSolved, 0, {}

    model = pulp.LpProblem("Max_Aggregated_Utility", pulp.LpMaximize)
    buyers = bids.loc[bids["buying"]].index.values
    sellers = bids.loc[~bids["buying"]].index.values
    index = [(i, j) for i in buyers for j in sellers]

    for i, x in bids.iterrows():
        if i not in reservation_prices:
            reservation_prices[i] = x.price

    coeffs = OrderedDict()
    for x in index:
        coeffs[x] = reservation_prices[x[0]] - reservation_prices[x[1]]

    qs = pulp.LpVariable.dicts("q", index, lowBound=0, cat="Continuous")
    model += pulp.lpSum([qs[x[0], x[1]] * coeffs[x] for x in index])

    for b in buyers:
        model += pulp.lpSum(qs[b, j] for j in sellers) <= bids.iloc[b]['quantity']
    for s in sellers:
        model += pulp.lpSum(qs[i, s] for i in buyers) <= bids.iloc[s]['quantity']

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    status = pulp.LpStatus[model.status]
    objective = pulp.value(model.objective)
    variables = OrderedDict()
    sorted_keys = sorted(qs.keys())
    for var in sorted_keys:
        varval = qs[var].varValue
        variables[var] = varval

    return status, objective, variables



def maximum_traded_volume(bids, *args, reservation_prices=OrderedDict()):
    model = pulp.LpProblem("Max_Traded_Volume", pulp.LpMaximize)

    if len(bids) == 0:
        return pulp.LpStatusNotSolved, 0, {}

    buyers = bids.loc[bids["buying"]].index.values
    sellers = bids.loc[~bids["buying"]].index.values

    index = [
        (i, j) for i in buyers for j in sellers if bids.iloc[i, 1] >= bids.iloc[j, 1]
    ]

    qs = pulp.LpVariable.dicts("q", index, lowBound=0, cat="Continuous")

    model += pulp.lpSum([qs[x[0], x[1]] for x in index])

    for b in buyers:
        model += (
            pulp.lpSum(qs[b, j] for j in sellers if (b, j) in index) <= bids.iloc[b]['quantity']
        )

    for s in sellers:
        model += (
            pulp.lpSum(qs[i, s] for i in buyers if (i, s) in index) <= bids.iloc[s]['quantity']
        )

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    status = pulp.LpStatus[model.status]
    objective = pulp.value(model.objective)
    variables = OrderedDict()
    sorted_keys = sorted(qs.keys())
    for q in sorted_keys:
        v = qs[q].varValue
        variables[q] = v

    return status, objective, variables


def percentage_traded(bids, transactions, reservation_prices=OrderedDict(), **kwargs):
    _, objective, _ = maximum_traded_volume(bids)

    total_traded = transactions.quantity.sum() / 2

    if objective is not None:
        return total_traded / objective
    else:
        return None


def calculate_profits(bids, transactions, reservation_prices=None, fees=None, **kwargs):
    users = sorted(bids.user.unique())
    buyers = bids.loc[bids["buying"]].index.values
    sellers = bids.loc[~bids["buying"]].index.values

    if reservation_prices is None:
        reservation_prices = OrderedDict()
    for i, x in bids.iterrows():
        if i not in reservation_prices:
            reservation_prices[i] = x.price

    if fees is None:
        fees = np.zeros(bids.user.unique().shape[0])

    profit = OrderedDict()
    for case in ["bid", "reservation"]:
        tmp = bids.reset_index().rename(columns={"index": "bid"}).copy()
        tmp = tmp[["bid", "price", "buying", "user"]]
        if case == "reservation":
            tmp.price = tmp.apply(
                lambda x: reservation_prices.get(x.bid, x.price), axis=1
            )
        merged = transactions.merge(tmp, on="bid").copy()
        merged["gain"] = merged.apply(lambda x: get_gain(x), axis=1)
        profit_player = merged.groupby("user")["gain"].sum()
        # print(profit_player)
        profit_player = np.array([profit_player.get(x, 0) for x in users])
        profit["player_{}".format(case)] = profit_player.astype("float64")

        if case == "bid":
            # print(merged)
            mb = merged.loc[merged["buying"]]
            ms = merged.loc[~merged["buying"]]
            # print(ms)
            # print(ms.quantity.sum(), mb.quantity.sum())
            # print(ms.price_x * ms.quantity)
            profit_market = (mb.price_x * mb.quantity).values.sum()
            profit_market -= (ms.price_x * ms.quantity).values.sum()
            profit_market += fees.sum()
            profit["market"] = profit_market.astype("float64")

    return profit


def get_gain(row):
    gap = row.price_y - row.price_x
    if not row.buying:
        gap = -gap
    return gap * row.quantity
