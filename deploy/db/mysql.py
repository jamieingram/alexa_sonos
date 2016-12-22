"""
.. module:: mysql
   :synopsis: MySQL database utilities.

"""

import re

from fabric.api import run, prompt
from fabric.colors import blue, yellow, red
from fabric.state import env
from fabric.utils import puts
from deploy.decorators import pre_hooks, post_hooks


def get_root_user():
    """ Get database root user name.
    """

    if not env.mysql_root_user:
        env.mysql_root_user = prompt(yellow(
            '> [MySQL]: Please enter root user name:'))

    return env.mysql_root_user


def get_root_pass():
    """ Get database root user pass.
    """

    if not env.mysql_root_pass:
        env.mysql_root_pass = prompt(yellow(
            '> [MySQL]: Please enter root user password (leave blank if none):'))

    return env.mysql_root_pass


@pre_hooks()
@post_hooks()
def create_database(**kwargs):
    """ Create a MySQL database.

    .. note::
        Supports pre and post hooks
    """

    from conf import settings

    safe = re.compile('[\W]+', re.UNICODE)

    def demand_valid_username():
        while True:
            username = prompt(yellow('> [MySQL]: Database Username:'))
            if not validate_db_username(username):
                puts(red('[MySQL] Username must be shorter than 16 characters'))
            else:
                break
        return username

    create = prompt(yellow('> [MySQL]: Create a MySQL DB [Y/n]: '))

    if create.lower() == 'y':

        mysql = "mysql -u {0}".format(settings.MYSQL_ROOT_USER())

        if settings.PROJECT_DB_HOST():
            mysql += " --host {0}".format(settings.PROJECT_DB_HOST())

        if settings.MYSQL_ROOT_PASS():
            mysql += " -p{0}".format(settings.MYSQL_ROOT_PASS())

        db_name = settings.PROJECT_DB_NAME()
        if len(settings.PROJECT()):
            puts(yellow('> [MySQL]: ') + red('Your db name was truncated: ') + yellow(db_name))

        if not db_name:
            db_name = prompt(yellow('> [MySQL]: Please enter a database name: '))
            db_name = safe.sub('', db_name)

        puts(blue('[MySQL] Database name: {0}'.format(db_name)))

        command = mysql + " --execute='CREATE DATABASE IF NOT EXISTS "\
                          "`{0}` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE "\
                          "utf8_unicode_ci */'".format(db_name)
        run(command)

        create_user = prompt(yellow('> [MySQL]: Create user for {0}? '
                                    '[Y/n]:'.format(db_name)))

        if create_user.lower() == 'y':

            username = settings.PROJECT_DB_USER()
            if not username or not validate_db_username(username):
                username = demand_valid_username()

            try:
                password = settings.PROJECT_DB_PASS().get(env.target)
            except AttributeError:
                password = None

            if not password:
                password = prompt(yellow('> [MySQL]: Database User Password for {0.target} environment:'.format(env)))

            command = mysql + " --execute=\"GRANT ALL PRIVILEGES "\
                              "ON {0}.* TO {1}@'localhost' IDENTIFIED BY "\
                              "'{2}'\"".format(db_name, username, password)
            run(command)

    else:
        puts(yellow('[MySQL]: Skipping DB Creation'))


def validate_db_username(username):
    safe = re.compile('[\W]+', re.UNICODE)
    username = safe.sub('', username)
    if len(username) > 16:
        return False
    return True
