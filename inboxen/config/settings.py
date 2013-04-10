# This file contains python variables that configure Lamson for email processing.
import logging
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'frontend.settings'

accepted_queue_dir = 'run/accepted'
accepted_queue_opts = {'safe': False, 'oversize_dir': None}

receiver_config = {'host': 'localhost', 'port': 8823}

out_handlers = ['app.handlers.out']
in_handlers = ['app.handlers.in']

router_defaults = {'host': 'localhost'}

template_config = {'dir': 'app', 'module': 'templates'}

# the config/boot.py will turn these values into variables set in settings
