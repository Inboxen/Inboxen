from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from inboxen.models import BlogPost

class RssFeed(Feed):
    title = "Inboxen News Feed"
    link = "/blog/feed/"
    feed_link = "http://inboxen.org/blog/feed"
    description = "The latest news and updates for inboxen site"

    def items(self):
        return BlogPost.objects.all().order_by('-date')

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return item.body

    def item_link(self, item):
        return "/blog/post/%s" % item.id
