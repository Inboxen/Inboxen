from django.db import models
from django.utils.module_loading import import_string

from modelcluster.fields import ParentalKey
from wagtail.wagtailcore import fields, models as wag_models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class HelpIndex(wag_models.Page):
    subpage_types = ['help.HelpPage', 'help.PeoplePage']


class AppPage(wag_models.Page):
    APP_CHOICES = (
        ("Tickets", "tickets"),
    )
    app = models.CharField(max_length=255, choices=APP_CHOICES)

    parent_page_types = ['help.HelpIndex']
    subpage_types = []

    def route(self, request, path):
        module = import_string("{}.urls".format(self.app))
        urls = module.urls

        # resolve view and kwargs
        # TODO
        view, args, kwargs = None

        self._view = view
        return (self, args, kwargs)

    def serve(self, *args, **kwargs):
        return self._view(request, *args, **kwargs)


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
