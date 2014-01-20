# This file contains python variables that configure Salmon for email processing.
import sys
import os

DEBUG = False

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

reject_dir = "run/rejected"
queue_opts = {}

receiver_config = {'host': 'localhost', 'port': 8823}

in_handlers = ['app.handlers.in']

router_defaults = {}

template_config = {'dir': 'app', 'module': 'templates'}

