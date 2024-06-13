import inspect
from typing import Callable, List, Type

from pymarketng.application.BidManager import BidManager
from pymarketng.application.Mechanism import Average_Mechanism_Multi, Mechanism
from pymarketng.application.TransactionManager import TransactionManager


class Market:
    def __init__(self, mechanism_selector: Callable) -> None:
        self.__check_signature_of_mechanism_selector(mechanism_selector)
        self.mechanism_selector = mechanism_selector
        self.bm_list=[]
        self.tm_list=[]

    def __check_signature_of_mechanism_selector(self, func):
        signature = inspect.signature(func)
        if len(signature.parameters) != 2:
            raise ValueError("Function must have exactly 2 parameters")
        if len(signature.parameters) != 2:
            raise ValueError("Function must have exactly 2 parameters")
        if list(signature.parameters.keys()) != ["bm_list", "tm_list"]:
            raise ValueError(
                "Function parameters must be named 'bm_list' and 'tm_list'"
            )
        if signature.parameters["bm_list"].annotation != List[BidManager]:
            raise ValueError("bm_list parameter must be a list of BidManager")
        if signature.parameters["tm_list"].annotation != List[TransactionManager]:
            raise ValueError("tm_list parameter must be a list of TransactionManager")
        if signature.return_annotation != Type[Mechanism]:
            raise ValueError("Function must return a subclass of Mechanism")

    # def run(self):
        



def mechanism_selctor_avg(
    bm_list: List[BidManager], tm_list: List[TransactionManager]
) -> Type[Mechanism]:
    return Average_Mechanism_Multi
