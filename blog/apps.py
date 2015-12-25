##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
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

from django.apps import AppConfig
from django.db.models.signals import pre_save

from blog import signals


class BlogConfig(AppConfig):
    name = "blog"
    verbose_name = "Inboxen Blog"

    def ready(self):
        BlogPost = self.get_model("BlogPost")
        pre_save.connect(signals.published_checker, sender=BlogPost, dispatch_uid="blog_date_draft_checker")
