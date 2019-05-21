##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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

import ipaddress

IPV4_HOST_CLASS = 32
IPV6_HOST_CLASS = 64


def strip_ip(ip, ipv4_host_class=IPV4_HOST_CLASS, ipv6_host_class=IPV6_HOST_CLASS):
    """Strip an IP address back to the largest routable part

    For IPv4, this is the full 32 bits. For IPv6 this is the first 64 bits.
    """
    ip = ipaddress.ip_address(str(ip))

    if isinstance(ip, ipaddress.IPv4Address):
        netmask = ip.max_prefixlen - ipv4_host_class
    elif isinstance(ip, ipaddress.IPv6Address):
        netmask = ip.max_prefixlen - ipv6_host_class
    else:
        raise ValueError("Not an IPv4 and IPv6 address")

    prefix = int(ip) & ~((1 << netmask) - 1)
    prefix = ipaddress.ip_address(prefix)

    return str(prefix)
