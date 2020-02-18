##
#    Copyright (C) 2020 Jessica Tallon & Matt Molyneaux
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

import copy


def setdefault_deep(cfg, defaults):
    if cfg is None:
        return copy.deepcopy(defaults)
    for key, value in defaults.items():
        if isinstance(value, dict):
            cfg[key] = setdefault_deep(cfg.get(key), value)
        else:
            cfg.setdefault(key, value)

    return cfg
