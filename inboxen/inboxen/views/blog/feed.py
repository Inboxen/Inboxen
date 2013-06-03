from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse
from inboxen.models import BlogPost
from markdown import markdown

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
