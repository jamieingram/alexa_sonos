"""
.. module:: utils
   :synopsis: Common helper utilities.

"""

import datetime
import os
import time
from yaml import load

from fabric.api import run, sudo
from fabric.colors import green, blue, red, yellow
from fabric.state import env
from fabric.utils import puts


def _print_error(message):
    """ Print error messages.

    :param message: The error message to print.
    :type message: str
    """

    puts(red('[ERROR]: {0}'.format(message), bold=True))


def _raise(exception):
    """ Raise exception, for usage in lambda's

    :param exception: The exception to be raised
    :type exception: Object
    """

    raise exception


def _sudo(command):
    """ Run command with sudo privileges

    :param command: The command to run with sudo.
    :type target: str.

    :returns: bool -- True if successful False if not.
    """

    if env.sudo_user:
        sudo(command)
    else:
        raise FabricException('Could not run {0}, missing '
                              'sudo user'.format(command))


def _symlink(target_path, link_path, use_sudo=False):
    """ Generate symbolic links.

    :param target_path: The symlink target path.
    :type target_path: str.

    :param link_path: The name for the symlinked file.
    :type link_path: str.

    :returns: bool -- True if successful False if not.
    """

    unlink = 'if [ -L {0} ]; then unlink {0}; fi'.format(link_path)
    link = 'ln -s {0} {1}'.format(target_path, link_path)

    try:
        if use_sudo:
            _sudo(unlink)
            _sudo(link)
        else:
            run(unlink)
            run(link)
        return True
    except FabricException as e:
        _print_error(e)
        return False
    except:
        _print_error('Symlink Failed: {0} > {1}'.format(target_path,
                                                        link_path))
        return False


def _target(name):
    """ Set environment target.

    :param name: The target name, for example 'stage'.
    :type target_path: str.
    """

    from conf import settings

    puts(blue('Set target: ') + green(name.title(), bold=True))

    now = time.time()

    env.now = str(int(now))
    env.now_str = datetime.datetime.fromtimestamp(now).strftime(
        '%d-%m-%Y at %H:%M')

    env.target = name
    try:
        env.base_path = os.path.join(settings.ROOT_PATH(), settings.CLIENT(),
                                     settings.PROJECT(),
                                     '{0}_{1}'.format(settings.PROJECT(),
                                                      settings.TARGET()))
    except FabricException as e:
        _print_error(e)


def _call_hooks(hooks):
    """ Run hook functions.

    :param hooks: List of hooks to import and call
    :type hooks: list or tuple
    """

    if hooks:
        for hook in hooks:
            try:
                path, name = os.path.splitext(hook)
                module = __import__(path, globals(), locals(), [name[1:]], -1)
                func = getattr(module, name[1:], None)
                if not callable(func):
                    _print_error('{0} is not callable'.format(hook))
                else:
                    puts(yellow('[HOOK]: {0}'.format(hook)))
                    func()
            except ImportError:
                _print_error('Failed to import hook: {0}'.format(hook))


def print_config_path():
    """
    Print config build path.

    **Usage:**

    Import into the ``fabfile.py``:

    .. code-block:: python:

        from velcro.utils import print_config_path


    Then use on the CLI:

    .. code-block:: none

        fab live print_config_path
    """

    from conf import settings
    puts(blue('Config Path: {0}'.format(settings.CONFIG_PATH())))


def print_local_config_path():
    """
    Print the local config path from the root of the
    repository.

    **Usage:**

    Import into the ``fabfile.py``:

    .. code-block:: python:

        from velcro.utils import print_local_config_path


    Then use on the CLI:

    .. code-block:: none

        fab live print_local_config_path
    """

    from conf import settings
    puts(blue('Config Path: {0}'.format(settings.LOCAL_CONFIG_PATH())))


def cdn_timestamp():
    """
    Write the current timestamp to an importable file

    **Usage:**

    Add to the deploy function as a post_hook ``fabfile.py``:
    Make sure it comes after git.clean or it will get deleted

    .. code-block:: python:
        ...
        @post_hooks(
            'velcro.utils.cdn_timestamp',
    """
    from conf import settings

    timestamp = str(int(time.time()))
    timestamp_path = os.path.join(settings.SRC_PATH(), 'src', env.project,
                                  'timestamp.py')
    run('touch {0}'.format(timestamp_path))
    run('echo "TIMESTAMP = {timestamp}" > {path}'.format(timestamp=timestamp,
                                                         path=timestamp_path))
    puts(blue('Updating CDN Timestamp: {0}'.format(timestamp)))


def get_local_config():
    """
    Sometimes it helps to keep some configs in a local file.
    this reads key value pairs from a ~/.velcro.yml file
    and adds them to the env

    Yaml format:

    .. code-block:: yaml:
        group:
          - property: value


    eg:

    .. code-block:: yaml:
        mysql:
          - root_user: root

    """

    try:
        with open(os.path.join(os.environ.get('HOME'), '.velcro.yml'), 'r') as f:
            data = load(f.read())
    except IOError:
        pass
    else:
        for group, config in data.iteritems():
            for k, v in config.iteritems():
                prop = '{group}_{key}'.format(group=group, key=k)
                setattr(env, prop, v)
