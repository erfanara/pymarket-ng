class User:
    _instances = {}

    def __new__(cls, id_num=None):
        if id_num is None:
            # TODO: remove these comments if needed
            # If id_num is not provided, it's likely a deepcopy operation
            # Return a new instance without registering it in _instances
            return super().__new__(cls)
        if id_num not in cls._instances:
            cls._instances[id_num] = super().__new__(cls)
        return cls._instances[id_num]

    def __init__(self, id_num, name="") -> None:
        if not hasattr(self, "id"):
            self.name = name
            self.id = id_num
            # TODO: what is this total bid? 
            self.total_bid = 0.0
            self.total_unit = 0.0
            self.total_sell_unit = 0.0
            self.total_buy_unit = 0.0
            self.total_profit = 0.0
            self.profit_per_unit = 0.0
            self.transactions = []
            self.bids = []
            self.num_of_participations = 0
            # TODO: clarify diff between total trade and total profit
            self.total_profit_p2p = 0.0
            self.total_profit_infra = 0.0
            self.total_profit_net = 0.0
            self.total_trade = 0.0
            self.total_trade_p2p = 0.0
            self.total_trade_infra = 0.0
            self.num_of_transactions_taken_via_p2p = 0
            self.num_of_transactions_taken_via_infra = 0
            self.score = 0  # TODO: custom variables for user
        
    def as_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "total_bid": self.total_bid,
            "total_unit": self.total_unit,
            "bids": self.bids,
            "transactions": self.transactions,
            "profit_per_unit": self.profit_per_unit,
            "total_profit": self.total_profit,
            "participations": self.num_of_participations,
            "score": self.score,
            "total_trade_p2p": self.total_trade_p2p,
            "total_trade_infra": self.total_trade_infra,
            "total_trade": self.total_trade,
            "total_profit_p2p": self.total_profit_p2p,
            "total_profit_infra": self.total_profit_infra,
            "total_net_profit": self.total_profit_net
            # "addr": hex(id(self))
        }

    def __repr__(self) -> str:
        # return hex(id(self))
        return str(self.id)

    def __key(self):
        return self.id

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, User):
            return self.__key() == other.__key()
        return NotImplemented
