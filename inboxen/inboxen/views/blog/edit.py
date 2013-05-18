##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##

from datetime import datetime
from pytz import utc

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test


from inboxen.models import BlogPost

@user_passes_test(lambda user:user.is_staff, login_url='/user/login/')
def edit(request, postid):

	error = ""

	try:
		post = BlogPost.objects.get(id=postid)
	except BlogPost.DoesNotExist:
		return HttpResponseRedirect("/blog/")

	if request.method == "POST":
		if not ("subject" in request.POST or "body" in request.POST):
			error = "You need to specify the subject and body of the post"
		else:
			post.subject = request.POST["subject"]
			post.body = request.POST["body"]
			#post.modified = datetime.now(utc)
			post.save()

			return HttpResponseRedirect("/blog/")

	context = {
		"error":error,
		"page":post.subject,
		"post":post,
	}

	return render(request, "blog/edit.html", context)
