##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from annoying import fields as annoying_fields
from django.db import models


class DeferAutoOneToOneField(annoying_fields.AutoOneToOneField):
    system_check_removed_details = {
        'msg': (
            'The deferring option is no longer needed by Inboxen'
            ' but this field stub is kept for historic migrations'
        ),
        'hint': 'Use AutoOneToOneField instead.',
        'id': 'fields.E945',
    }


class LargeObjectField(models.IntegerField):
    def db_type(self, connection):
        return 'oid'

    system_check_removed_details = {
        'msg': (
            'No longer supported by upstream'
        ),
        'hint': "Don't use this field.",
        'id': 'fields.E946',
    }
