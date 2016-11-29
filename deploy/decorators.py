"""
.. module:: decorators
  :synopsis: Common function decorators.

"""

from utils import _call_hooks

from functools import wraps


def pre_hooks(*args):
    """ Pre hooks decorator, runs functions before the call of the
    decorated function.

    :rtype: callable -- the decorated function
    """

    arg_hooks = None
    if args:
        arg_hooks = args

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if arg_hooks:
                _call_hooks(arg_hooks)
            hooks = kwargs.get('pre')
            if hooks:
                _call_hooks(hooks.split('|'))
            return func(*args, **kwargs)
        return wrapper
    return inner


def post_hooks(*args):
    """ Post hooks decorator, runs functions after the call of the
    decorated function.

    :rtype: callable -- the decorated function
    """

    arg_hooks = None
    if args:
        arg_hooks = args

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            if arg_hooks:
                _call_hooks(arg_hooks)
            hooks = kwargs.get('post')
            if hooks:
                _call_hooks(hooks.split('|'))
        return wrapper
    return inner
