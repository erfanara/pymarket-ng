class Transaction:
    def __init__(
        self, buyyer_bid, seller_bid, buy_price, sell_price, quantity=1.0, active=False
    ) -> None:
        self.buyyer_bid = buyyer_bid
        self.seller_bid = seller_bid
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.quantity = quantity
        self.active = active

    def as_dict(self):
        return {
            "buyyer_bid": self.buyyer_bid,
            "seller_bid": self.seller_bid,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            # "active": self.active,
        }
