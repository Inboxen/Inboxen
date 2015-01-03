##
#    Copyright (C) 2013-2015 Jessica Tallon & Matt Molyneaux
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

import re

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views import generic

from lxml import etree, html as lxml_html
from lxml.html.clean import Cleaner
from premailer.premailer import Premailer
import watson

from inboxen import models
from website.views import base

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')

__all__ = ["EmailView"]


def unicode_damnit(data, charset="utf-8", errors="replace"):
    """Makes doubley sure that we can turn the database's binary typees into
    unicode objects
    """
    if isinstance(data, unicode):
        return data

    return unicode(str(data), charset, errors)


class EmailView(base.CommonContextMixin, base.LoginRequiredMixin, generic.DetailView):
    model = models.Email
    pk_url_kwarg = "id"
    template_name = 'inbox/email.html'

    def get(self, *args, **kwargs):

        with watson.skip_index_update():
            out = super(EmailView, self).get(*args, **kwargs)
            if "all-headers" in self.request.GET:
                self.object.flags.view_all_headers = bool(int(self.request.GET["all-headers"]))

            self.object.flags.read = True
            self.object.flags.seen = True
            self.object.save(update_fields=["flags"])
        return out

    def get_object(self, *args, **kwargs):
        # Convert the id from base 16 to 10
        self.kwargs[self.pk_url_kwarg] = int(self.kwargs[self.pk_url_kwarg], 16)
        return super(EmailView, self).get_object(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        queryset = super(EmailView, self).get_queryset(*args, **kwargs)
        queryset = queryset.filter(
            inbox__user=self.request.user,
            inbox__inbox=self.kwargs["inbox"],
            inbox__domain__domain=self.kwargs["domain"],
            flags=~models.Email.flags.deleted
            ).select_related("inbox", "inbox__domain")
        return queryset

    def get_success_url(self):
        return self.request.path

    def post(self, *args, **kwargs):
        obj = self.get_object()

        if "important-toggle" in self.request.POST:
            with watson.skip_index_update():
                obj.flags.important = not bool(obj.flags.important)
                obj.save(update_fields=["flags"])

        return HttpResponseRedirect(self.get_success_url())

    def find_body(self, html, plain):
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
            return not self.request.user.userprofile.flags.prefer_html_email
        # which ever has the lower lft value will win
        elif html.lft < plain.lft:
            return False
        else:  # html.lft > plain.lft
            return True

    def get_context_data(self, **kwargs):
        if "all-headers" in self.request.GET:
            headers = None
            headers_fetch_all = bool(int(self.request.GET["all-headers"]))
        else:
            headers = cache.get(self.object.id, version="email-header")
            headers_fetch_all = bool(self.object.flags.view_all_headers)

        if headers is None:
            headers = models.Header.objects.filter(part__email=self.object, part__parent=None)
            if headers_fetch_all:
                headers = headers.get_many()
            else:
                headers = headers.get_many("Subject", "From")

        email_dict = {}
        email_dict["headers"] = headers
        email_dict["date"] = self.object.received_date
        email_dict["inbox"] = self.object.inbox
        email_dict["eid"] = self.object.eid

        # iterate over MIME parts
        html = None
        plain = None
        attachments = []
        for part in self.object.parts.all():
            part_head = part.header_set.get_many("Content-Type", "Content-Disposition")
            part_head["content_type"] = part_head.pop("Content-Type", "").split(";", 1)
            dispos = part_head.pop("Content-Disposition", "")

            if part_head["content_type"][0].startswith("multipart") or part_head["content_type"][0].startswith("message"):
                continue

            try:
                params = dict(HEADER_PARAMS.findall(part_head["content_type"][1]))
            except IndexError:
                params = {}
            params.update(dict(HEADER_PARAMS.findall(dispos)))

            # find filename, could be anywhere
            if "filename" in params:
                part_head["filename"] = params["filename"]
            elif "name" in params:
                part_head["filename"] = params["name"]
            else:
                part_head["filename"] = ""

            # grab charset
            part.charset = params.get("charset", "utf-8")

            if html is None and part_head["content_type"][0] == "text/html":
                html = part
            elif plain is None and part_head["content_type"][0] == "text/plain":
                plain = part

            attachments.append((part, part_head))

        # set raw body
        plain_message = self.find_body(html, plain)
        if plain_message is None:
            if len(attachments) == 1:
                email_dict["body"] = unicode_damnit(attachments[0][0].body.data, attachments[0][0].charset)
            else:
                email_dict["body"] = u""
            plain_message = True
        elif plain_message:
            email_dict["body"] = unicode_damnit(plain.body.data, plain.charset)
        else:
            email_dict["body"] = str(html.body.data)

        # default to not asking - no images in plain text emails
        ask_images = False

        if not plain_message:
            try:
                # anything in this try block could raise an exception that would require us
                # to display an error and present the plain text part of a message
                html_tree = lxml_html.fromstring(email_dict["body"])
                charset = html.charset

                # if the HTML doc says its a different encoding, use that
                for meta_tag in html_tree.xpath("/html/head/meta"):
                    if meta_tag.get("http-equiv", None) is "Content-Type":
                        content = meta_tag.get("content")
                        content = content.split(";", 1)[1]
                        charset = dict(HEADER_PARAMS.finall(content)).get("charset", html.charset)
                        break
                    elif meta_tag.get("charset", None) is not None and meta_tag.get("charset", None) is not "":
                        charset = meta_tag.get("charset")
                        break

                # GET params for users with `ask_image` set in their profile
                if "imgDisplay" in self.request.GET and int(self.request.GET["imgDisplay"]) == 1:
                    img_display = True
                elif self.request.user.userprofile.flags.ask_images:
                    img_display = False
                    ask_images = True
                else:
                    img_display = self.request.user.userprofile.flags.display_images

                # filter images if we need to
                if not img_display:
                    for img in html_tree.xpath("//img"):
                        try:
                            del img.attrib["src"]
                        except KeyError:
                            pass

                try:
                    html_tree = Premailer(html_tree).transform()
                except Exception:
                    # Yeah, a pretty wide catch, but Premailer likes to throw up everything and anything
                    messages.info(self.request, _("Part of this message could not be parsed - it may not display correctly"))

                # Mail Pile uses this, give back if you come up with something better
                cleaner = Cleaner(page_structure=True, meta=True, links=True, javascript=True,
                                scripts=True, frames=True, embedded=True, safe_attrs_only=True)
                cleaner.kill_tags = [
                    "style",  # remove style tags, not attrs
                    "base",
                ]

                html_tree = cleaner.clean_html(html_tree)

                email_dict["body"] = unicode_damnit(etree.tostring(html_tree), charset)
            except (etree.LxmlError, ValueError):
                if plain is not None and len(plain.body.data) > 0:
                    email_dict["body"] = unicode_damnit(plain.body.data, plain.charset)
                else:
                    email_dict["body"] = u""

                plain_message = True
                ask_images = False
                messages.error(self.request, _("This email contained invalid HTML and could not be displayed"))

        self.headline = email_dict["headers"].get("Subject", _("No Subject"))

        assert isinstance(email_dict["body"], unicode), "body is %r" % type(email_dict["body"])

        context = super(EmailView, self).get_context_data(**kwargs)
        context.update({
                        "email": email_dict,
                        "plain_message": plain_message,
                        "attachments": attachments,
                        "ask_images": ask_images,
                        "headersfetchall": headers_fetch_all,
                        })

        return context
