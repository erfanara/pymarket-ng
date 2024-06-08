class User:
    def __init__(self, id) -> None:
        self.id = id
        self.profit = 0
        self.transactions = []
        self.bids = []
        self.num_of_participations = 0

    def as_dict(self):
        return {
            "id": self.id,
            "profit": self.profit,
            "transactoins": self.transactions,
            "bids": self.bids,
            "participations": self.num_of_participations,
        }

    def __repr__(self) -> str:
        return str(self.id)