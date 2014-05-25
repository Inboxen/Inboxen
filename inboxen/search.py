##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

import watson

class EmailSearchAdapter(watson.SearchAdapter):
    def get_title(self, obj)
        return u"" # return subject

    def get_description(self, obj):
        return u"" # return the body that would be displayed to user (just plain?)

    def get_content(self, obj):
        return u"" # return all text/ bodies?

class TagSearchAdapter(watson.SearchAdapter):
    def get_title(self, obj)
        return obj.tag

    def get_description(self, obj):
        return u""

    def get_content(self, obj):
        return u""
