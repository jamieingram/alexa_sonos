"""
.. module:: conf
   :synopsis: Configurable settings.

"""

import os

from fabric.state import env
from . import FabricException
from db.mysql import get_root_user, get_root_pass
from utils import _raise

from utils import get_local_config


class Config(object):

    """ velcro configuration class, for easy reference to settings defined
    in fabfile.py

    .. note::
       Do not call this directly, use:
       conf import settings
       settings.IS_STATIC().
    """

    def __init__(self, *args, **kwargs):
        """ Sets up setting attributes.
        """

        # Get any config vars that are in the local ~/.velcro.yml file
        # and set them on the env object
        get_local_config()

        # Timestamps - set on target
        self.NOW = self._env_config(
            'now', lambda: _raise(FabricException(
                'Missing timestamp, have you set target?')))
        self.NOW_STR = self._env_config(
            'now_str', lambda: _raise(FabricException(
                'Missing timestamp, have you set target?')))

        # Directories
        self.CONFIG_DIR = self._env_config('config_dir', 'config')

        # Paths
        self.ROOT_PATH = self._env_config(
            'root_path', lambda: _raise(FabricException(
                'env.root_path required')))
        self.BASE_PATH = self._env_config(
            'base_path', lambda: _raise(FabricException(
                'Missing Base Path, have you set a target?')))
        self.SRC_PATH = lambda: os.path.join(self.BASE_PATH(), 'src')
        self.LOCAL_PATH = self._env_config(
            'local_path', lambda: _raise(FabricException(
                'env.local_path is required.')))
        self.LOG_PATH = self._env_config(
            'log_path', lambda: os.path.join(self.BASE_PATH(), 'logs'))
        self.CONFIG_PATH_PIPELINE = self._env_config(
            'config_path_pipeline', lambda: ['{package_name}'
                                             '{config_dir}',
                                             '{target}'])
        self.CONFIG_PATH = self._env_config(
            'config_path', lambda: os.path.join(*self._build_config_path()))
        self.LOCAL_CONFIG_PATH = lambda: os.path.join(
            *self._build_config_path(local=True))
        self.HTTP_SERVER_CONF_PATH = self._env_config(
            'http_server_conf_path', lambda: _raise(FabricException(
                'env.http_server_conf_path is required.')))

        # Logs
        self.DEPLOY_LOG = lambda: os.path.join(self.LOG_PATH(), 'deploy.log')
        self.ROLLBACK_LOG = lambda: os.path.join(self.LOG_PATH(),
                                                 'rollback.log')

        # Project Details
        self.CLIENT = self._env_config('client', lambda: env.user)
        self.PROJECT = self._env_config(
            'project', lambda: _raise(FabricException('Missing Project Name')))
        self.PACKAGE_NAME = self._env_config('package_name',
                                             lambda: self.PROJECT())

        # Target
        self.TARGET = self._env_config(
            'target', lambda: _raise(FabricException('Missing Target')))

        # Directories
        self.DIRECTORIES = self._env_config('directories', ['src', ])

        # SCM
        self.SUPPORTED_SCM = ['git', ]
        self.SCM = self._env_config(
            'scm', lambda: _raise(FabricException('env.scm is required')))

        # Python
        self.PY_VENV_BASE = self._env_config(
            'py_venv_base', lambda: _raise(FabricException(
                'env.py_venv_base is required.')))
        self.PY_VENV_NAME = self._env_config(
            'py_venv_name', lambda: '{target}_{client}_{project}'.format(
                target=self.TARGET(),
                client=self.CLIENT(),
                project=self.PROJECT()))
        self.PY_PIP_REQS_FILE = self._env_config(
            'py_pip_reqs_file', 'requirements.txt')

        # Location of setup.py to install the package
        self.PY_SRC_DIRNAME = self._env_config('py_src_dirname', None)

        # DJANGO
        self.DJANGO_SETTINGS_MODULE = self._env_config(
            'django_settings_module', lambda: _raise(FabricException(
                'env.django_settings_module is required.')))

        # MySQL
        self.MYSQL_ROOT_USER = self._env_config(
            'mysql_root_user', lambda: get_root_user())
        self.MYSQL_ROOT_PASS = self._env_config(
            'mysql_root_pass', lambda: get_root_pass())

        # For creating project DB
        self.PROJECT_DB_HOST = self._env_config('project_db_host', None)
        self.PROJECT_DB_USER = self._env_config('project_db_user',
                lambda: '{0}_{1}'.format(env.project[0:10], env.target))
        self.PROJECT_DB_NAME = self._env_config('project_db_name',
                lambda: '{0}_{1}'.format(env.project[0:10], env.target))

        self.PROJECT_DB_PASS = self._env_config('project_db_pass', None)

        # Upstart Service
        self.UPSTART_SCRIPTS = self._env_config(
            'upstart_scripts', lambda: _raise(FabricException(
                'env.upstart_scripts is required.')))

        # Supervisord Services
        self.SUPERVISORD_CONFIG_DIR = self._env_config(
            'supervisord_config_dir', lambda: _raise(FabricException(
                'env.supervisord_config_dir is required')))
        self.SUPERVISORD_CONFIGS = self._env_config(
            'supervisord_configs', lambda: _raise(FabricException(
                'env.supervisord_configs is required')))
        self.SUPERVISORD_SYMLINK_SUDO = self._env_config(
            'supervisord_symlink_sudo', lambda: False)

        # Nginx
        self.NGINX_CONF = self._env_config(
            'nginx_conf', lambda: _raise(FabricException(
                'env.nginx_conf is required.')))
        self.NGINX_SYMLINK_SUDO = self._env_config(
            'nginx_symlink_sudo', lambda: False)

        # Users
        self.SUDO_USER = self._env_config('sudo_user', lambda: env.user)
        self.USER = self._env_config(
            'user', lambda: _raise(FabricException(
                'env.nginx_conf is required.')))
        # Current Host
        self.HOST = self._env_config(
            'host', lambda: _raise(FabricException(
                'env.host is required.')))

    def _env_config(self, name, default=None):
        """ Allows for configurable settings to be passed as values for
        immediate execution or as values for deferred execution.

        :param name: The setting name.
        :type name: str.

        :param default: Default value if setting does not exist.
        :type default: str or int or callable.

        :returns: callable -- The setting.
        """

        def inner():
            setting = getattr(env, name, default)
            if callable(setting):
                try:
                    return setting()
                except AttributeError:
                    return None
            else:
                return setting

        return inner

    def _build_config_path(self, local=False):
        """
        Build the config path from the list pipeline.
        """

        pipeline_map = {
            'package_name': self.PACKAGE_NAME(),
            'config_dir': self.CONFIG_DIR(),
            'target': self.TARGET()
        }

        if local:
            dirs = [
                self.LOCAL_PATH()
            ]
        else:
            dirs = [
                self.SRC_PATH()
            ]

        pipeline = self.CONFIG_PATH_PIPELINE()
        for el in pipeline:
            broken = False
            for k, v in pipeline_map.iteritems():
                try:
                    dirs.append(el.format(**{k: v}))
                except KeyError:
                    pass
                else:
                    broken = True
                    break
            if not broken:
                dirs.append(el)

        return dirs


settings = Config()
