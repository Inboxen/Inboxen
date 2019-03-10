##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
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

from datetime import timedelta
from importlib import import_module
import gc
import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Avg, Case, Count, F, Max, Min, StdDev, Sum, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from watson import search as watson_search

from inboxen import models
from inboxen.celery import app
from inboxen.utils.tasks import task_group_skew

log = logging.getLogger(__name__)


@app.task(ignore_result=True)
@transaction.atomic()
def statistics():
    """Gather statistics about users and their inboxes"""
    try:
        last_stat = models.Statistic.objects.latest("date")
    except models.Statistic.DoesNotExist:
        last_stat = None

    # the keys of these dictionaries have awful names for historical reasons
    # don't change them unless you want to do a data migration
    one_day_ago = timezone.now() - timedelta(days=1)
    user_aggregate = {
        "count": Count("id", distinct=True),
        "new": Coalesce(Count(
            Case(
                When(date_joined__gte=one_day_ago, then=F("id")),
            ),
            distinct=True,
        ), 0),
        "oldest_user_joined": Min("date_joined"),
        "with_inboxes": Coalesce(Count(
            Case(
                When(inbox__isnull=False, then=F("id")),
            ),
            distinct=True,
        ), 0),
    }

    inbox_aggregate = {
        "inbox_count__avg": Coalesce(Avg("inbox_count"), 0),
        "inbox_count__max": Coalesce(Max("inbox_count"), 0),
        "inbox_count__min": Coalesce(Min("inbox_count"), 0),
        "inbox_count__stddev": Coalesce(StdDev("inbox_count"), 0),
        "inbox_count__sum": Coalesce(Sum("inbox_count"), 0),
    }

    email_aggregate = {
        "email_count__avg": Coalesce(Avg("email_count"), 0),
        "email_count__max": Coalesce(Max("email_count"), 0),
        "email_count__min": Coalesce(Min("email_count"), 0),
        "email_count__stddev": Coalesce(StdDev("email_count"), 0),
        "email_count__sum": Coalesce(Sum("email_count"), 0),
    }

    # collect user and inbox stats
    users = get_user_model().objects.aggregate(**user_aggregate)
    inboxes = get_user_model().objects.annotate(inbox_count=Count("inbox__id")).aggregate(**inbox_aggregate)

    domain_count = models.Domain.objects.available(None).count()
    inboxes_possible = len(settings.INBOX_CHOICES) ** settings.INBOX_LENGTH

    inboxes["total_possible"] = inboxes_possible * domain_count

    # collect email state
    inbox_qs = models.Inbox.objects.exclude(deleted=True).annotate(email_count=Count("email__id"))
    emails = inbox_qs.aggregate(**email_aggregate)

    inboxes["with_emails"] = inbox_qs.exclude(email_count=0).count()
    inboxes["disowned"] = models.Inbox.objects.filter(user__isnull=True).count()
    emails["emails_read"] = models.Email.objects.filter(read=True).count()

    if last_stat:
        email_diff = (emails["email_count__sum"] or 0) - (last_stat.emails["email_count__sum"] or 0)
        emails["running_total"] = last_stat.emails["running_total"] + max(email_diff, 0)
    else:
        emails["running_total"] = emails["email_count__sum"] or 0

    stat = models.Statistic(
        users=users,
        emails=emails,
        inboxes=inboxes,
    )

    stat.save()

    log.info("Saved statistics (%s)", stat.date)


@app.task(ignore_result=True)
def clean_expired_session():
    """Clear expired sessions"""
    engine = import_module(settings.SESSION_ENGINE)

    try:
        engine.SessionStore.clear_expired()
    except NotImplementedError:
        log.info("%s does not implement clear_expired", settings.SESSION_ENGINE)


@app.task(ignore_result=True)
@transaction.atomic()
def inbox_new_flag(user_id, inbox_id=None):
    emails = models.Email.objects.order_by("-received_date")
    emails = emails.filter(inbox__user__id=user_id, inbox__exclude_from_unified=False)
    if inbox_id is not None:
        emails = emails.filter(inbox__id=inbox_id)
    emails = list(emails.values_list("id", flat=True)[:100])  # number of emails on page
    emails = models.Email.objects.filter(id__in=emails, seen=False)

    if emails.count() > 0:
        # if some emails haven't been seen yet, we have nothing else to do
        return
    elif inbox_id is None:
        profile = models.UserProfile.objects.get_or_create(user_id=user_id)[0]
        profile.unified_has_new_messages = False
        profile.save(update_fields=["unified_has_new_messages"])
    else:
        with watson_search.skip_index_update():
            inbox = models.Inbox.objects.get(user__id=user_id, id=inbox_id)
            inbox.new = False
            inbox.save(update_fields=["new"])


@app.task(ignore_result=True)
def deal_with_flags(email_id_list, user_id, inbox_id=None):
    """Set seen flags on a list of email IDs and then send off tasks to update
    "new" flags on affected Inbox objects
    """
    with transaction.atomic():
        with watson_search.skip_index_update():
            # update seen flags
            models.Email.objects.filter(id__in=email_id_list).update(seen=True)

    if inbox_id is None:
        # grab affected inboxes
        inbox_list = models.Inbox.objects.filter(user__id=user_id, email__id__in=email_id_list)
        inbox_list = inbox_list.distinct()

        for inbox in inbox_list:
            inbox_new_flag.delay(user_id, inbox.id)
    else:
        # we only need to update
        inbox_new_flag.delay(user_id)


@app.task(ignore_result=True)
def force_garbage_collection():
    """Call the garbage collector.

    This task expects to be sent to a broadcast queue
    """
    collected = gc.collect()

    log.info("GC collected {0} objects.".format(collected))


@app.task(rate_limit=500)
@transaction.atomic()
def delete_inboxen_item(model, item_pk):
    _model = apps.get_app_config("inboxen").get_model(model)

    try:
        item = _model.objects.only('pk').get(pk=item_pk)
        item.delete()
    except (IntegrityError, _model.DoesNotExist):
        pass


@app.task(rate_limit="1/m")
@transaction.atomic()
def batch_delete_items(model, args=None, kwargs=None, skip_items=None, limit_items=None, batch_number=500):
    """If something goes wrong and you've got a lot of orphaned entries in the
    database, then this is the task you want.

    Be aware: this task pulls a list of PKs from the database which may cause
    increased memory use in the short term.

    * model is a string
    * args and kwargs should be obvious
    * batch_number is the number of delete tasks that get sent off in one go
    """
    _model = apps.get_app_config("inboxen").get_model(model)

    if args is None and kwargs is None:
        raise Exception("You need to specify some filter options!")
    elif args is None:
        args = []
    elif kwargs is None:
        kwargs = {}

    items = _model.objects.only('pk').filter(*args, **kwargs)
    items = [(model, item.pk) for item in items.iterator()]
    if skip_items is not None:
        items = items[skip_items:]
    if limit_items is not None:
        items = items[:limit_items]
    if len(items) == 0:
        return

    items = delete_inboxen_item.chunks(items, batch_number).group()
    task_group_skew(items, step=batch_number/10.0)
    items.apply_async()


@app.task(rate_limit="1/h")
def clean_orphan_models():
    # Body
    batch_delete_items.delay("body", kwargs={"partlist__isnull": True})

    # HeaderName
    batch_delete_items.delay("headername", kwargs={"header__isnull": True})

    # HeaderData
    batch_delete_items.delay("headerdata", kwargs={"header__isnull": True})


@app.task(rate_limit="1/h")
def auto_delete_emails():
    batch_delete_items.delay("email", kwargs={
        "inbox__user__inboxenprofile__auto_delete": True,
        "received_date__lt": timezone.now() - timedelta(days=settings.INBOX_AUTO_DELETE_TIME),
        "important": False,
    })


@app.task(rate_limit="1/h")
def calculate_quota(batch_number=500):
    if not settings.PER_USER_EMAIL_QUOTA:
        return

    users = get_user_model().objects.only("pk")

    user_tasks = calculate_user_quota.chunks([(i.pk,) for i in users.iterator()], batch_number).group()
    if len(user_tasks) == 0:
        return

    task_group_skew(user_tasks, step=batch_number/10.0)
    user_tasks.delay()


@app.task
def calculate_user_quota(user_id):
    if not settings.PER_USER_EMAIL_QUOTA:
        return

    try:
        profile = get_user_model().objects.get(id=user_id).inboxenprofile
    except get_user_model().DoesNotExist:
        return

    email_count = models.Email.objects.filter(inbox__user_id=user_id).count()

    profile.quota_percent_usage = min((email_count * 100) / settings.PER_USER_EMAIL_QUOTA, 100)
    profile.save(update_fields=["quota_percent_usage"])

    if profile.quota_options == profile.DELETE_MAIL and email_count > settings.PER_USER_EMAIL_QUOTA:
        batch_delete_items.delay("email", kwargs={"important": False, "inbox__user_id": user_id},
                                 skip_items=settings.PER_USER_EMAIL_QUOTA)
