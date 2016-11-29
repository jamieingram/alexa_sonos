"""
.. module:: velcro.env
   :synopsis: Project bootstrapping, usually only called a few times.

"""

import os

from fabric.api import run
from fabric.contrib.files import exists
from fabric.context_managers import cd
from fabric.colors import blue, green, yellow
from fabric.utils import puts
from . import FabricException
from decorators import pre_hooks, post_hooks
from utils import _print_error


@pre_hooks()
@post_hooks()
def bootstrap(**kwargs):
    """ Bootstrap an environment. For example creating project directories
    defined inside the ``fabfile.py``.

    .. note::
        Supports pre and post hooks

    **Usage:**

    .. code-block:: none

        # No Hooks
        fab {target} bootstrap

        # With pre hooks
        fab {target} bootstrap:pre_hooks=some_hook

        # With post hooks
        fab {target} bootstrap:post_hooks=some_hook

        # With pre and post hooks
        fab {target} bootstrap:pre_hooks=a_hook|b_hook,post_hooks=c_hook


    ****kwargs:**

    :param pre_hooks: List of hooks to run pre bootstrap
    :type pre_hooks: list

    :param post_hooks: List of hooks to run post bootstrap
    :type post_hooks: list
    """

    from conf import settings

    def walk_directories(d, depth=0, base=''):
        for k, v in sorted(d.items(), key=lambda x: x[0]):
            path = os.path.join(base, k)
            if isinstance(v, dict):
                walk_directories(v, depth=depth + 1, base=path)
            else:
                if not exists(path):
                    run('mkdir -p {0}'.format(path))
                    puts(blue(('|- ') * (depth + 1) + k))

    try:
        if not exists(settings.BASE_PATH()):
            puts(yellow('[WARNING]: {0} Does not exist, creating. '.format(
                settings.BASE_PATH())))
            run('mkdir -p {0}'.format(settings.BASE_PATH()))
        puts(blue('Creating directories at {0}'.format(
            settings.BASE_PATH())))
        walk_directories(settings.DIRECTORIES(), base=settings.BASE_PATH())
    except FabricException as e:
        _print_error(e)

    # Log Path - Can be different
    if not exists(settings.LOG_PATH()):
        puts(blue('Creating logging directory'))
        puts(blue('Create log directory: ') + green(settings.LOG_PATH()))
        run('mkdir -p {0}'.format(settings.LOG_PATH()))

    try:
        scm_init = {
            'git': _git_init
        }[settings.SCM()]
        scm_init()
    except KeyError:
        _print_error('Unable to initialise {0} repository, only {1} '
                     'are supported'.format(settings.SCM(), ', '.join(
                         settings.SUPPORTED_SCM)))
    except FabricException as e:
        _print_error(e)


def _git_init():
    """ Create Git repository in settings.SRC_PATH()
    """

    from velcro.conf import settings

    puts(blue('Initialising git repository'))
    command = 'if [ ! -d ./.git ]; then git init && git config '\
              'receive.denyCurrentBranch ignore; fi;'
    with cd(settings.SRC_PATH()):
        try:
            puts(blue('Running: ') + green(command))
            run(command)
        except:
            _print_error('Failed to create git repository')
