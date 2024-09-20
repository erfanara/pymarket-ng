# import matplotlib
# matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from collections import OrderedDict

from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.TransactionManager import TransactionManager


def demand_curve(bm: BidsManager):
    bm.sort()
    buying = bm.get_df_buyers()
    buying["acum"] = buying.unit.cumsum()
    demand_curve = buying[["acum", "price"]].values
    demand_curve = np.vstack([demand_curve, [np.inf, 0]])
    index = buying.index.values.astype("int64")
    return demand_curve, index


def supply_curve(bm: BidsManager):
    bm.sort()
    selling = bm.get_df_sellers()
    selling["acum"] = selling.unit.cumsum()
    supply_curve = selling[["acum", "price"]].values
    supply_curve = np.vstack([supply_curve, [np.inf, np.inf]])
    index = selling.index.values.astype("int64")
    return supply_curve, index


# def get_value_stepwise(x, f):
#     """
#     Returns the value of a stepwise constant
#     function defined by the right extrems
#     of its interval
#     Functions are assumed to be defined
#     in (0, inf).

#     Parameters
#     ----------
#     x: float
#         Value in which the function is to be
#         evaluated
#     f: np.ndarray
#         Stepwise function represented as a 2 column
#         matrix. Each row is the rightmost extreme
#         point of each constant interval. The first column
#         contains the x coordinate and is sorted increasingly.
#         f is assumed to be defined only in the interval
#         :math: (0, \infty)
#     Returns
#     --------
#     float or None
#         The image of x under f: `f(x)`. If `x` is negative,
#         then None is returned instead. If x is outside
#         the range of the function (greater than `f[-1, 0]`),
#         then the method returns None.

#     Examples
#     ---------
#     >>> f = np.array([
#     ...     [1, 1],
#     ...     [3, 4]])
#     >>> [pm.get_value_stepwise(x, f)
#     ...     for x in [-1, 0, 0.5, 1, 2, 3, 4]]
#     [None, 1, 1, 1, 4, 4, None]

#     """
#     if x < 0:
#         return None

#     for step in f:
#         if x <= step[0]:
#             return step[1]


# def intersect_stepwise(
#         f,
#         g,
#         k=0.5
#     ):
#     """
#     Finds the intersection of
#     two stepwise constants functions
#     where f is assumed to be bigger at 0
#     than g.
#     If no intersection is found, None is returned.

#     Parameters
#     ----------
#     f: np.ndarray
#         Stepwise constant function represented as
#         a 2 column matrix where each row is the rightmost
#         point of the constat interval. The first column
#         is sorted increasingly.
#         Preconditions: f is non-increasing.

#     g: np.ndarray
#         Stepwise constant function represented as
#         a 2 column matrix where each row is the rightmost
#         point of the constat interval. The first column
#         is sorted increasingly.
#         Preconditions: g is non-decreasing and
#         `f[0, 0] > g[0, 0]`
#     k : float
#         If the intersection is empty or an interval,
#         a convex combination of the y-values of f and g
#         will be returned and k will be used to determine
#         hte final value. `k=1` will be the value of g
#         while `k=0` will be the value of f.

#     Returns
#     --------
#     x_ast : float or None
#         Axis coordinate of the intersection of both
#         functions. If the intersection is empty,
#         then it returns None.
#     f_ast : int or None
#         Index of the rightmost extreme
#         of the interval of `f` involved in the
#         intersection. If the intersection is
#         empty, returns None
#     g_ast : int or None
#         Index of the rightmost extreme
#         of the interval of `g` involved in the
#         intersection. If the intersection is
#         empty, returns None.
#     v : float or None
#         Ordinate of the intersection if it
#         is uniquely identified, otherwise
#         the k-convex combination of the
#         y values of `f` and `g` in the last
#         point when they were both defined.

#     Examples
#     ---------
#     Simple intersection with diferent domains

#     >>> f = np.array([[1, 3], [3, 1]])
#     >>> g = np.array([[2,2]])
#     >>> pm.intersect_stepwise(f, g)
#     (1, 0, 0, 2)

#     Empty intersection, returning the middle value

#     >>> f = np.array([[1,3], [2, 2.5]])
#     >>> g = np.array([[1,1], [2, 2]])
#     >>> pm.intersect_stepwise(f, g)
#     (None, None, None, 2.25)
#     """
#     x_max = np.min([f.max(axis=0)[0], g.max(axis=0)[0]])
#     xs = sorted([x for x in set(g[:, 0]).union(set(f[:, 0])) if x <= x_max])
#     fext = [get_value_stepwise(x, f) for x in xs]
#     gext = [get_value_stepwise(x, g) for x in xs]
#     x_ast = None
#     for i in range(len(xs) - 1):
#         if (fext[i] > gext[i]) and (fext[i + 1] < gext[i + 1]):
#             x_ast = xs[i]

#     f_ast = np.argmax(f[:, 0] >= x_ast) if x_ast is not None else None
#     g_ast = np.argmax(g[:, 0] >= x_ast) if x_ast is not None else None

#     g_val = g[g_ast, 1] if g_ast is not None else get_value_stepwise(xs[-1], g)
#     f_val = f[f_ast, 1] if f_ast is not None else get_value_stepwise(xs[-1], f)

#     intersect_domain_both = x_ast in f[:, 0] and x_ast in g[:, 0]
#     if not (intersect_domain_both) and (x_ast is not None):
#         v = g_val if x_ast in f[:, 0] else f_val
#     else:
#         v = g_val * k + (1 - k) * f_val

#     return x_ast, f_ast, g_ast, v


# BUG: if all of bids are buy or sell this won't work
def plot_demand_curves(bm: BidsManager, ax=None, margin_X=1.2, margin_Y=1.2):
    if ax is None:
        fig, ax = plt.subplots()

    extra_X = 3
    extra_Y = 1

    dc = demand_curve(bm)[0]
    sp = supply_curve(bm)[0]

    x_dc = dc[:, 0]
    x_dc = np.concatenate([[0], x_dc])
    x_sp = np.concatenate([[0], sp[:, 0]])

    y_sp = sp[:, 1]
    y_dc = dc[:, 1]
    max_x = max(x_dc[-2], x_sp[-2])
    extra_X = max_x * margin_X

    x_dc[-1] = extra_X
    y_dc = np.concatenate([y_dc, [0]])
    max_point = y_dc.max() * margin_Y

    x_sp[-1] = extra_X
    y_sp[-1] = max_point
    y_sp = np.concatenate([y_sp, [y_sp[-1]]])

    ax.step(x_dc, y_dc, where="post", c="r", label="Demand")
    ax.step(x_sp, y_sp, where="post", c="b", label="Supply")
    ax.set_xlabel('unit')
    ax.set_ylabel("Price")
    ax.legend()
    plt.show()


def plot_trades_as_graph(bm: BidsManager, tm: TransactionManager, ax=None):
    buyers = bm.get_df_buyers()
    bids = bm.get_df()
    tmp = tm.get_df()
    tmp["user_1"] = tmp.seller_bid.map(bids.user)
    tmp["user_2"] = tmp.source.map(bids.user)
    tmp["is_buying"] = tmp.buyer_bid.map(buyers)

    G = nx.from_pandas_edgelist(tmp, "user_1", "user_2")

    edge_labels = OrderedDict()
    duplicated_labels = tmp.set_index(["user_1", "user_2"])['unit'].to_dict()
    for (x, y), v in duplicated_labels.items():
        if (x, y) not in edge_labels and (y, x) not in edge_labels:
            edge_labels[(x, y)] = v

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    pos = nx.bipartite_layout(G, buyers, align="horizontal", scale=3)
    _ = nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color="k", node_size=500)
    _ = nx.draw_networkx_labels(G, pos=pos, ax=ax, font_color="w")
    _ = nx.draw_networkx_edges(G, pos=pos, label=G, ax=ax)
    _ = nx.draw_networkx_edge_labels(
        G, pos=pos, edge_labels=edge_labels, label_pos=0.9, ax=ax
    )
    _ = ax.axis("off")

    return ax

# # TODO: move to library
# import seaborn as sns
# import matplotlib.pyplot as plt

# fig, axes = plt.subplots(2, 1, figsize=(20, 20))

# # Create a box plot for 'Price' for 'Seller' for each 'time'
# sns.boxplot(x='time', y='price', data=sellers_df.reset_index(drop=True), ax=axes[0], flierprops=dict(markerfacecolor='r', marker='s'))
# axes[0].set_title('Box plot of Price for Sellers over Time')
# axes[0].set_xlabel('Time')
# axes[0].set_ylabel('Price')
# axes[0].tick_params(axis='x', rotation=90)  # Rotate x-axis labels for better visibility

# # Create a box plot for 'Price' for 'Buyer' for each 'time'
# sns.boxplot(x='time', y='price', data=buyers_df.reset_index(drop=True), ax=axes[1], flierprops=dict(markerfacecolor='r', marker='s'))
# axes[1].set_title('Box plot of Price for Buyers over Time')
# axes[1].set_xlabel('Time')
# axes[1].set_ylabel('Price')
# axes[1].tick_params(axis='x', rotation=90)  # Rotate x-axis labels for better visibility

# plt.tight_layout()
# plt.show()

# TODO: i guess we need to remove the outlirers and then we are able to calculate the mean. 

# # TODO: move to library
# import seaborn as sns
# import matplotlib.pyplot as plt

# fig, axes = plt.subplots(2, 1, figsize=(20, 20))

# # Create a box plot for 'unit' for 'Seller' for each 'time'
# sns.boxplot(x='time', y='unit', data=sellers_df.reset_index(drop=True), ax=axes[0], flierprops=dict(markerfacecolor='r', marker='s'))
# axes[0].set_title('Box plot of unit for Sellers over Time')
# axes[0].set_xlabel('Time')
# axes[0].set_ylabel('unit')
# axes[0].tick_params(axis='x', rotation=90)  # Rotate x-axis labels for better visibility

# # Create a box plot for 'unit' for 'Buyer' for each 'time'
# sns.boxplot(x='time', y='unit', data=buyers_df.reset_index(drop=True), ax=axes[1], flierprops=dict(markerfacecolor='r', marker='s'))
# axes[1].set_title('Box plot of unit for Buyers over Time')
# axes[1].set_xlabel('Time')
# axes[1].set_ylabel('unit')
# axes[1].tick_params(axis='x', rotation=90)  # Rotate x-axis labels for better visibility

# plt.tight_layout()
# plt.show()


# # TODO: move to library

# sns.set_style("whitegrid")

# # Create the plot
# plt.figure(figsize=(20, 6))
# buyers_bids_count = buyers_df.groupby('time').size().reset_index(name='count')
# sellers_bids_count = sellers_df.groupby('time').size().reset_index(name='count')
# all_bids_count = df.groupby('time').size().reset_index(name='count')
# sns.lineplot(data=buyers_bids_count, x='time', y='count', marker='o', label='buy bids')
# sns.lineplot(data=sellers_bids_count, x='time', y='count', marker='o', label='sell bids')
# sns.lineplot(data=all_bids_count, x='time', y='count', marker='o', label='all bids')

# # Add titles and labels
# plt.title('Count of bids over time')
# plt.xlabel('Time')
# plt.ylabel('Count')
# plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
# plt.legend()
# plt.tight_layout()  # Adjust layout to make room for rotated labels

# # Show the plot
# plt.show()

# numerical_columns = ['is_peak', 'load', 'generate','SOC','is_seller', 'price', 'unit']
# plt.figure(figsize=(12, 8))
# plt.suptitle('Heatmap', fontsize=16)
# sns.heatmap(df[numerical_columns].corr(), annot=True, cmap='coolwarm')
# plt.show()