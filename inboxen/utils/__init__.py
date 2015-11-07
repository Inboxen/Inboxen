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
from django.contrib import messages

from django_assets import env as assets_env
from webassets.script import GenericArgparseImplementation
from lxml import etree, html as lxml_html
from lxml.html.clean import Cleaner
from premailer.premailer import Premailer

from inboxen.context_processors import reduced_settings_context
from redirect import proxy_url

# use the following to get a pipe separated list of inboxes that should be reserved
# cat /etc/aliases | egrep "^[^#]" | awk '{gsub (":", ""); print $1}' | sort | tr "\n" "|" | sed 's/|$/\)$\n/' | sed 's/^/\^(/'
RESERVED_LOCAL_PARTS = re.compile(r"""^(abuse|adm|amanda|apache|bin|canna|daemon|dbus|decode|desktop|dovecot|dumper|fax|ftp|ftpadm|ftp-adm|ftpadmin|ftp-admin|games|gdm|gopher|halt|hostmaster|ident|info|ingres|ldap|lp|mail|mailer-daemon|mailnull|manager|marketing|mysql|named|netdump|news|newsadm|newsadmin|nfsnobody|nobody|noc|nscd|ntp|nut|operator|pcap|postfix|postgres|postmaster|privoxy|pvm|quagga|radiusd|radvd|root|rpc|rpcuser|rpm|sales|security|shutdown|smmsp|squid|sshd|support|sync|system|toor|usenet|uucp|vcsa|webalizer|webmaster|wnn|www|xfs)$""")

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')


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

    asset_modules = ["inboxen.assets"]

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


def unicode_damnit(data, charset="utf-8", errors="replace"):
    """Makes doubley sure that we can turn the database's binary typees into
    unicode objects
    """
    if isinstance(data, unicode):
        return data

    return unicode(str(data), charset, errors)


def clean_html_body(request, email, body, charset):
    """Clean up a html part as best we can

    Doesn't catch LXML errors
    """
    html_tree = lxml_html.fromstring(body)

    # if the HTML doc says its a different encoding, use that
    for meta_tag in html_tree.xpath("/html/head/meta"):
        if meta_tag.get("http-equiv", None) is "Content-Type":
            content = meta_tag.get("content")
            content = content.split(";", 1)[1]
            charset = dict(HEADER_PARAMS.finall(content)).get("charset", charset)
            break
        elif meta_tag.get("charset", None) is not None and meta_tag.get("charset", None) is not "":
            charset = meta_tag.get("charset")
            break

    try:
        html_tree = Premailer(html_tree).transform()
    except Exception as exc:
        # Yeah, a pretty wide catch, but Premailer likes to throw up everything and anything
        messages.info(request, _("Part of this message could not be parsed - it may not display correctly"))
        _log.exception(exc)

    # Mail Pile uses this, give back if you come up with something better
    cleaner = Cleaner(page_structure=True, meta=True, links=True, javascript=True,
                    scripts=True, frames=True, embedded=True, safe_attrs_only=True)
    cleaner.kill_tags = [
        "style",  # remove style tags, not attrs
        "base",
    ]

    html_tree = cleaner.clean_html(html_tree)

    # filter images if we need to
    if not email["display_images"]:
        for img in html_tree.xpath("//img"):
            try:
                # try to delete src first - we don't want to add a src where there wasn't one already
                del img.attrib["src"]
                # replace image with 1px png
                img.attrib["src"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
            except KeyError:
                pass

    for link in html_tree.xpath("//a"):
        try:
            # proxy link
            url = link.attrib["href"]
            link.attrib["href"] = proxy_url(url)

            # open link in tab
            link.attrib["target"] = "_blank"
        except KeyError:
            pass

    # finally, export to unicode
    email["body"] = unicode_damnit(etree.tostring(html_tree), charset)


def find_body(request, email, attachments):
    """Updates `email` with the correct body
    """
    html = None
    plain = None

    for part in attachments:
        if part.content_type == "text/html":
            html = part
            break

    for part in attachments:
        if part.content_type == "text/plain":
            plain = part
            break

    # work out what we've got and what to do with it
    if html is None and plain is None:
        # no valid parts found, either has no body or is a non-MIME email
        email["plain_message"] = True
        if len(attachments) == 1:
            email["body"] = unicode_damnit(attachments[0].body.data, attachments[0].charset)
        else:
            email["body"] = u""

        email["ask_images"] = False

        return  # nothing else needs doing
    elif html is None:
        email["plain_message"] = True
    elif plain is None:
        email["plain_message"] = False
    elif html.parent_id == plain.parent_id:
        # basically multiple/alternative
        email["plain_message"] = not request.user.userprofile.flags.prefer_html_email
    # which ever has the lower lft value will win
    elif html.lft < plain.lft:
        email["plain_message"] = False
    else:  # html.lft > plain.lft
        email["plain_message"] = True

    # finally, set the body to something
    if email["plain_message"]:
        email["body"] = unicode_damnit(plain.body.data, plain.charset)
        email["ask_images"] = False
    else:
        try:
            clean_html_body(request, email, str(html.body.data), html.charset)
        except (etree.LxmlError, ValueError) as exc:
            if plain is not None and len(plain.body.data) > 0:
                email["body"] = unicode_damnit(plain.body.data, plain.charset)
            else:
                email["body"] = u""

            email["plain_message"] = True
            email["ask_images"] = False
            messages.error(request, _("This email contained invalid HTML and could not be displayed"))
            _log.exception(exc)
