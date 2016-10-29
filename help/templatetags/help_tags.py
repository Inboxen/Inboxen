from django import template

from help.utils import app_reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def app_url(context, viewname, *args, **kwargs):
    request = context['request']

    return app_reverse(request.page, request.site, viewname, args, kwargs)
