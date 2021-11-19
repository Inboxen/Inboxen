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

import re

from lxml.etree import ElementTree
from qrcode.image.svg import SvgPathImage

# use the following to get a pipe separated list of inboxes that should be reserved
# cat /etc/aliases | egrep "^[^#]" | awk '{gsub (":", ""); print $1}' | sort | tr "\n" "|" | sed 's/|$/\n/'
RESERVED_LOCAL_PARTS_REGEX = r"""abuse|adm|amanda|apache|bin|canna|daemon|dbus|decode|desktop|dovecot|dumper|fax|ftp|ftpadm|ftp-adm|ftpadmin|ftp-admin|games|gdm|gopher|halt|hostmaster|ident|info|ingres|ldap|lp|mail|mailer-daemon|mailnull|manager|marketing|mysql|named|netdump|news|newsadm|newsadmin|nfsnobody|nobody|noc|nscd|ntp|nut|operator|pcap|postfix|postgres|postmaster|privoxy|pvm|quagga|radiusd|radvd|root|rpc|rpcuser|rpm|sales|security|shutdown|smmsp|squid|sshd|support|sync|system|tor|usenet|uucp|vcsa|webalizer|webmaster|wnn|www|xfs"""  # noqa: E501
RESERVED_LOCAL_PARTS = re.compile(r"^({})$".format(RESERVED_LOCAL_PARTS_REGEX), re.IGNORECASE)


def is_reserved(inbox):
    """Checks `inbox` against know reserved email addresses (local part)

    Assumes `inbox` has been lowercased
    """
    return RESERVED_LOCAL_PARTS.search(inbox) is not None


class SvgPathImageTagOnly(SvgPathImage):
    def _write(self, stream):
        self._img.append(self.make_path())
        etree = ElementTree(self._img)
        svg = etree.getroot()
        # fix the svg qrcode gives us so we can use it in a html page
        del svg.attrib["width"]
        del svg.attrib["height"]
        svg.attrib["preserveAspectRatio"] = "xMinYMin meet"
        etree.write(stream, encoding="UTF-8")
