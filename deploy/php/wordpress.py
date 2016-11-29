"""
.. module:: wordpress
   :synopsis: Wordpress utilities.

.. moduleauthor:: Jamie Ingram
"""

import os

from velcro import VelcroException
from velcro.utils import _symlink, _print_error


def symlink():
    """
    Symlink wp-config file to project root

    .. note::
        This assumes your Wordpress install has a env specific
        config folder within the project root - e.g.
        /poke/data/www/client/project/project_live/src/src/project/config/live
        this requires the env variable config_path_pipeline
    """

    from velcro.conf import settings

    try:
        conf_file = os.path.join(settings.CONFIG_PATH(), 'wp-config.php')
        destination_dir = os.path.join(
            settings.SRC_PATH(), 'src', settings.PROJECT()
        )
    except VelcroException as e:
        _print_error(e)
    else:
        _symlink(destination_dir, conf_file)
