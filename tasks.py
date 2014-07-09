import logging
from datetime import datetime, timedelta

from celery import task
from pytz import utc

from django.db import transaction
from django.db.models import F

from inboxen.models import Email, Inbox, User, Statistic

log = logging.getLogger(__name__)

@task(ignore_result=True)
@transaction.atomic()
def statistics():
    # get user statistics
    user_count = User.objects.all().count()
    new_count =  User.objects.filter(date_joined__gte=datetime.now(utc) - timedelta(days=1)).count()
    active_count = User.objects.filter(last_login__gte=datetime.now(utc) - timedelta(days=7)).count()

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
        profile = User.objects.select_related("userprofile").get(id=user_id).userprofile
        profile.flags.unified_has_new_messages = False
        profile.save()
    else:
        inbox = Inbox.objects.get(user__id=user_id, id=inbox_id)
        inbox.flags.new = False
        inbox.save()

@task(ignore_result=True)
@transaction.atomic()
def deal_with_flags(email_id_list, user_id, inbox_id=None):
    """Set seen flags on a list of email IDs and then send off tasks to update
    "new" flags on affected Inbox objects"""
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
