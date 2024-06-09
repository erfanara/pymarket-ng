import pandas as pd
from pymarketng.domain.User import User


class UserManager:
    def __init__(self) -> None:
        self.users = {}

    def add_user(self, *users: User):
        for u in users:
            self.users[u.id] = u

    def add_users(self, users: list[User]):
        self.add_user(*users)

    def get_df(self):
        return pd.json_normalize([u.as_dict() for u in self.users])