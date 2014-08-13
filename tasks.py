from datetime import datetime, timedelta
import gc
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F

from celery import task
from pytz import utc
import watson

from inboxen.models import Email, Inbox, Statistic

log = logging.getLogger(__name__)

@task(ignore_result=True)
@transaction.atomic()
def statistics():
    # get user statistics
    user_count = get_user_model().objects.all().count()
    new_count =  get_user_model().objects.filter(date_joined__gte=datetime.now(utc) - timedelta(days=1)).count()
    active_count = get_user_model().objects.filter(last_login__gte=datetime.now(utc) - timedelta(days=7)).count()

    stat = Statistic(
        user_count=user_count,
        new_count=new_count,
        active_count=active_count,
        date=datetime.now(utc),
    )

    stat.save()

    log.info("Saved statistics (%s)", stat.date)


@task(ignore_result=True)
@transaction.atomic()
def inbox_new_flag(user_id, inbox_id=None):
    emails = Email.objects.order_by("-received_date").only('id')
    emails = emails.filter(inbox__user__id=user_id, inbox__flags=~Inbox.flags.exclude_from_unified)
    if inbox_id is not None:
        emails = emails.filter(inbox__id=inbox_id)
    emails = [email.id for email in emails[:100]] # number of emails on page
    emails = Email.objects.filter(id__in=emails, flags=~Email.flags.seen)

    # if some emails haven't been seen yet, we have nothing else to do
    if emails.count() > 0:
        return

    if inbox_id is None:
        profile = get_user_model().objects.select_related("userprofile").get(id=user_id).userprofile
        profile.flags.unified_has_new_messages = False
        profile.save(update_fields=["flags"])
    else:
        with watson.skip_index_update():
            inbox = Inbox.objects.get(user__id=user_id, id=inbox_id)
            inbox.flags.new = False
            inbox.save(update_fields=["flags"])

@task(ignore_result=True)
def deal_with_flags(email_id_list, user_id, inbox_id=None):
    """Set seen flags on a list of email IDs and then send off tasks to update
    "new" flags on affected Inbox objects
    """
    with transaction.atomic():
        with watson.skip_index_update():
            # update seen flags
            Email.objects.filter(id__in=email_id_list).update(flags=F('flags').bitor(Email.flags.seen))

    if inbox_id is None:
        # grab affected inboxes
        inbox_list = Inbox.objects.filter(user__id=user_id, email__id__in=email_id_list)
        inbox_list = inbox_list.distinct()

        for inbox in inbox_list:
            inbox_new_flag.delay(user_id, inbox.id)
    else:
        # we only need to update
        inbox_new_flag.delay(user_id)

@task(rate_limit="100/s")
def search(user_id, search_term, offset=0, limit=10):
    """Offload the expensive part of search to avoid blocking the web interface"""
    email_subquery = Email.objects.filter(
                        flags=F("flags").bitand(~Email.flags.deleted),
                        inbox__flags=F("inbox__flags").bitand(~Inbox.flags.deleted),
                        inbox__user_id=user_id,
                        )
    inbox_subquery = Inbox.objects.filter(flags=F("flags").bitand(~Inbox.flags.deleted), user_id=user_id)
    search_qs = watson.search(search_term, models=(email_subquery, inbox_subquery))
    limit = offset + limit

    results = {
            "emails": list(search_qs.filter(content_type__model="email").values_list("id", flat=True)[offset:limit]),
            "inboxes": list(search_qs.filter(content_type__model="inbox").values_list("id", flat=True)[offset:limit]),
            }

    return results

@task(ignore_result=True)
def force_garbage_collection():
    """Call the garbage collector.

    This task expects to be sent to a broadcast queue
    """
    collected = gc.collect()

    log.info("GC collected {0} objects.".format(collected))
