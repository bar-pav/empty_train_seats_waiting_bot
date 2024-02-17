from dataclasses import dataclass

from aiogram.fsm.state import State
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext


class M(type):
    def __new__(mcs, name, bases, dct, **kwargs):
        print(name, bases, dct, sep=', ')
        print(kwargs)
        cls = super().__new__(mcs, name, bases, dct, **kwargs)
        print(':', cls)


class A(metaclass=M):
    x = None
    # pass


# print(type(M))
# print(type(A), A.__name__)


def a(**kwargs):
    print(kwargs)


a(x=1)
