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

from markdown import markdown

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext as _

from inboxen.models import BlogPost


class RssFeed(Feed):
    title = "{0} News Feed".format(settings.SITE_NAME)
    feed_url = reverse_lazy('blog-feed-rss')
    link = reverse_lazy('blog')

    def items(self):
        return BlogPost.objects.filter(draft=False).order_by('-date')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return markdown(item.body)

    def item_link(self, item):
        return reverse('blog-post', kwargs={"postid": item.id})

    def description(self):
        return _("The latest news and updates for {0}").format(settings.SITE_NAME)

class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
    feed_url = reverse_lazy('blog-feed-atom')
