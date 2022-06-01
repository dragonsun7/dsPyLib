#! /usr/bin/env python3
from __future__ import print_function

# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-06-01 21:25:53'

# noinspection HttpUrlsUsage
"""
    对象内存占用
    https://blog.csdn.net/PSpiritV/article/details/123224519
    http://lvkun.site/#!/python-object-memory-usage
    https://code.activestate.com/recipes/577504/
"""

from collections import deque
from itertools import chain
from sys import getsizeof, stderr

try:
    from reprlib import repr
except ImportError:
    pass


def total_size(o, handlers=None, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    if handlers is None:
        handlers = {}
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: lambda d: chain.from_iterable(d.items()),
                    set: iter,
                    frozenset: iter,
                    }
    all_handlers.update(handlers)  # user handlers take precedence
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(obj):
        if id(obj) in seen:  # do not double count the same object
            return 0
        seen.add(id(obj))
        s = getsizeof(obj, default_size)

        if verbose:
            print(s, type(obj), repr(obj), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(obj, typ):
                s += sum(map(sizeof, handler(obj)))
                break
        else:
            if not hasattr(o.__class__, '__slots__'):
                if hasattr(o, '__dict__'):
                    # no __slots__ *usually* means a __dict__,
                    # but some special builtin classes (such as `type(None)`) have neither
                    s += sizeof(o.__dict__)
                    # else, `o` has no attributes at all, so sys.getsizeof() actually returned the correct value
            else:
                s += sum(sizeof(getattr(o, x)) for x in o.__class__.__slots__ if hasattr(o, x))
        return s

    return sizeof(o)


def demo():
    d = dict(a=1, b=2, c=3, d=[4, 5, 6, 7], e='a string of chars')
    print(total_size(d, verbose=True))


if __name__ == '__main__':
    demo()
