##
#    Copyright (C) 2013, 2014, 2015 Jessica Tallon & Matt Molyneaux
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

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.db import models

from pytz import utc


def decided_checker(sender, instance=None, **kwargs):
    if instance.date_decided is None and instance.succeeded is not None and instance.authorizer is not None:
        instance.date_decided = datetime.now(utc)
        if instance.succeeded is True:
            profile = instance.requester.inboxenprofile
            profile.pool_amount = models.F("pool_amount") + instance.amount
            profile.save(update_fields=["pool_amount"])
    elif instance.authorizer is None or instance.succeeded is None:
        # either authorizer or succeeded is missing, so we'll bug out
        instance.authorizer = None
        instance.succeeded = None
        instance.date_decided = None


def logout_message(sender, request, **kwargs):
    msg = getattr(request, "_logout_message", settings.LOGOUT_MSG)
    messages.add_message(request, messages.INFO, msg)
