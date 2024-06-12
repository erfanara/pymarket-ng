import pandas as pd
from pymarketng.domain.User import User
from typing import Dict


class UserManager:
    def __init__(self) -> None:
        self.users: Dict[int, User] = {}

    def add(self, id_num):
        if self.users.get(id_num) is None:
            self.users[id_num] = User(id_num)

    def add_user(self, *users: User):
        for u in users:
            self.users[u.id] = u

    def get_df(self):
        return pd.json_normalize([v.as_dict() for k,v in self.users.items()])
