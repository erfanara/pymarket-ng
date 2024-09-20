from pymarketng.domain.User import User


class Transaction:
    def __init__(
        self, buyer_bid, seller_bid, buy_price:float, sell_price:float, mechanism_name='', unit=1.0, active=False
    ) -> None:
        self.buyer_bid = buyer_bid
        self.seller_bid = seller_bid
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.unit = unit
        self.active = active
        self.mechanism_name = mechanism_name
        if self.buyer_bid.time != 0:
            self.time = self.buyer_bid.time
        else:
            self.time = self.seller_bid.time


        # # update remaining_unit (TODO: moved to Mechanism.py)
        # self.buyer_bid.remaining_unit -= unit
        # self.seller_bid.remaining_unit -= unit

        self.buyer_profit_per_unit = buyer_bid.price - buy_price
        self.seller_profit_per_unit = sell_price - seller_bid.price
        self.buyer_total_profit = self.buyer_profit_per_unit * unit
        self.seller_total_profit = self.seller_profit_per_unit * unit

        # TODO: tidy needed
        self.buyer_total_trade_p2p = 0.0
        self.buyer_total_trade_infra = 0.0
        self.buyer_total_profit_p2p = 0.0
        self.buyer_total_profit_infra = 0.0
        self.seller_total_trade_p2p = 0.0
        self.seller_total_trade_infra = 0.0
        self.seller_total_profit_p2p = 0.0
        self.seller_total_profit_infra = 0.0
        if self.mechanism_name != 'Leftover_Clear':
            self.buyer_total_trade_p2p = buy_price * unit
            self.seller_total_trade_p2p = sell_price * unit
            self.buyer_total_profit_p2p = self.buyer_total_profit
            self.seller_total_profit_p2p = self.seller_total_profit
        else:
            self.buyer_total_trade_infra = buy_price * unit
            self.seller_total_trade_infra = sell_price * unit
            self.buyer_total_profit_infra = self.buyer_total_profit
            self.seller_total_profit_infra = self.seller_total_profit

        buyer = User(self.buyer_bid.user)
        seller = User(self.seller_bid.user)
        self.buyer = buyer
        self.seller = seller
        buyer.profit_per_unit += self.buyer_profit_per_unit
        seller.profit_per_unit += self.seller_profit_per_unit
        buyer.total_profit += self.buyer_total_profit
        seller.total_profit += self.seller_total_profit

        buyer.total_trade_p2p += self.buyer_total_trade_p2p
        buyer.total_trade_infra += self.buyer_total_trade_infra
        buyer.total_profit_p2p += self.buyer_total_profit_p2p
        buyer.total_profit_infra += self.buyer_total_profit_infra
        buyer.total_trade = buyer.total_trade_p2p + buyer.total_trade_infra
        buyer.total_profit_net = buyer.total_profit_p2p - buyer.total_profit_infra

        seller.total_trade_p2p += self.seller_total_trade_p2p
        seller.total_trade_infra += self.seller_total_trade_infra
        seller.total_profit_p2p += self.seller_total_profit_p2p
        seller.total_profit_infra += self.seller_total_profit_infra
        seller.total_trade = seller.total_trade_p2p + seller.total_trade_infra
        seller.total_profit_net = seller.total_profit_p2p - seller.total_profit_infra

        buyer.transactions.append(self)
        seller.transactions.append(self)

    def as_dict(self):
        return {
            "time": self.time,
            "mechanism": {
                "buy_price": self.buy_price,
                "sell_price": self.sell_price,
                'unit': self.unit,
                'name': self.mechanism_name,
            },
            "buyer": {
                "id": self.buyer_bid.user,
                "price": self.buyer_bid.price,
                'unit': self.buyer_bid.unit,
                "remaining_unit": self.buyer_bid.remaining_unit,
            },
            "seller": {
                "id": self.seller_bid.user,
                "price": self.seller_bid.price,
                'unit': self.seller_bid.unit,
                "remaining_unit": self.seller_bid.remaining_unit,
            },
            # "active": self.active,
        }

    def __repr__(self) -> str:
        return f"({User(self.buyer_bid.user).id}, {self.buy_price})<({self.unit})>({User(self.seller_bid.user).id}, {self.sell_price})"
