from pymarketng.domain.User import User


class Bid:
    """
    price: per unit of quantity
    """

    def __init__(
        self, price:float, user_id:int, quantity=1.0, buying=True, time=0, divisible=True
    ) -> None:
        self.quantity = quantity
        self.remaining_quantity = quantity
        self.price = price
        self.user = User(user_id)
        self.buying = buying
        self.time = time
        self.divisible = divisible

    def __eq__(self, other):
        return self.price == other.price

    def __lt__(self, other):
        return self.price < other.price

    def __gt__(self, other):
        return self.price > other.price

    def __add__(self, other):
        return self.price + other.price

    def __repr__(self) -> str:
        return f"{self.quantity} * {self.price}"

    def as_dict(self):
        return {
            "user": self.user,
            "buying": self.buying,
            "price": self.price,
            "quantity": self.quantity,
            "remaining_quantity": self.remaining_quantity,
            "time": self.time,
            "divisible": self.divisible,
        }
