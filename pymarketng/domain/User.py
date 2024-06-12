class User:
    _instances = {}

    def __new__(cls, id_num=None):
        if id_num is None:
            # If id_num is not provided, it's likely a deepcopy operation
            # Return a new instance without registering it in _instances
            return super().__new__(cls)
        if id_num not in cls._instances:
            cls._instances[id_num] = super().__new__(cls)
        return cls._instances[id_num]

    def __init__(self, id_num, name="") -> None:
        if not hasattr(self, 'id'):
            self.name = name
            self.id = id_num
            self.total_bid = 0.0
            self.total_quantity = 0.0
            self.total_profit = 0.0
            self.profit_per_unit = 0.0
            self.transactions = []
            self.bids = []
            self.num_of_participations = 0
            self.score = 0  # custom variables for user

    def as_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "total_bid": self.total_bid,
            "total_quantity": self.total_quantity,
            "bids": self.bids,
            "transactions": self.transactions,
            "profit_per_unit": self.profit_per_unit,
            "total_profit": self.total_profit,
            "participations": self.num_of_participations,
            "score": self.score,
            # "addr": hex(id(self))
        }

    def __repr__(self) -> str:
        # return hex(id(self))
        return str(self.id)

    def __key(self):
        return (self.id)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, User):
            return self.__key() == other.__key()
        return NotImplemented
