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

from markdown import markdown

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse

from website.models import BlogPost


class RssFeed(Feed):
    title = "Inboxen News Feed"
    link = "/blog/feed/rss"
    feed_link = "http://%s/blog/feed/rss" % settings.ALLOWED_HOSTS[0]
    description = "The latest news and updates for inboxen site"

    def items(self):
        return BlogPost.objects.filter(draft=False).order_by('-date')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return markdown(item.body)

    def item_link(self, item):
        return "/blog/post/%s" % item.id

class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
    link = "/blog/feed/atom"
    feed_link = "http://%s/blog/feed/atom" % settings.ALLOWED_HOSTS[0]
