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

        # update remaining_quantity
        self.buyyer_bid.remaining_quantity -= quantity
        self.seller_bid.remaining_quantity -= quantity

        self.buyer_profit_per_unit = buyyer_bid.price - buy_price
        self.seller_profit_per_unit = sell_price - seller_bid.price
        self.buyer_total_profit = self.buyer_profit_per_unit * quantity
        self.seller_total_profit = self.seller_profit_per_unit * quantity
        self.buyyer_bid.user.profit_per_unit += self.buyer_profit_per_unit
        self.seller_bid.user.profit_per_unit += self.seller_profit_per_unit
        self.buyyer_bid.user.total_profit += self.buyer_total_profit
        self.seller_bid.user.total_profit += self.seller_total_profit

        self.buyyer_bid.user.transactions.append(self)
        self.seller_bid.user.transactions.append(self)

    def as_dict(self):
        return {
            "mechanism": {
                "buy_price": self.buy_price,
                "sell_price": self.sell_price,
                "quantity": self.quantity,
            },
            "buyer": {
                "id": self.buyyer_bid.user,
                "price": self.buyyer_bid.price,
                "quantity": self.buyyer_bid.quantity,
                "remaining_quantity": self.buyyer_bid.remaining_quantity,
            },
            "seller": {
                "id": self.seller_bid.user,
                "price": self.seller_bid.price,
                "quantity": self.seller_bid.quantity,
                "remaining_quantity": self.seller_bid.remaining_quantity,
            },
            # "active": self.active,
        }

    def __repr__(self) -> str:
        return f"({self.buyyer_bid.user.id}, {self.buy_price})<({self.quantity})>({self.seller_bid.user.id}, {self.sell_price})"
