"""
.. module:: nginx
   :synopsis: Nginx utility functions.

"""

import os

from fabric.colors import green, yellow, red
from fabric.utils import puts
from deploy import FabricException
from deploy.utils import _symlink, _print_error, _sudo


def symlink():
    """
    Symlink project Nginx configs to Nginx config root

    .. warning::
        This uses the sites-enabled / sites-available pattern.

    .. note::
        To use this you must provide the following ``env`` settings in the
        ``fabfile.py``:

        - ``env.http_server_conf_path``
        - ``env.nginx_conf``

        For example:

        - ``env.http_server_conf_path = '/etc/nginx/``
        - ``env.nginx_conf = 'nginx.conf'``

    Using the example settings above the following symlinks would be created:

    - ``/path/to/project/config/dir/nginx.conf > \
/etc/nginx/sites-available/client_project_target.conf``
    - ``/etc/nginx/sites-available/client_project_target.conf > \
/etc/nginx/sites-enabled/client_project_target.conf``

    Set ``env.nginx_symlink_sudo = True`` to run symlinks as sudo
    """

    from conf import settings

    try:
        sudo = settings.NGINX_SYMLINK_SUDO()
        config_name = '{client}_{project}_{target}'.format(
            client=settings.CLIENT(), project=settings.PROJECT(),
            target=settings.TARGET())
        available_path = os.path.join(
            settings.HTTP_SERVER_CONF_PATH(), 'sites-available')
        enabled_path = os.path.join(
            settings.HTTP_SERVER_CONF_PATH(), 'sites-enabled')
        conf_path = os.path.join(settings.CONFIG_PATH(), settings.NGINX_CONF())
    except FabricException as e:
        _print_error(e)
    else:
        _symlink(conf_path, os.path.join(available_path, config_name),
                 use_sudo=sudo)
        _symlink(os.path.join(available_path, config_name),
                 os.path.join(enabled_path, config_name),
                 use_sudo=sudo)


def restart_nginx():
    """
    Restart Nginx Daemon
    """

    puts(yellow('[Nginx] Restarting'))
    _sudo('service nginx restart')


def reload_nginx():
    """
    Reload Nginx Configs
    """

    puts(yellow('[Nginx] Reloading'))
    _sudo('service nginx reload')


def stop_nginx():
    """
    Stop Nginx Daemon
    """

    puts(red('[Nginx] Stopping'))
    _sudo('service nginx stop')


def start_nginx():
    """
    Start Nginx Daemon
    """

    puts(green('[Nginx] Starting'))
    _sudo('service nginx start')
