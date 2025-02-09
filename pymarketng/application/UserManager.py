import pandas as pd
# import fireducks.pandas as pd
from pymarketng.domain.User import User
from typing import Set


class UserManager:
    def __init__(self) -> None:
        self.users: Set[User] = set()

    def add(self, id_num):
        self.users.add(User(id_num))

    def add_user(self, *users: User):
        for u in users:
            self.users.add(u)

    def get_df(self):
        return pd.json_normalize([u.as_dict() for u in self.users])
