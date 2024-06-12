class User:
    def __init__(self, id_num, name="") -> None:
        self.name = name
        self.id = id_num
        self.balance = 0
        self.total_profit = 0
        self.profit_per_unit = 0
        self.transactions = []
        self.bids = []
        self.num_of_participations = 0
        self.score = 0  # custom variables for user

    def as_dict(self):
        return {
            "id": self.id,
            "profit": self.total_profit,
            "transactoins": self.transactions,
            "bids": self.bids,
            "participations": self.num_of_participations,
        }

    def __repr__(self) -> str:
        return str(self.id)

    # TODO: whats the point of these functions?
    # def __key(self):
    #     return (self.id)

    # def __hash__(self):
    #     return hash(self.__key())

    # def __eq__(self, other):
    #     if isinstance(other, User):
    #         return self.__key() == other.__key()
    #     return NotImplemented
