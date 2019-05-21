##
#    Copyright (C) 2019 Jessica Tallon & Matt Molyneaux
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

import inspect
import logging

IS_SALMON = inspect.stack()[-1][1].endswith("salmon")


class IsSalmon(logging.Filter):
    def filter(self, record):
        return not IS_SALMON


class IsNotSalmon(logging.Filter):
    def filter(self, record):
        return not IS_SALMON
