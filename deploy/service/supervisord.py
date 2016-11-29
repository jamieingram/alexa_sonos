"""
.. module:: service.supervisor
   :synopsis: Install and manage services managed by supervisord.

"""

import ConfigParser
import os

from fabric.colors import green, red, yellow, blue
from fabric.utils import puts
from deploy import FabricException
from deploy.utils import _print_error, _sudo, _symlink


def symlink():
    """
    Symlink project supervisord configs into supervisord directory.

    .. note::
        To use this you must provide the following ``env`` settings in the
        ``fabfile.py``:

        - ``env.supervisord_config_dir``
        - ``env.supercisord_configs``

        For example:

        - ``env.supervisord_config_dir = '/poke/data/conf/supervisord/``
        - ``env.supercisord_configs = ['supervisord.django.conf', ]``

    Using the example settings above the following symlinks would be created:

    - ``/path/to/project/config/dir/supervisord.gunicorn.conf > \
/poke/data/conf/supervisord/client_project_django_target.conf``

    Set ``env.supervisord_symlink_sudo = True`` to run as sudo.
    """

    from velcro.conf import settings

    symlinks = []

    try:
        sudo = settings.SUPERVISORD_SYMLINK_SUDO()
        configs = settings.SUPERVISORD_CONFIGS()
        for target_name in configs:
            fname, ext = os.path.splitext(target_name)
            name = fname.split('.')[-1:][0]
            config_name = '{client}_{project}_{name}_{target}.conf'.format(
                name=name,
                client=settings.CLIENT(),
                project=settings.PROJECT(),
                target=settings.TARGET())
            config_path = os.path.join(
                settings.SUPERVISORD_CONFIG_DIR(),
                config_name)
            target_path = os.path.join(
                settings.CONFIG_PATH(),
                target_name)
            symlinks.append((config_path, target_path))
    except FabricException as e:
        _print_error(e)
    else:
        for link, target in symlinks:
            _symlink(target, link, use_sudo=sudo)


def _get_programs():
    """
    Get the list of programs defined on the configs.

    :returns: List -- of programs
    """

    from velcro.conf import settings

    programs = []

    try:
        configs = settings.SUPERVISORD_CONFIGS()
        for config in configs:
            path = os.path.join(settings.LOCAL_CONFIG_PATH(), config)
            parser = ConfigParser.ConfigParser()
            parser.readfp(open(path))
            for section in parser.sections():
                if section.startswith('program:'):
                    p, full_name = section.split(':')
                    split_full_name = full_name.split('_')
                    not_in_list = [
                        settings.PACKAGE_NAME(),
                        settings.CLIENT(),
                        settings.TARGET()
                    ]
                    human_name = '_'.join(
                        filter(lambda e: e not in not_in_list,
                               split_full_name))
                    programs.append((human_name, full_name))
    except FabricException as e:
        _print_error(e)
    else:
        return programs


def _get_program_name(hname):
    """
    Return the full program name from the human name.
    """

    programs = _get_programs()
    try:
        program = [f for h, f in programs if h == hname][0]
    except IndexError:
        _print_error("[Supervisor] Unknown Program: {0}".format(hname))
    else:
        return program


def list_programs():
    """
    List the available programs.
    """

    puts(green('[Supervisord]: Available programs:'))
    programs = _get_programs()
    for human_name, full_name in programs:
        puts(blue('  > {0} ({1})'.format(human_name, full_name)))


def reread():
    """
    Reread supervisord configs and update.
    """

    _sudo('supervisorctl -c /etc/supervisord/supervisord.conf reread')
    _sudo('supervisorctl -c /etc/supervisord/supervisord.conf update')


def start(name):
    """
    Start supervisord service

    :param name: Name of the supervisord service
    :type name: str
    """

    program = _get_program_name(name)

    puts(green('[Supervisord]: Starting {0}'.format(name)))
    _sudo('supervisorctl -c /etc/supervisord/supervisord.conf '
          'start {0}'.format(program))


def stop(name):
    """
    Stop suoervisord service

    :param name: Name of the supervisord service
    :type name: str
    """

    program = _get_program_name(name)

    puts(red('[Supervisord]: Stopping {0}'.format(name)))
    _sudo('supervisorctl -c /etc/supervisord/supervisord.conf '
          'stop {0}'.format(program))


def restart(name):
    """
    Restart supervisord service

    :param name: Name of the supervisord service
    :type name: str
    """

    program = _get_program_name(name)

    puts(yellow('[Supervisord]: Restarting {0}'.format(name)))
    _sudo('supervisorctl -c /etc/supervisord/supervisord.conf '
          'restart {0}'.format(program))
