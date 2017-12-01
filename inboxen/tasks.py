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

from datetime import datetime, timedelta
from importlib import import_module
import gc
import logging
import urllib

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.db.models import Avg, Case, Count, F, Max, Min, StdDev, Sum, When, IntegerField
from django.db.models.functions import Coalesce

from pytz import utc
from watson import search as watson_search

from inboxen import models
from inboxen.celery import app

log = logging.getLogger(__name__)

SEARCH_TIMEOUT = 60 * 30


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
    one_day_ago = datetime.now(utc) - timedelta(days=1)
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
    inbox_qs = models.Inbox.objects.exclude(flags=models.Inbox.flags.deleted).annotate(email_count=Count("email__id"))
    emails = inbox_qs.aggregate(**email_aggregate)

    inboxes["with_emails"] = inbox_qs.exclude(email_count=0).count()
    inboxes["disowned"] = models.Inbox.objects.filter(user__isnull=True).count()
    emails["emails_read"] = models.Email.objects.filter(flags=models.Email.flags.read).count()

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
    emails = emails.filter(inbox__user__id=user_id, inbox__flags=~models.Inbox.flags.exclude_from_unified)
    if inbox_id is not None:
        emails = emails.filter(inbox__id=inbox_id)
    emails = list(emails.values_list("id", flat=True)[:100])  # number of emails on page
    emails = models.Email.objects.filter(id__in=emails, flags=~models.Email.flags.seen)

    if emails.count() > 0:
        # if some emails haven't been seen yet, we have nothing else to do
        return
    elif inbox_id is None:
        profile = models.UserProfile.objects.get_or_create(user_id=user_id)[0]
        profile.flags.unified_has_new_messages = False
        profile.save(update_fields=["flags"])
    else:
        with watson_search.skip_index_update():
            inbox = models.Inbox.objects.get(user__id=user_id, id=inbox_id)
            inbox.flags.new = False
            inbox.save(update_fields=["flags"])


@app.task(ignore_result=True)
def deal_with_flags(email_id_list, user_id, inbox_id=None):
    """Set seen flags on a list of email IDs and then send off tasks to update
    "new" flags on affected Inbox objects
    """
    with transaction.atomic():
        with watson_search.skip_index_update():
            # update seen flags
            models.Email.objects.filter(id__in=email_id_list).update(flags=F('flags').bitor(models.Email.flags.seen))

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
def requests():
    """Check for unresolved Inbox allocation requests"""
    requests = models.Request.objects.filter(succeeded__isnull=True)
    requests = requests.select_related("requester").order_by("-date")
    requests = requests.values("id", "amount", "date", "requester__username", "requester__inboxenprofile__pool_amount")

    if len(requests) == 0:
        return

    output = []

    item_format = "User: {username}\n      Date: {date}\n    Amount: {amount}\n   Current: {current}\n"

    for request in requests:
        item = item_format.format(
            username=request["requester__username"],
            date=request["date"],
            amount=request["amount"],
            current=request["requester__inboxenprofile__pool_amount"]
        )
        output.append(item)

    output = "\n\n".join(output)

    mail.mail_admins("Inbox Allocation Requests", output)


@app.task(rate_limit="100/s")
def search(user_id, search_term):
    """Offload the expensive part of search to avoid blocking the web interface"""
    email_subquery = models.Email.objects.viewable(user_id)
    inbox_subquery = models.Inbox.objects.viewable(user_id)

    results = {
        "emails": list(watson_search.search(search_term, models=(email_subquery,)).values_list("id", flat=True)),
        "inboxes": list(watson_search.search(search_term, models=(inbox_subquery,)).values_list("id", flat=True)),
    }

    key = u"{0}-{1}".format(user_id, search_term)
    key = urllib.quote(key.encode("utf-8"))

    cache.set(key, results, SEARCH_TIMEOUT)

    return results


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
def batch_delete_items(model, args=None, kwargs=None, batch_number=500):
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
    if len(items) == 0:
        return

    items = delete_inboxen_item.chunks(items, batch_number).group()
    items.skew(step=batch_number/10.0)
    items.apply_async()


@app.task(rate_limit="1/h")
def clean_orphan_models():
    # Body
    batch_delete_items.delay("body", kwargs={"partlist__isnull": True})

    # HeaderName
    batch_delete_items.delay("headername", kwargs={"header__isnull": True})

    # HeaderData
    batch_delete_items.delay("headerdata", kwargs={"header__isnull": True})
