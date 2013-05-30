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

from pytz import utc
from datetime import datetime, timedelta
from django.db import transaction
from inboxen.models import Attachment, Tag, Alias, Domain, Email, Statistic
from django.contrib.auth.models import User
from celery import task, chain
from inboxen.helper.user import null_user, user_profile
from inboxen.helper.alias import gen_alias
from inboxen.helper.mail import send_email, make_message

##
# Data liberation
##
@task
def liberate(user):
    result = chain(liberate_user.s(user), liberate_aliases.s(user), liberate_emails.s(user))()
    result = [result.get(), result.parent.get(), result.parent.parent.get()]

    # todo: reuse previously made alias if one does exist.
    alias = None
 
    if not alias:
        # okay first time, lets make an alias
        alias = Alias(
            alias=gen_alias(5),
            domain=random.choice(Domain.objects.all()),
            user=user,
            created=datetime.now(utc),
            deleted=False
        )
        alias.save()
        tags = ["Inboxen", "data", "liberation"]
        for i, tag in enumerate(tags):
            tags[i] = Tag(tag=tag, alias=alias)
            tags[i].save()
    
    # right now we need to take the result and make attachments
    attachments = []
    for data in result:
        if data["file"]:
            # store as path
            a = Attachment(
                path=data["data"],
                content_type=data["type"],
                content_disposition=data["name"],
            )
        else:
            # store as regular attachment in db
            a = Attachment(
                data=data["data"],
                content_type=data["type"],
                content_disposition=data["name"]
            )
        a.save()
        attachments.append(a)

    body = """
    Hello,

    You recently requested your data. All the data you have is here excluding:

    - Your password (this is hashed[1] and salted[2] so is a string of nonsense)
    - Your salt[2] (this is used help secure the storage of your password)

    We don't disclose them as those do not change due to data liberation, since they don't
    give any value to you they just reduce the security. All your other data has been given to you though.
    
    You should find attached to this email all the data Inboxen has.

    Thanks,
    The Inboxen Team.

    --
    [1] - https://en.wikipedia.org/wiki/Hash_function
    [2] - https://en.wikipedia.org/wiki/Salt_%28cryptography%29
    """

    send_email(
        user=user, 
        alias=alias,
        sender="support@inboxen.org",
        subject="Data Liberation",
        body=body,
        attachments=attachments,
    ) 

@task
def liberate_user(user):
    data = {
        "preferences":{}
    }

    # user's preferences
    profile = user_profile(user)
    if profile.html_preference == 0:
        data["preferences"]["html_preference"] = "Reject HTML"
    elif profile.html_preference == 1:
        data["preferences"]["html_preference"] = "Prefer plain-text"
    else:
        data["preferences"]["html_preference"] = "Prefer HTML"

    data["preferences"]["pool_amount"] = profile.pool_amount

    # user data
    data["username"] = user.username
    data["is_staff"] = user.is_staff
    data["is_superuser"] = user.is_superuser
    data["last_login"] = user.last_login.isoformat()
    data["join_date"] = user.date_joined.isoformat()
    data["groups"] = [str(group) for group in user.groups.all()]

    data = json.dumps(data)

    return {
        "data":data,
        "type":"text/json",
        "name":"User Data",
        "file":False,
    }

@task
def liberate_aliases(result, user):
    data = {}

    aliases = Alias.objects.filter(user=user)
    for alias in aliases:
        email = "%s@%s" % (alias.alias, alias.domain)
        tags = [tag.tag for tag in Tag.objects.filter(alias=alias)]
        data[email] = {
            "created":alias.created.isoformat(),
            "deleted":alias.deleted,
            "tags":tags,
        }

    data = json.dumps(data)

    return {
        "data":data,
        "type":"text/json",
        "name":"Aliases",
        "file":False,
    }

@task
def liberate_emails(result, user):
    """ Makes a maildir of all their emails """
    # first we need to come up with a temp name
    rstr = ""
    for i in range(7):
        rstr += string.ascii_letters[random.randint(0, 50)]
    fname = "/tmp/mkdir%s_%s_%s_%s" % (time.time(), os.getpid(), rstr, hashlib.sha256(user.username + rstr).hexdigest()[:50])
    
    # now make the maildir
    mdir = mailbox.Maildir(fname)
    mdir.lock()
    # right
    for email in Email.objects.filter(user=user).iterator():
        message_result = liberate_make_message(email).get()
        msg = message_result.result
        mdir.add(msg)
    mdir.flush()

    # now we need to tar this puppy up!
    tar = tarfile.open("%s.tar.gz" % fname, "w:gz")
    tar.add("%s/" % fname) # directories are added recursively by default
    tar.close()

    # right now we just wanna throw this into an attachment
    # at some point (soon) we need to get it so attachments can live on the filesystem

    return {
        "data":"%s.tar.gz" % fname,
        "type":"application/x-gzip",
        "name":"Tarball of emails as Maildir",
        "file":True,
    }

@task(rate=15)
def liberate_make_message(message):
    """ Takes a message and makes it """
    msg = make_message(message)
    msg = msg.as_string()
    return msg

##
# Statistics
##

@task
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
@task(default_retry_delay=5 * 60) # 5 minutes
def delete_alias(email, user=None):
    if email in [types.StringType]:
        if not user:
            raise Exception("Need to give username")
        alias, domain = email.split("@", 1)
        try:
            domain = Domain.objects.get(domain=domain)
            alias = Alias.objects.get(alias=alias, domain=domain, user=user)
        except Alias.DoesNotExist:
            return False
    else:
        user = email.inbox.user
        alias = email
    # delete emails
    emails = Email.objects.filter(inbox=alias, user=user).iterator()

    # it seems to cause problems if you do QuerySet.delete()
    # this seems to be more efficiant when we have a lot of data
    for email in emails:
        delete_email.delay(email)

    # delete tags
    tags = Tag.objects.filter(alias=alias)
    tags.delete()

    # okay now mark the alias as deleted
    alias.created = datetime.fromtimestamp(0)
    alias.save()

    return True

@task(rate_limit=100, ignore_result=True, store_errors_even_if_ignored=True)
@transaction.commit_on_success
def delete_email(email):
    email.delete()

@task(ignore_result=True, store_errors_even_if_ignored=True)
def disown_alias(result, alias, futr_user=None):
    if not futr_user:
        futr_user = null_user()

    alias.user = futr_user
    alias.save()

@task(max_retries=None, default_retry_delay=10 * 60, ignore_result=True, store_errors_even_if_ignored=True)
def delete_user(user):
    alias = Alias.objects.filter(user=user).exists()
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
def delete_account(user):
    # first we need to make sure the user can't login
    user.set_unusable_password()
    user.save()

    # first delete all aliases
    alias = Alias.objects.filter(user=user)[:100]
    for a in alias:
        chain(delete_alias.s(a), disown_alias.s(a)).delay()

    # now scrub some more info we have
    user_profile(user).delete()
    
    # finally delete the user object only when 
    # all the alias/email tasks have finished
    delete_user.delay(user) 
