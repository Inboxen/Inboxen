##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.core.paginator import InvalidPage

def look_back(paginator, limit=None):
    try:
        previous = paginator.previous_page_number()
    except InvalidPage:
        return []

    previous = [
        {
            "page":previous,
            "active":False,
        }
    ]

    if limit == 1:
        return previous
    
    return look_back(
        paginator.paginator.page(previous[0]["page"]), 
        limit-1,
    ) + previous

def look_forward(paginator, limit=None):
    try:
        n = paginator.next_page_number()
    except InvalidPage:
        return []

    n = [
            {
                "page":n,
                "active":False,
            }
    ]

    if limit == 1:
        return n

    return n + look_forward(
        paginator.paginator.page(n[0]["page"]),
        limit-1,
    )

def page(paginator):
    pages = []

    if paginator.has_previous():
        pages += look_back(paginator, 2)
    
    pages += [
        {
            "page":paginator.number,
            "active":True,
        }
    ]

    if paginator.has_next():
        pages += look_forward(paginator, 2)



    return pages
