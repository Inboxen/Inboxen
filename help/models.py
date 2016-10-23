from django.db import models

from wagtail.wagtailcore import fields, models as wag_models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel


class HelpIndex(wag_models.Page):
    subpage_types = ['help.HelpPage']


class HelpPage(wag_models.Page):
    body = fields.RichTextField(blank=True)

    content_panels = wag_models.Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    parent_page_types = ['help.HelpIndex', 'help.HelpPage']
    subpage_types = ['help.HelpPage']
