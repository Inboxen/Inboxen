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

from django.conf import settings
from django.template import loader
from django_assets import env as assets_env
from webassets.script import GenericArgparseImplementation

from inboxen.context_processors import reduced_settings_context


# use the following to get a pipe separated list of inboxes that should be reserved
# cat /etc/aliases | egrep "^[^#]" | awk '{gsub (":", ""); print $1}' | sort | tr "\n" "|" | sed 's/|$/\n/'
RESERVED_LOCAL_PARTS_REGEX = r"""abuse|adm|amanda|apache|bin|canna|daemon|dbus|decode|desktop|dovecot|dumper|fax|ftp|ftpadm|ftp-adm|ftpadmin|ftp-admin|games|gdm|gopher|halt|hostmaster|ident|info|ingres|ldap|lp|mail|mailer-daemon|mailnull|manager|marketing|mysql|named|netdump|news|newsadm|newsadmin|nfsnobody|nobody|noc|nscd|ntp|nut|operator|pcap|postfix|postgres|postmaster|privoxy|pvm|quagga|radiusd|radvd|root|rpc|rpcuser|rpm|sales|security|shutdown|smmsp|squid|sshd|support|sync|system|tor|usenet|uucp|vcsa|webalizer|webmaster|wnn|www|xfs"""
RESERVED_LOCAL_PARTS = re.compile(r"^({})$".format(RESERVED_LOCAL_PARTS_REGEX), re.IGNORECASE)

_log = logging.getLogger(__name__)


def generate_maintenance_page():
    """Render maintenance page into static files"""
    template_name = "maintenance.html"
    template = loader.get_template("inboxen/%s" % template_name)

    output_dir = os.path.join(settings.STATIC_ROOT, "pages")
    output_path = os.path.join(output_dir, template_name)
    _log.info("Building maintenance page...")

    context = reduced_settings_context(None)
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
        raise Exception("Asset building failed with error code %d" % errored)


def is_reserved(inbox):
    """Checks `inbox` against know reserved email addresses (local part)

    Assumes `inbox` has been lowercased
    """
    return RESERVED_LOCAL_PARTS.search(inbox) is not None
