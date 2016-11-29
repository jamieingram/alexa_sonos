import os
from fabric.api import env, roles
from fabric.state import output
from fabric.operations import run, put, local

from deploy.env import bootstrap as _bootstrap
from deploy.decorators import pre_hooks, post_hooks
from deploy.http.nginx import (restart_nginx, reload_nginx, stop_nginx,
                               start_nginx)
from deploy.scm.git import deploy as _deploy
from deploy.target import live, stage

# Project Details
env.client = 'lingobee'
env.project = 'alexa_sonos'
# Paths & Directories
env.root_path = '/lingobee/data/www/'
env.directories = {
    'media': None, 'static': None, 'logs': None,
}

# Users
env.user = 'jamie'
env.sudo_user = 'root'

# Version Control
env.scm = 'git'


# Hosts to deploy too
env.hosts = [
    'lingobee.com'
]


def bootstrap():
    _bootstrap()
