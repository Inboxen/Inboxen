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

IPV4_HOST_PREFIX = 32
IPV6_HOST_PREFIX = 64


def strip_ip(ip_addr, ipv4_host_prefix=IPV4_HOST_PREFIX, ipv6_host_prefix=IPV6_HOST_PREFIX):
    """Strip an IP address back to the largest routable part

    For IPv4, this is the full 32 bits. For IPv6 this is the first 64 bits.
    """
    ip = ipaddress.ip_address(ip_addr)
    prefix_len = ip.max_prefixlen

    if isinstance(ip, ipaddress.IPv4Address):
        remove_bits = prefix_len - ipv4_host_prefix
    elif isinstance(ip, ipaddress.IPv6Address):
        remove_bits = prefix_len - ipv6_host_prefix
    else:
        raise ValueError("Not an IPv4 or IPv6 address")

    # the netmask should be a series of 1s for the bits we want to
    # keep followed by 0s for the bits we don't
    netmask = 2**prefix_len - 2**remove_bits
    prefix = int(ip) & netmask
    prefix = ip.__class__(prefix)

    return str(prefix)
