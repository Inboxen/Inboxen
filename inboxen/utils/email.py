##
#    Copyright (C) 2014-2016 Jessica Tallon & Matt Molyneaux
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

from __future__ import print_function

import re
import logging

from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import html as html_utils, safestring
from django.utils.translation import ugettext as _
import six

from lxml import etree, html as lxml_html
from lxml.html.clean import Cleaner
from premailer.premailer import Premailer

from redirect import proxy_url


HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')

HTML_SAFE_ATTRS = ["style", "title", "href", "src", "height", "width"]

HTML_ALLOW_TAGS = ["p", "a", "i", "b", "em", "strong", "ol", "ul", "li", "pre",
                   "code", "img", "div", "span", "table", "tr", "th", "td",
                   "thead", "tbody", "tfooter", "br"]


_log = logging.getLogger(__name__)


class InboxenPremailer(Premailer):
    def _load_external(self, url):
        """Don't load external resources"""
        return ""


def unicode_damnit(data, charset="utf-8", errors="replace"):
    """Makes doubley sure that we can turn the database's binary typees into
    six.text_type objects
    """
    if isinstance(data, six.text_type):
        return data
    elif data is None:
        return u""

    try:
        return six.text_type(six.binary_type(data), charset, errors)
    except LookupError:
        return six.text_type(six.binary_type(data), "ascii", errors)


def _clean_html_body(request, email, body, charset):
    """Clean up a html part as best we can

    Doesn't catch LXML errors
    """
    html_tree = lxml_html.fromstring(body)

    # if the HTML doc says its a different encoding, use that
    for meta_tag in html_tree.xpath("/html/head/meta"):
        if meta_tag.get("http-equiv", None) == "Content-Type":
            try:
                content = meta_tag.attrib["content"]
                content = content.split(";", 1)[1]
                charset = dict(HEADER_PARAMS.findall(content))["charset"]
                break
            except (KeyError, IndexError):
                pass
        elif "charset" in meta_tag.attrib:
            charset = meta_tag.attrib["charset"]
            break

    try:
        # check there's a body for premailer
        if html_tree.find("body") is not None:
            html_tree = InboxenPremailer(html_tree).transform()
    except Exception as exc:
        # Yeah, a pretty wide catch, but Premailer likes to throw up everything and anything
        messages.info(request, _("Part of this message could not be parsed - it may not display correctly"))
        _log.warning("Failed to render CSS for %s: %s", email["eid"], exc)

    # Mail Pile uses this, give back if you come up with something better
    cleaner = Cleaner(
        allow_tags=HTML_ALLOW_TAGS,
        kill_tags=["style"],  # remove style tags, not attrs
        remove_unknown_tags=False,
        safe_attrs=HTML_SAFE_ATTRS,
        safe_attrs_only=True,
        style=False,  # keep style attrs
    )

    html_tree = cleaner.clean_html(html_tree)

    # filter images if we need to
    if not email["display_images"]:
        for img in html_tree.xpath("//img"):
            try:
                # try to delete src first - we don't want to add a src where there wasn't one already
                del img.attrib["src"]
                # replace image with 1px png
                img.attrib["src"] = staticfiles_storage.url("imgs/placeholder.svg")
                email["has_images"] = True
            except KeyError:
                pass

    for link in html_tree.xpath("//a"):
        try:
            # proxy link
            url = link.attrib["href"]
            link.attrib["href"] = proxy_url(url)
        except KeyError:
            pass

        # open link in tab
        link.attrib["target"] = "_blank"
        # and prevent window.opener bug (noopener is only supported in newer
        # browsers, plus we already set noreferrer in the head)
        link.attrib["rel"] = "noreferrer"

    # finally, export to unicode
    body = unicode_damnit(etree.tostring(html_tree, method="html"), charset)
    return safestring.mark_safe(body)


def render_body(request, email, attachments):
    """Updates `email` with the correct body"""
    plain_message = True
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
        plain_message = not request.user.inboxenprofile.prefer_html_email
    # which ever has the lower lft value will win
    elif html.lft < plain.lft:
        plain_message = False
    else:  # html.lft > plain.lft
        plain_message = True

    # finally, set the body to something
    if plain_message:
        if plain is not None:
            body = unicode_damnit(plain.body.data, plain.charset)
        elif len(attachments) == 1:
            # non-MIME email, only "part" must be plain text
            body = unicode_damnit(attachments[0].body.data, attachments[0].charset)
        else:
            body = u""
    else:
        try:
            body = _clean_html_body(request, email, six.binary_type(html.body.data), html.charset)
        except (etree.LxmlError, ValueError) as exc:
            if plain is not None and len(plain.body.data) > 0:
                body = unicode_damnit(plain.body.data, plain.charset)
            else:
                body = u""

            plain_message = True
            messages.error(request, _("Some parts of this email contained invalid HTML and could not be displayed"))
            _log.warning("Failed to render HTML for %s: %s", email["eid"], exc)

    if plain_message:
        # if this is a plain text body, escape any HTML and wrap it in <pre>
        # tags
        body = html_utils.escape(body)
        body = u"<pre>{}</pre>".format(body)
        body = safestring.mark_safe(body)

    return body


def is_leaf_text_node(part):
    """Check that a suspected text part is actually a leaf node and is of the
    correct mime type
    """
    content_type = part.content_type
    main = ""
    sub = ""

    if u"/" in content_type:
        main, sub = content_type.split("/", 1)

    return part.is_leaf_node() and main == "text" and sub in ["html", "plain"]


def find_bodies(part):
    """Find bodies that should be displayed to the user

    Generator that returns lists of sibling parts. Sibling parts should not be
    displayed together, but are alternatives to eachother, e.g.:

        >>> print([i for i in find_bodies(root_part)])
        [[part1], [html_part2, plain_part2], [part3]]

    Where part1 and part2 might be children of "multipart/mixed" (and they're
    the only "text/" parts), and html_part2 and plain_part2 are siblings from a
    single "multipart/alternative".
    """
    try:
        main, sub = part.content_type.split("/", 1)
    except ValueError:
        # if there isn't a content type and it's the root part, then this is a
        # plain email
        if part.is_leaf_node() and part.get_level() == 0:
            yield [part]
            return
        # whether or not this is the root part, return now as there's nothing
        # left to process
        yield []
        return
    except AttributeError:
        yield []
        return

    if main == "multipart":
        if sub == "alternative":
            # multipart/alternatives should be chosen later
            yield [child for child in part.get_children() if is_leaf_text_node(child)]
            return

        # other multiple parts need their sub trees walked before we can render
        # anything
        for child in part.get_children():
            for returned_child in find_bodies(child):
                yield returned_child
    elif part.parent and part.parent.content_type == "multipart/digest":
        # we must be a message/rfc822, There should only be one child, which is
        # either a text/ part or a multipart/signed
        if len(part.get_children()) == 1:
            child = part.get_children()[0]
            if child.content_type == "multipart/signed":
                # signed messages will have at least two children, the
                # signature and some other child if that child is a leaf text
                # node, we should display it
                yield [grandchild for grandchild in child.get_children() if is_leaf_text_node(grandchild)]
            elif is_leaf_text_node(child):
                yield [child]
    elif is_leaf_text_node(part):
        # part is a leaf node and has a content type that we can display
        yield [part]
        return


def print_tree(part, func=lambda x: str(x)):
    """Pretty print a Mime tree

    For debugging emails

    func should be a callable that accepts a PartList object as its only
    argument and returns a string
    """
    indent = "\t" * part.get_level()
    print("{}{}".format(indent, func(part)))

    for child in part.get_children():
        print_tree(child, func)
