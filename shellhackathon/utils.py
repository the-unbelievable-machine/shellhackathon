import itertools
from typing import List

import pandas as pd


####################################################################################################
# Project specific helper functions


####################################################################################################
# Generic helper functions
def function_with_doctest(arg):
    """
    Doctests are executed automatically.

    Examples:
        >>> function_with_doctest('hello world')
        hello world

        >>> function_with_doctest(42)
        42
    """
    print(arg)


def pairwise(iterable):
    """
    Pairwise iteration with overlap.

    Examples:
        >>> l = list(range(5))
        >>> list(pairwise(l))
        [(0, 1), (1, 2), (2, 3), (3, 4)]

    Taken from https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def dict_product(dicts):
    """
    Calculate the cross-product of all entries of the given dicts.

    Examples:
        >>> list(dict_product(dict(char='ab', num=[1, 2])))
        [{'char': 'a', 'num': 1}, {'char': 'a', 'num': 2}, {'char': 'b', 'num': 1}, {'char': 'b', 'num': 2}]
    """
    return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))


def gather(df, key: str, value: str, cols: List[str]):
    """
    tidyr-like gather function.

    Args:
        df: the dataframe to gather data from
        key: the name of the new key column
        value: the name of the new value column
        cols: list of name of the columns to gather from df

    Examples:
        >>> df = pd.DataFrame({'names': ['Wilbur', 'Petunia', 'Gregory'],
        ...                    'a': [67, 80, 64],
        ...                    'b': [56, 90, 50]})
        >>> df
             names   a   b
        0   Wilbur  67  56
        1  Petunia  80  90
        2  Gregory  64  50
        >>> gather(df, 'drug', 'heartrate', ['a', 'b'])
             names drug  heartrate
        0   Wilbur    a         67
        1  Petunia    a         80
        2  Gregory    a         64
        3   Wilbur    b         56
        4  Petunia    b         90
        5  Gregory    b         50

    See:
        - https://blog.rstudio.com/2014/07/22/introducing-tidyr/
        - http://connor-johnson.com/2014/08/28/tidyr-and-pandas-gather-and-melt/

    """
    assert all(col in df.columns for col in cols), 'col does not exist in df'
    id_vars = [col for col in df.columns if col not in cols]
    return pd.melt(df,
                   id_vars=id_vars,
                   value_vars=cols,
                   var_name=key,
                   value_name=value)


def mark_consecutive(series: pd.Series) -> pd.Series:
    """
    Return a `pd.Series` which has the same ID (starting from 0)
    for consecutive parts of the given series.

    Examples:
        >>> series = pd.Series([1, 1, 1, 5, 5])
        >>> mark_consecutive(series)
        0    0
        1    0
        2    0
        3    1
        4    1
        dtype: int64
    """
    shifted = series.shift(1)
    changepoints = shifted != series
    return changepoints.cumsum() - 1
