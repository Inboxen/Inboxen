##
#
# Copyright 2013 Jessica Tallon, Matt Molyneaux
# 
# This file is part of Inboxen.
#
# Inboxen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Inboxen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
#
##

from inboxen.models import Alias, Domain

def alias_exists(alias, domain):
    if Alias.objects.filter(alias=alias, domain__domain=domain, deleted=False).exists():
        return (True, False)
    elif Alias.objects.filter(alias=alias, domain__domain=domain).exists():
        return (False, True)
    else:
        return (False, False)

def domain_exists(domain):
    if Domain.objects.filter(domain=domain).exists():
        return True
    else:
        return False
