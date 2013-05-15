##
#
# Copyright 2013 Jessica Tallon, Matt Molyneaux
# 
# This file is part of Inboxen back-end.
#
# Inboxen back-end is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Inboxen back-end is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inboxen back-end.  If not, see <http://www.gnu.org/licenses/>.
#
##

from lamson.routing import route, stateless, nolocking
from config.settings import DEBUG
from app.model.email import make_email

@route("(alias)@(domain)", alias=".+", domain=".+")
@nolocking
@stateless
def START(message, alias=None, domain=None):

    # alias should have already have been checked before the email entered the
    # queue
    make_email(message, alias, domain)
