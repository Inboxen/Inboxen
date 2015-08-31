##
#    Copyright (C) 2014, 2015 Jessica Tallon & Matt Molyneaux
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

import os
import re
import logging
import sys

from django.conf import settings
from django.template import loader, Context
from django import test
from django.utils.translation import ugettext as _

from django_assets import env as assets_env
from webassets.script import GenericArgparseImplementation

from website.context_processors import reduced_settings_context

# use the following to get a pipe separated list of inboxes that should be reserved
# cat /etc/aliases | egrep "^[^#]" | awk '{gsub (":", ""); print $1}' | sort | tr "\n" "|" | sed 's/|$/\)$\n/' | sed 's/^/\^(/'
RESERVED_LOCAL_PARTS = re.compile(r"""^(abuse|adm|amanda|apache|bin|canna|daemon|dbus|decode|desktop|dovecot|dumper|fax|ftp|ftpadm|ftp-adm|ftpadmin|ftp-admin|games|gdm|gopher|halt|hostmaster|ident|info|ingres|ldap|lp|mail|mailer-daemon|mailnull|manager|marketing|mysql|named|netdump|news|newsadm|newsadmin|nfsnobody|nobody|noc|nscd|ntp|nut|operator|pcap|postfix|postgres|postmaster|privoxy|pvm|quagga|radiusd|radvd|root|rpc|rpcuser|rpm|sales|security|shutdown|smmsp|squid|sshd|support|sync|system|toor|usenet|uucp|vcsa|webalizer|webmaster|wnn|www|xfs)$""")


_log = logging.getLogger(__name__)


def generate_maintenance_page():
    """Render maintenance page into static files"""
    template_name = "maintenance.html"
    template = loader.get_template(template_name)

    output_dir = os.path.join(settings.STATIC_ROOT, "pages")
    output_path = os.path.join(output_dir, template_name)
    _log.info("Building maintenance page...")

    context = Context(reduced_settings_context(None))
    context["headline"] = _("Back Soon!")
    rendered = template.render(context)

    try:
        os.mkdir(output_dir, 0711)
    except OSError:
        pass


    output = open(output_path, "w")
    output.write(rendered)
    output.close()


def build_assets():
    """Build assets like ./manage.py assets build does"""
    if settings.ASSETS_AUTO_BUILD:
        return

    env = assets_env.get_env()
    argparser = GenericArgparseImplementation(env=env, no_global_options=False)

    errored = argparser.run_with_argv(["build"]) or 0
    if errored != 0:
        raise Exception("Asset building failed with error cdoe %d" % errored)


def is_reserved(inbox):
    """Checks `inbox` against know reserved email addresses (local part)

    Assumes `inbox` has been lowercased
    """
    return RESERVED_LOCAL_PARTS.search(inbox) is not None


class WebAssetsOverrideMixin(object):
    """Reset Django Assets crap

    Work around for https://github.com/miracle2k/django-assets/issues/44
    """

    asset_modules = ["website.assets"]

    def disable(self, *args, **kwargs):
        ret_value = super(WebAssetsOverrideMixin, self).disable(*args, **kwargs)

        # reset asset env
        assets_env.reset()
        assets_env._ASSETS_LOADED = False

        # unload asset modules so python reimports them
        for module in self.asset_modules:
            try:
                del sys.modules[module]
                __import__(module)
            except (KeyError, ImportError):
                _log.debug("Couldn't find %s in sys.modules", module)

        return ret_value


class override_settings(WebAssetsOverrideMixin, test.utils.override_settings):
    pass


def find_body(user, html, plain):
    """Given a pair of plaintext and html MIME parts, return True or False
    based on whether the body should be plaintext or not. Returns None
    if there is no viable body
    """
    # find if one is None
    if html is None and plain is None:
        return None
    elif html is None:
        return True
    elif plain is None:
        return False

    # parts are siblings, user preference
    if html.parent == plain.parent:
        return not user.userprofile.flags.prefer_html_email
    # which ever has the lower lft value will win
    elif html.lft < plain.lft:
        return False
    else:  # html.lft > plain.lft
        return True
