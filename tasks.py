import types
import random
import json
import time
import string
import tarfile
import os
import mailbox
import logging
import hashlib
from datetime import datetime, timedelta
from shutil import rmtree

from pytz import utc
from celery import task, chain, group, chord

from django.db import transaction
from django.contrib.auth.models import User

from website.helper.user import null_user, user_profile
from website.helper.alias import gen_alias
from website.helper.mail import send_email, make_message
from inboxen.models import Attachment, Tag, Alias, Domain, Email, Statistic

TAR_TYPE = {
    'tar.gz': {'writer': 'w:gz', 'mime-type': 'application/x-gzip'},
    'tar.bz2': {'writer': 'w:bz2', 'mime-type': 'application/x-bzip2'},
    'tar': {'writer': 'w:', 'mime-type': 'application/x-tar'}
    }

##
# Data liberation
##

# limit each line to 79 chars
LIBERATION_BODY = """Hello,

You recently requested we liberate your data. Please find attached all data we
have of yours, excluding:

- Your password (this is hashed[1] and salted[2] so is a string of nonsense)
- The salt[2] (this is used help secure the storage of your password)

Both these data could be used to compromise your account if not kept secure
and are completely useless to you as you already know your password.

Please don't hesitate to contact support if there are any issues with the
attached files.

Thank you,,
The Inboxen Team.

--
[1] - https://en.wikipedia.org/wiki/Hash_function
[2] - https://en.wikipedia.org/wiki/Salt_%28cryptography%29
"""


@task(rate='2/h')
def liberate(user, options={}):
    """ Get set for liberation, expects User object """

    options['user'] = user.id

    rstr = ""
    for i in range(7):
        rstr += string.ascii_letters[random.randint(0, 50)]
    mail_path = "/tmp/%s_%s_%s_%s" % (time.time(), os.getpid(), rstr, hashlib.sha256(user.username + rstr).hexdigest()[:50])

    # make maildir
    mailbox.Maildir(mail_path)

    chord([liberate_alias.s(mail_path, alias.id) for alias in Alias.objects.filter(user=user, deleted=False).only('id')], liberate_collect_emails.s(mail_path, options)).apply_async()

@task(rate='100/h')
def liberate_alias(mail_path, alias_id):
    """ Gather email IDs """

    alias = Alias.objects.get(id=alias_id, deleted=False)
    maildir = mailbox.Maildir(mail_path)
    maildir.add_folder(str(alias))

    return {
            'folder': str(alias),
            'ids': [email.id for email in Email.objects.filter(inbox=alias).only('id')]
            }

@task()
def liberate_collect_emails(results, mail_path, options):
    """ Send off data mining tasks """

    msg_tasks = []
    for result in results:
        alias = [liberate_message.s(mail_path, result['folder'], email_id) for email_id in result['ids']]
        msg_tasks.extend(alias)

    msg_tasks = chain(group(msg_tasks), liberate_tarball.s(mail_path, options), liberation_finish.s(mail_path, options))
    msg_tasks.apply_async()

@task(rate='1000/m')
def liberate_message(mail_path, alias, email_id):
    """ Take email from database and put on filesystem """

    maildir = mailbox.Maildir(mail_path).get_folder(alias)
    msg = Email.objects.get(id=email_id)
    msg = make_message(msg)
    maildir.add(str(msg))

@task(default_retry_delay=600)
def liberate_tarball(result, mail_path, options):
    """ Tar up and delete the maildir """

    # TODO: Move tar to somewhere that's not /tmp

    try:
        tar_type = TAR_TYPES[options['compressType']]
        tar_name = "%s.%s" % (mail_path, options['compressType'])
        tar = tarfile.open(tar_name, tar_type['writer'])
    except (IOError, OSError), error:
        raise liberate_tarball.retry(exc=error)

    try:
        tar.add("%s/" % mail_path) # directories are added recursively by default
    finally:
        tar.close()

    rmtree(mail_path)

    return {'path': tar_name, 'mime-type': tar_type['mime-type']}

@task()
@transaction.commit_on_success
def liberation_finish(result, mail_path, options):
    """ Create email to send to user """

    archive = result.get()
    archive = Attachment(
                path=archive['path'],
                content_type=archive['mime-type'],
                content_disposition=archive['path'].split('/')[-1]
                )
    archive.save()

    profile = liberate_user_profile(options['user'], result.parent)
    profile = Attachment(
                data=profile['data'],
                content_type=profile['type'],
                content_disposition=profile['name']
                )

    alias_tags = liberate_alias_tags(options['user'])
    alias_tags = Attachment(
                data=alias_tags['data'],
                content_type=profile['type'],
                content_disposition=profile['name']
                )
    alias_tags.save()

    alias = Alias.objects.filter(tag="Inboxen")
    alias = alias.filter(tag="data")
    alias = alias.filter(tag="liberation")

    try:
        alias = alias.get(user__id=options['user'])
    except Alias.MultipleObjectsReturned:
        alias = alias.filter(user__id=options['user'])[0]
    except Alias.DoesNotExist:
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


   send_email(
        alias=alias,
        sender="support@inboxen.org",
        subject="Data Liberation",
        body=LIBERATION_BODY
        attachments=[archive, profile, alias_tags, errors]

def liberate_user_profile(user_id, email_results):
    data = {
        'preferences':{}
    }
    user = User.objects.get(id=user_id)


    # user's preferences
    profile = user_profile(user)
    if profile.html_preference == 0:
        data['preferences']['html_preference'] = 'Reject HTML'
    elif profile.html_preference == 1:
        data['preferences']['html_preference'] = 'Prefer plain-text'
    else:
        data['preferences']['html_preference'] = 'Prefer HTML'

    data['preferences']['pool_amount'] = profile.pool_amount

    # user data
    data['username'] = user.username
    data['is_staff'] = user.is_staff
    data['is_superuser'] = user.is_superuser
    data['last_login'] = user.last_login.isoformat()
    data['join_date'] = user.date_joined.isoformat()
    data['groups'] = [str(group) for group in user.groups.all()]

    if email_results.failed():
        data['errors'] = []
        for result in email_results:
            data['errors'].append(str(result))

    data = json.dumps(data)

    return {
        'data':data,
        'type':'text/json',
        'name':'user.json'
    }

def liberate_alias_tags(user_id):
    data = {}

    aliases = Alias.objects.filter(user__id=user_id)
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
        "name":"aliases.json"
    }

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
