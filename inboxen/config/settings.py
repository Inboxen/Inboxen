# This file contains python variables that configure Lamson for email processing.
import logging
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'inboxen.settings'

accepted_queue_dir = 'run/accepted'
accepted_queue_opts_in = {}
accepted_queue_opts_out = {}

receiver_config = {'host': 'localhost', 'port': 8823}

out_handlers = ['app.handlers.out']
in_handlers = ['app.handlers.in']

router_defaults = {}

template_config = {'dir': 'app', 'module': 'templates'}

datetime_format = "%Y-%m-%d %H:%M:%S"
recieved_header_name = 'x-lamson-recieved'

# the config/boot.py will turn these values into variables set in settings
