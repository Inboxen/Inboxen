import os
import stat

from django.conf import settings
from django.core.checks import register, Tags, Error
from django.core import exceptions


@register(Tags.security, deploy=True)
def config_permissions_check(app_configs, **kwargs):
    """Check that our chosen settings file cannot be interacted with by other
    users"""
    if settings.CONFIG_PATH == "":
        return []
    try:
        mode = os.stat(settings.CONFIG_PATH).st_mode
    except OSError:
        raise exceptions.ImproperlyConfigured("Could not stat {}".format(settings.CONFIG_PATH))

    if mode & stat.S_IRWXO != 0:
        return [
            Error("Other users could be able to interact with your settings file. Please check file permissions on {}".format(settings.CONFIG_PATH))
        ]
    else:
        return []
