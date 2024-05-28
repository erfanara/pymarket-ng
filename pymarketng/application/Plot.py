# import matplotlib
# matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from collections import OrderedDict

from pymarketng.application.Mechanism import BidManager
from pymarketng.application.TransactionManager import TransactionManager


def demand_curve(bm:BidManager):
    bm.sort()
    buying = bm.get_df_buyyers()
    buying['acum'] = buying.quantity.cumsum()
    demand_curve = buying[['acum', 'price']].values
    demand_curve = np.vstack([demand_curve, [np.inf, 0]])
    index = buying.index.values.astype('int64')
    return demand_curve, index


def supply_curve(bm:BidManager):
    bm.sort()
    selling = bm.get_df_sellers()
    selling['acum'] = selling.quantity.cumsum()
    supply_curve = selling[['acum', 'price']].values
    supply_curve = np.vstack([supply_curve, [np.inf, np.inf]])
    index = selling.index.values.astype('int64')
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

def plot_demand_curves(bm:BidManager, ax=None, margin_X=1.2, margin_Y=1.2):
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

    ax.step(x_dc, y_dc, where='post', c='r', label='Demand')
    ax.step(x_sp, y_sp, where='post', c='b', label='Supply')
    ax.set_xlabel('Quantity')
    ax.set_ylabel('Price')
    ax.legend()
    plt.show()

def plot_trades_as_graph(
        bm:BidManager,
        tm:TransactionManager,
        ax=None):
    buyers=bm.get_df_buyyers()
    bids = bm.get_df()
    tmp = tm.get_df()
    tmp['user_1'] = tmp.seller_bid.map(bids.user)
    tmp['user_2'] = tmp.source.map(bids.user)
    tmp['buying'] = tmp.buyyer_bid.map(buyers)

    G = nx.from_pandas_edgelist(tmp, 'user_1', 'user_2')

    edge_labels = OrderedDict()
    duplicated_labels = tmp.set_index(
        ['user_1', 'user_2'])['quantity'].to_dict()
    for (x, y), v in duplicated_labels.items():
        if ((x, y) not in edge_labels and (y, x) not in edge_labels):
            edge_labels[(x, y)] = v

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    pos = nx.bipartite_layout(G, buyers, align='horizontal', scale=3)
    _ = nx.draw_networkx_nodes(
        G,
        pos=pos,
        ax=ax,
        node_color='k',
        node_size=500)
    _ = nx.draw_networkx_labels(G, pos=pos, ax=ax, font_color='w')
    _ = nx.draw_networkx_edges(G, pos=pos, label=G, ax=ax)
    _ = nx.draw_networkx_edge_labels(
        G,
        pos=pos,
        edge_labels=edge_labels,
        label_pos=0.9,
        ax=ax)
    _ = ax.axis('off')

    return ax
