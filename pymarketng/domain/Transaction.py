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
            "mechanism":{
                "buy_price": self.buy_price,
                "sell_price": self.sell_price,
                "quantity": self.quantity
            },
            "buyer": {
                "id": self.buyyer_bid.user,
                "price" : self.buyyer_bid.price,
                "quantity": self.buyyer_bid.quantity,
                "remaining_quantity": self.buyyer_bid.remaining_quantity
            },
            "seller": {
                "id": self.seller_bid.user,
                "price" : self.seller_bid.price,
                "quantity": self.seller_bid.quantity,
                "remaining_quantity": self.seller_bid.remaining_quantity
            },
            # "active": self.active,
        }
