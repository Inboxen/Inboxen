##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

import os
import stat

from django.conf import settings
from django.core import exceptions
from django.core.checks import Error, Tags, register

from inboxen.models import Domain

PERMISSION_ERROR_MSG = "Other users could be able to interact with your settings file.\
 Please check file permissions on {}".format(settings.CONFIG_PATH)

DOMAIN_ERROR_MSG = "No domains available. Add one via the createdomain command."


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
            Error(PERMISSION_ERROR_MSG)
        ]
    else:
        return []


@register(Tags.models, deploy=True)
def domains_available_check(app_configs, **kwargs):
    errors = []
    available = Domain.objects.available(None).exists()
    if not available:
        errors.append(Error(DOMAIN_ERROR_MSG))

    return errors
