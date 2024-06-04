import pandas as pd

from pymarketng.domain.Transaction import Transaction


class TransactionManager:
    def __init__(self) -> None:
        self.trans = []

    def add_transaction(self, *transactions: Transaction):
        self.trans.extend(transactions)

    def add_transactions(self, bids: list[Transaction]):
        self.trans.extend(bids)

    def get_df(self):
        return pd.json_normalize([t.as_dict() for t in self.trans])