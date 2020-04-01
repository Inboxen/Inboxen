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

from django.apps import apps


def task_group_skew(group, step=1):
    """Work around for https://github.com/celery/celery/issues/4298"""
    group.tasks = list(group.tasks)
    group.skew(step=step)


def create_queryset(model, app="inboxen", args=None, kwargs=None, skip_items=None, limit_items=None):
    """Create queryset from parts that can be JSON serialised"""
    if isinstance(model, str):
        _model = apps.get_app_config(app).get_model(model)
    else:
        _model = model

    if args is None and kwargs is None:
        raise Exception("You need to specify some filter options!")
    elif args is None:
        args = []
    elif kwargs is None:
        kwargs = {}

    items = _model.objects.only('pk').filter(*args, **kwargs)
    if skip_items is not None:
        items = items[skip_items:]
    if limit_items is not None:
        items = items[:limit_items]

    return items
