from django.db import models
from django.core.urlresolvers import RegexURLResolver, reverse

from modelcluster.fields import ParentalKey
from wagtail.wagtailcore import fields, models as wag_models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class HelpIndex(wag_models.Page):
    subpage_types = [
        # all Pages except itself
        'help.HelpPage',
        'help.PeoplePage',
        'help.AppPage',
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(HelpIndex, self).get_context(request, *args, **kwargs)
        context["menu"] = self.get_children().live().public()

        return context


class AppPage(wag_models.Page):
    APP_CHOICES = (
        ("tickets.urls", "Tickets"),
    )
    app = models.CharField(max_length=255, unique=True, choices=APP_CHOICES)

    content_panels = wag_models.Page.content_panels + [
        FieldPanel('app'),
    ]

    parent_page_types = ['help.HelpIndex']
    subpage_types = []

    def route(self, request, path_components):
        resolver = RegexURLResolver(r"^", self.app)
        _, _, url = self.get_url_parts()
        path = request.path[len(url):]
        view, args, kwargs = resolver.resolve(path)

        self._view = view
        return (self, args, kwargs)

    def serve(self, request, *args, **kwargs):
        return self._view(request, *args, **kwargs)

    def reverse(self, viewname, args, kwargs):
        """Gives reverse URL for view name relative to page"""
        return reverse(viewname, urlconf=self.app, args=args, kwargs=kwargs)


class HelpPage(wag_models.Page):
    body = fields.RichTextField(blank=True)

    content_panels = wag_models.Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    parent_page_types = ['help.HelpIndex', 'help.HelpPage']
    subpage_types = ['help.HelpPage']


class PeoplePage(wag_models.Page):
    content_panels = wag_models.Page.content_panels + [
        InlinePanel('people', label="People"),
    ]

    parent_page_types = ['help.HelpIndex']
    subpage_types = []


class PersonInfo(wag_models.Orderable):
    page = ParentalKey(PeoplePage, related_name="people")
    name = models.CharField(max_length=255)
    body = fields.RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel("name"),
        FieldPanel('body', classname="full"),
        ImageChooserPanel('feed_image'),
    ]
