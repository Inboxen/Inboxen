##
#    Copyright (C) 2013 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings

@login_required
def make_reply(request):

    ## this should set up the reply form just so
    pass

@login_required
@require_POST
def send_reply(request):

    context = {
        "page":_("Contact"),
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    ## magically get the user address we're replying to/from
    alias = "bluh@bluh.com"

    ## grab info from POST and store in both user alias and support alias
    ## (because we want to see what we've said)

