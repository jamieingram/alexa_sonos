"""
.. module:: velcro.target
   :synopsis: Common pre defined target functions.

"""

from .utils import _target


def live():
    """ Set the target to live environment """

    return _target('live')


def stage():
    """ Set the target to stage environment """

    return _target('stage')


def test():
    """ Set the target to test environment """

    return _target('test')


def dev():
    """ Set the target to dev environment """

    return _target('dev')
