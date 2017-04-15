##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings, urls

from wagtail.wagtailcore import hooks

from cms.views import user_editing_disabled_view


@hooks.register('before_serve_page')
def set_page_on_request(page, request, serve_args, serve_kwargs):
    request.page = page


@hooks.register('construct_main_menu')
def remove_user_menu_items(request, menu_items):
    if settings.ENABLE_USER_EDITING:
        return  # don't remove anything

    for item in menu_items:
        if item.name == "settings":
            for sub_item in item.menu.registered_menu_items[:]:
                if sub_item.name in ["users", "groups"]:
                    idx = item.menu.registered_menu_items.remove(sub_item)


@hooks.register('register_admin_urls')
def override_user_urls():
    if not settings.ENABLE_USER_EDITING:
        return [
            urls.url(r'^users/', user_editing_disabled_view),
            urls.url(r'^groups/', user_editing_disabled_view),
        ]
