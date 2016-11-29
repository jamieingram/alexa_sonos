#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
.. module:: git
   :synopsis: Git utilities.

"""

from __future__ import unicode_literals

from fabric.api import run, local, prompt
from fabric.colors import blue, yellow, red
from fabric.context_managers import cd
from fabric.utils import puts
from fabric.state import env

from deploy import FabricException
from deploy.decorators import pre_hooks, post_hooks
from deploy.utils import _print_error


def clean():
    """ Clean git repository.
    """

    from velcro.conf import settings

    try:
        with cd(settings.SRC_PATH()):
            puts(blue('[GIT] Cleaning'))
            run("git clean -df")
    except FabricException as e:
        _print_error(e)


def update_submodules():
    """ Update git submodules
    """

    from velcro.conf import settings

    try:
        with cd(settings.SRC_PATH()):
            puts(blue('[GIT] Updating sub modules'))
            run('git submodule update --init')
    except FabricException as e:
        _print_error(e)


@pre_hooks()
@post_hooks()
def deploy(branch, **kwargs):
    """ Deploy project code using git.

    .. note::
        Supports pre and post hooks.

    :param banch: Branch to deploy HEAD from
    :type branch: str
    """

    from velcro.conf import settings

    commit = local('git log -1 --format=format:%H {0}'.format(branch),
                   capture=True)

    if 'live' == env.target and 'master' != branch:

        puts((blue('[ROBO NAG] 👮  Oh, I see you\'re pushing ') +
              yellow(branch) +
              blue(' to live. Y\'all be sure to merge to master now'))
             .encode('utf-8'))

        answer = prompt(yellow(u'[ROBO NAG] want me to do it?'))

        if 'y' == answer.lower():
            cmd = 'git checkout master && git pull origin master && '\
                  'git merge {0} && git push origin master -u'.format(branch)
            local(cmd)
        else:
            prompt(red('[ROBO NAG] Ok, I\'m sure you\'re just testing something. '
                       'Good luck, merge it when you get a mo yeh?'))

    elif 'live' == env.target and 'master' == branch:
        puts(blue('[ROBO NAG] 🎉  Woop woop! deploying live').encode('utf-8'))
        answer = prompt(yellow('[ROBO NAG] Push to Githubs?'))

        if 'y' == answer.lower():
            cmd = 'git pull origin master && git push origin master -u'
            local(cmd)
            puts(blue('[ROBO NAG] 😇 Pushing Master to Origin').encode('utf-8'))

    try:
        push = 'git push -f ssh://{user}@{host}/{src} {branch}'.format(
            user=settings.USER(), host=settings.HOST(),
            src=settings.SRC_PATH(), branch=branch)
    except FabricException as e:
        _print_error(e)
    else:
        puts((blue('[GIT] Force Pushing on ') +
              yellow(branch) +
              blue(' branch')))
        local(push)
        with cd(settings.SRC_PATH()):
            puts(blue('[GIT] Resetting to: {0}'.format(commit)))
            run('git reset --hard {0}'.format(commit))
