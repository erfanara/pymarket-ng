from pymarketng.domain.User import User


class Bid:
    """
    price: per unit of unit
    """

    def __init__(
        self, price:float, user_id:int, unit=1.0, buying=True, time=0, divisible=True
    ) -> None:
        self.unit = unit
        self.remaining_unit = unit
        self.price = price
        self.user = User(user_id)
        self.buying = buying
        self.time = time
        self.divisible = divisible

        # update user
        if self.buying:
            self.user.total_bid -= self.price*self.unit
            self.user.total_unit -= self.unit
        else:
            self.user.total_bid += self.price*self.unit
            self.user.total_unit += self.unit
        
        self.user.bids.append(self)

    def __eq__(self, other):
        return self.price == other.price

    def __lt__(self, other):
        return self.price < other.price

    def __gt__(self, other):
        return self.price > other.price

    def __add__(self, other):
        return self.price + other.price

    def __repr__(self) -> str:
        return f"{self.unit} * {self.price}"

    def as_dict(self):
        return {
            "user": self.user,
            "is_buying": self.buying,
            "price": self.price,
            'unit': self.unit,
            "remaining_unit": self.remaining_unit,
            "time": self.time,
            "divisible": self.divisible,
        }
