import types
import random
import json
import hashlib
import time
import string
import tarfile
import os
import mailbox
import logging
from datetime import datetime, timedelta
from shutil import rmtree

from pytz import utc
from celery import task, chain, group

from django.db import transaction
from django.contrib.auth.models import User

from website.helper.user import null_user, user_profile
from website.helper.alias import gen_alias
from website.helper.mail import send_email, make_message
from inboxen.models import Attachment, Tag, Alias, Domain, Email, Statistic

##
# Data liberation
##

@task(rate="1/h")
@transaction.commit_on_success
def liberate(user, options={}):
    pass

##
# Statistics
##

@task
@transaction.commit_on_success
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

    logging.info("Saved statistics (%s)" % stat.date)


##
# Alias stuff
##

@task(rate="10/m", default_retry_delay=5 * 60) # 5 minutes
@transaction.commit_on_success
def delete_alias(email, user=None):
    if type(email) in [types.StringType, types.UnicodeType]:
        if not user:
            raise Exception("Need to give username")
        alias, domain = email.split("@", 1)
        try:
            domain = Domain.objects.get(domain=domain)
            alias = Alias.objects.get(alias=alias, domain=domain, user=user)
        except Alias.DoesNotExist:
            return False
    else:
        user = email.user
        alias = email

    # delete emails
    for email in Email.objects.filter(inbox=alias, user=user).only('id'):
        delete_email.delay(email)
        
    # delete tags
    tags = Tag.objects.filter(alias=alias)
    tags.delete()

    # okay now mark the alias as deleted
    alias.created = datetime.fromtimestamp(0)
    alias.save()

    return True

@task(ignore_result=True, store_errors_even_if_ignored=True, rate_limit=200)
@transaction.commit_on_success
def delete_email(email):
    email.delete()

@task(ignore_result=True, store_errors_even_if_ignored=True)
@transaction.commit_on_success
def disown_alias(result, alias, futr_user=None):
    if not futr_user:
        futr_user = null_user()

    alias.user = futr_user
    alias.save()

@task(max_retries=None, default_retry_delay=10 * 60, ignore_result=True, store_errors_even_if_ignored=True)
@transaction.commit_on_success
def delete_user(user):
    alias = Alias.objects.filter(user=user).only('id').exists()
    if alias:
        logging.info("Defering user deletion to later")
        # defer this task until later
        raise delete_user.retry(
            exc=Exception("User still has aliases"),
            countdown=60)
    else:
        logging.info("Deleting user %s" % user.username)
        user.delete()
    return True

@task(default_retry_delay=10 * 60, ignore_result=True, store_errors_even_if_ignored=True)
@transaction.commit_on_success
def delete_account(user):
    # first we need to make sure the user can't login
    user.set_unusable_password()
    user.save()

    # first delete all aliases
    alias = Alias.objects.filter(user=user).only('id')
    for a in alias:
        chain(delete_alias.s(a), disown_alias.s(a)).delay()

    # now scrub some more info we have
    user_profile(user).delete()
    
    # finally delete the user object only when 
    # all the alias/email tasks have finished
    delete_user.delay(user) 
