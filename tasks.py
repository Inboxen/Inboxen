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
from django.conf import settings

from website.helper.user import null_user, user_profile
from website.helper.alias import gen_alias
from website.helper.mail import send_email, make_message
from inboxen.models import Attachment, Tag, Alias, Domain, Email, Statistic

for setting_name in ('LIBERATION_BODY', 'LIBERATION_SUBJECT', 'LIBERATION_PATH'):
    assert hasattr(settings, setting_name), "%s has not been set" % setting_name

TAR_TYPES = {
    'tar.gz': {'writer': 'w:gz', 'mime-type': 'application/x-gzip'},
    'tar.bz2': {'writer': 'w:bz2', 'mime-type': 'application/x-bzip2'},
    'tar': {'writer': 'w:', 'mime-type': 'application/x-tar'}
    }

##
# Data liberation
##

@task(rate='2/h')
def liberate(user, options={}):
    """ Get set for liberation, expects User object """

    options['user'] = user.id

    rstr = ""
    for i in range(7):
        rstr += string.ascii_letters[random.randint(0, 50)]
    mail_path = "%s/%s_%s_%s_%s" % (settings.LIBERATION_PATH, time.time(), os.getpid(), rstr, hashlib.sha256(user.username + rstr).hexdigest()[:50])

    # make maildir
    mailbox.Maildir(mail_path)

    tasks = chord(
                [liberate_alias.s(mail_path, alias.id) for alias in Alias.objects.filter(user=user, deleted=False).only('id')],
                liberate_collect_emails.s(mail_path, options)
                )
    tasks.apply_async()

@task(rate='100/h')
def liberate_alias(mail_path, alias_id):
    """ Gather email IDs """

    alias = Alias.objects.get(id=alias_id, deleted=False)
    maildir = mailbox.Maildir(mail_path)
    maildir.add_folder(str(alias))

    return {
            'folder': str(alias),
            'ids': [email.id for email in Email.objects.filter(inbox=alias, deleted=False).only('id')]
            }

@task()
def liberate_collect_emails(results, mail_path, options):
    """ Send off data mining tasks """

    msg_tasks = []
    for result in results:
        alias = [liberate_message.s(mail_path, result['folder'], email_id) for email_id in result['ids']]
        msg_tasks.extend(alias)

    msg_tasks = chain(
                    group(msg_tasks),
                    liberate_convert_box.s(mail_path, options),
                    liberate_tarball.s(mail_path, options),
                    liberation_finish.s(mail_path, options)
                    )
    msg_tasks.apply_async()

@task(rate='1000/m')
def liberate_message(mail_path, alias, email_id, debug=False):
    """ Take email from database and put on filesystem """
    maildir = mailbox.Maildir(mail_path).get_folder(alias)

    try:
        msg = Email.objects.get(id=email_id, deleted=False)
        msg = make_message(msg)
    except Exception, exc:
        if debug:
            raise
        else:
            raise Exception(hex(int(email_id))[2:])

    maildir.add(str(msg))

@task()
def liberate_convert_box(result, mail_path, options):
    """ Convert maildir to mbox if needed """
    if options['mailType'] == 'maildir':
        pass

    elif options['mailType'] == 'mailbox':

        maildir = mailbox.Maildir(mail_path)
        mbox = mailbox.mbox(mail_path + '.mbox')
        mbox.lock()

        for alias in maildir.list_folders():
            folder = maildir.get_folder(alias)

            for key in folder.iterkeys():
                msg = str(folder.pop(key))
                mbox.add(msg)
            maildir.remove_folder(alias)

        rmtree(mail_path)
        mbox.close()

    return result

@task(default_retry_delay=600)
def liberate_tarball(result, mail_path, options):
    """ Tar up and delete the maildir """

    try:
        tar_type = TAR_TYPES[options.get('compressType', 'tar.gz')]
        tar_name = "%s.%s" % (mail_path, options.get('compressType', 'tar.gz'))
        tar = tarfile.open(tar_name, tar_type['writer'])
    except (IOError, OSError), error:
        raise liberate_tarball.retry(exc=error)

    dir_name = "inboxen-%s" % datetime.now(utc).date()

    if options['mailType'] == 'maildir':
        try:
            tar.add("%s/" % mail_path, dir_name) # directories are added recursively by default
        finally:
            tar.close()
        rmtree(mail_path)

    elif options['mailType'] == 'mailbox':
        try:
            tar.add("%s.mbox" % mail_path, dir_name)
        finally:
            tar.close()
        os.remove("%s.mbox" % mail_path)

    return {'path': tar_name, 'mime-type': tar_type['mime-type'], 'results': result}

@task()
@transaction.commit_on_success
def liberation_finish(result, mail_path, options):
    """ Create email to send to user """

    archive = Attachment(
                path=result['path'],
                content_type=result['mime-type'],
                content_disposition="emails.%s" % options.get('compressType', 'tar.gz')
                )
    archive.save()

    profile = liberate_user_profile(options['user'], result['results'])
    profile = Attachment(
                data=profile['data'],
                content_type=profile['type'],
                content_disposition=profile['name']
                )
    profile.save()

    alias_tags = liberate_alias_tags(options['user'])
    alias_tags = Attachment(
                data=alias_tags['data'],
                content_type=alias_tags['type'],
                content_disposition=alias_tags['name']
                )
    alias_tags.save()

    alias = Alias.objects.filter(tag__tag="Inboxen")
    alias = alias.filter(tag__tag="data")
    alias = alias.filter(tag__tag="liberation")

    try:
        alias = alias.get(user__id=options['user'])
    except Alias.MultipleObjectsReturned:
        alias = alias.filter(user__id=options['user'])[0]
    except Alias.DoesNotExist:
        user = User.objects.get(id=options['user'])
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
        subject=settings.LIBERATION_SUBJECT,
        body=settings.LIBERATION_BODY,
        attachments=[archive, profile, alias_tags]
        )

def liberate_user_profile(user_id, email_results):
    """ User profile data """
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

    data['errors'] = []
    for result in email_results:
        if result != None:
            data['errors'].append(str(result))

    data = json.dumps(data)

    return {
        'data':data,
        'type':'application/json',
        'name':'user.json'
    }

def liberate_alias_tags(user_id):
    """ Grab tags from aliases """
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
        "type":"application/json",
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

    # delete emails in another task(s)
    emails = Email.objects.filter(inbox=alias, user=user).only('id')

    # sending an ID over the wire and refetching the Django model on the side
    # is cheaper than serialising the Django model - this appears to be the
    # cause of our previous memory issues! - M
    emails = group([delete_email.s(email.id) for email in emails])
    emails.apply_async()
        
    # delete tags
    tags = Tag.objects.filter(alias=alias).only('id')
    tags.delete()

    # okay now mark the alias as deleted
    alias.created = datetime.fromtimestamp(0)
    alias.save()

    return True

@task(rate_limit=200)
@transaction.commit_on_success
def delete_email(email_id):
    email = Email.objects.filter(id=email_id).only('id')[0]
    email.delete()

@task()
@transaction.commit_on_success
def disown_alias(result, alias, futr_user=None):
    if not futr_user:
        futr_user = null_user()

    alias.user = futr_user
    alias.save()

@task()
@transaction.commit_on_success
def delete_user(user):
    alias = Alias.objects.filter(user=user).only('id').exists()
    if alias:
        logging.warning("Defering user deletion to later")
        # defer this task until later
        raise delete_user.retry(
            exc=Exception("User still has aliases"),
            countdown=60)
    else:
        logging.info("Deleting user %s" % user.username)
        user.delete()
    return True

@task()
@transaction.commit_on_success
def delete_account(user):
    # first we need to make sure the user can't login
    user.set_unusable_password()
    user.save()

    # get ready to delete all aliases
    alias = Alias.objects.filter(user=user).only('id')
    delete = chord([chain(delete_alias.s(a), disown_alias.s(a)) for a in alias], delete_user.s(user))

    # now scrub info we have
    user_profile(user).delete()

    # now send off delete tasks
    delete.apply_async()
