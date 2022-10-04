from enum import Enum
from functools import wraps
from tabulate import tabulate
from termgraph.module import BarChart, Data

import click

def print_table(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        data = func(*args, **kwargs)
        click.echo(tabulate(data))

    return wrapper_func

def print_chart(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        data, labels = func(*args, **kwargs)
        chart = BarChart(Data(data, labels))
        chart.draw()

    return wrapper_func

class EnumType(click.Choice):
    def __init__(self, enum: Enum, case_sensitive=False):
        self.__enum = enum
        super().__init__(
            choices=[item.value for item in enum], case_sensitive=case_sensitive
        )

    def convert(self, value, param, ctx):
        if value is None or isinstance(value, Enum):
            return value

        converted_str = super().convert(value, param, ctx)
        return self.__enum(converted_str)