import types
import random
import json
import time
import string
import tarfile
import os
import mailbox
import logging
from datetime import datetime, timedelta
from shutil import rmtree
from hashlib import sha256

from pytz import utc
from celery import task, chain, group. chord

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
def liberate(user, options={}):
    """ Get set for liberation, expects User object """
    rstr = ""
    for i in range(7):
        rstr += string.ascii_letters[random.randint(0, 50)]
    mail_path = "/tmp/%s_%s_%s_%s" % (time.time(), os.getpid(), rstr, sha256(user.username + rstr).hexdigest()[:50]

    # make maildir
    mailbox.Maildir(mail_path)

    chord([liberate_alias.s(mail_path, alias.id) for alias in Alias.objects.filter(user=user, deleted=False).only('id')], liberate_collect_emails.s(mail_path, options)).apply_async()

@task(rate="10/h")
def liberate_alias(mail_path, alias_id):
    """ Gather email IDs """

    alias = Alias.objects.get(id=alias_id, deleted=False)
    maildir = mailbox.Maildir(mail_path)
    maildir.add_folder(str(alias))
    return {'folder': str(alias), 'ids': [email.id for email in Email.objects.filter(alias=alias).only('id')]}

@task()
def liberate_collect_emails(results, mail_path, options):
    """ Send off data mining tasks """

    msg_tasks = []
    for result in results:
        alias = [liberate_message.s(mail_path, result['folder'], email_id) for email_id in result['ids']]
        msg_tasks.append(alias)
    msg_tasks = chain(group(msg_tasks).s(), liberate_taball.s(mail_path))
    chord(msg_tasks.s(),liberate_finish.s(maildir)).apply_async()

@task(rate="100/m")
def liberate_message(mail_path, alias, email_id):
    """ Take email from database and put on filesystem """

    maildir = mailbox.Maildir(mail_path).get_folder(alias)
    msg = Email.objects.get(id=email_id)
    msg = make_message(msg)
    maildir.add(str(msg))

@task()
def liberate_tarball(result, mail_path):
    pass

    # tarball maildir or mbox
    # remove maildir/mbox
    # retry on exception

@task()
@transaction.commit_manually
def liberation_finish(result, maildir):
    pass

    # create attachments with user data
    # grab ids of email tasks that failed, attach them to user data
    # work out tarball name and attach
    # "send" email

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
