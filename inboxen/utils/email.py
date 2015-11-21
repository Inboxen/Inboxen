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
"""This module contains domain logic (as opposed to data logic found in
models.py) for emails

It's in "utils" because "domain.py" would get confusing :P """

import re
import logging

from django.utils.translation import ugettext as _
from django.contrib import messages

from lxml import etree, html as lxml_html
from lxml.html.clean import Cleaner
from premailer.premailer import Premailer

from redirect import proxy_url


HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')

_log = logging.getLogger(__name__)


def _unicode_damnit(data, charset="utf-8", errors="replace"):
    """Makes doubley sure that we can turn the database's binary typees into
    unicode objects
    """
    if isinstance(data, unicode):
        return data

    return unicode(str(data), charset, errors)


def _clean_html_body(request, email, body, charset):
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
    return _unicode_damnit(etree.tostring(html_tree), charset)


def _render_body(request, email, attachments):
    """Updates `email` with the correct body
    """
    plain_message = True
    ask_images = False

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
        plain_message = True
    elif html is None:
        plain_message = True
    elif plain is None:
        plain_message = False
    elif html.parent_id == plain.parent_id:
        # basically multiple/alternative
        plain_message = not request.user.userprofile.flags.prefer_html_email
    # which ever has the lower lft value will win
    elif html.lft < plain.lft:
        plain_message = False
    else:  # html.lft > plain.lft
        plain_message = True

    # finally, set the body to something
    if plain_message:
        if plain:
            body = _unicode_damnit(plain.body.data, plain.charset)
        elif len(attachments) == 1:
            body = _unicode_damnit(attachments[0].body.data, attachments[0].charset)
        else:
            body = u""

        ask_images = False
    else:
        try:
            body = _clean_html_body(request, email, str(html.body.data), html.charset)
        except (etree.LxmlError, ValueError) as exc:
            if plain is not None and len(plain.body.data) > 0:
                body = _unicode_damnit(plain.body.data, plain.charset)
            else:
                body = u""

            plain_message = True
            ask_images = False
            messages.error(request, _("Some parts of this email contained invalid HTML and could not be displayed"))
            _log.exception(exc)

    if plain_message:
        body = u"<pre>{}</pre>".format(body)

    if ask_images:
        email["ask_images"] = True

    return body


def find_bodies(request, email, attachments, depth=0):
    """Find bodies that should be inlined and add them to email["bodies"]

    `attachments` should a list like object (i.e. have the method `index`)"""
    for part in attachments:
        try:
            main, sub = part.content_type.split("/", 1)
        except ValueError:
            if len(attachments) == 1 and depth == 0:
                email["bodies"] = [_render_body(request, email, attachments)]
            return
        if part.parent:
            parent_main, parent_sub = part.parent.content_type.split("/", 1)
        else:
            parent_main, parent_sub = ("", "")

        if main == "multipart":
            if sub == "alternative":
                email["bodies"].append(_render_body(request, email, part.childs))
                continue
            find_bodies(request, email, part.childs, depth=depth+1)
        elif part.parent and part.parent.content_type == "multipart/digest":
            if len(part.childs) == 1:
                email["bodies"].append(_render_body(request, email, part.childs))
        elif part.is_leaf_node() and main == "text" and sub in ["html", "plain"]:
            email["bodies"].append(_render_body(request, email, [part]))
