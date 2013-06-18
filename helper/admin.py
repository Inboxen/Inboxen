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

from datetime import datetime, timedelta

from pytz import utc

from django.contrib.auth.models import User

def statistics():

	# how many users are there?
	users = User.objects.all().count()

	new_users = User.objects.filter(date_joined__gte=datetime.now(utc) - timedelta(days=1)).count()

	active_users = User.objects.filter(last_login__gte=datetime.now(utc) - timedelta(days=1)).count()

	return {
		"users":users,
		"new_users":new_users,
		"active_users":active_users
	}

