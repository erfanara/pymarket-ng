class Bid:
    """
    price: per unit of quantity
    """

    def __init__(
        self, price, user, quantity=1.0, buying=True, time=0, divisible=True
    ) -> None:
        self.quantity = quantity
        self.price = price
        self.user = user
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
            "quantity": self.quantity,
            "price": self.price,
            "user": self.user,
            "buying": self.buying,
            "time": self.time,
            "divisible": self.divisible,
        }
