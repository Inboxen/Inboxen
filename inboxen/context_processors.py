##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings

import inboxen


def reduced_settings_context(request):
    """Introduces a reduced set of settings into the context

    This allows access to settings which will often be used
    by the templates but exclude sensative information to such
    as the salt to prevent accidents or bugs in the rest of django
    compromising us.
    """
    reduced_settings = {
        "SITE_NAME": settings.SITE_NAME,
        "ENABLE_REGISTRATION": settings.ENABLE_REGISTRATION,
        "INBOXEN_COMMIT_ID": inboxen.__version__,
        "SOURCE_LINK": settings.SOURCE_LINK,
    }
    return {"settings": reduced_settings}
