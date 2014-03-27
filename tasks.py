import logging
from datetime import datetime, timedelta

from celery import task
from pytz import utc

from django.db import transaction
from django.db.models import F

from inboxen.models import Email, User, Statistic

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
def deal_with_flags(email_id_list, inbox_id=None):
    Email.objects.filter(id__in=email_id_list).update(flag=F('flags').bitor(Email.flags.seen))
