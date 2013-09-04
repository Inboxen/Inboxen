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
from website.helper.inbox import gen_inbox
from website.helper.mail import send_email, make_message
from inboxen.models import Attachment, Tag, Inbox, Domain, Email, Statistic

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
                [liberate_inbox.s(mail_path, inbox.id) for inbox in Inbox.objects.filter(user=user, deleted=False).only('id')],
                liberate_collect_emails.s(mail_path, options)
                )
    tasks.apply_async()

@task(rate='100/h')
def liberate_inbox(mail_path, inbox_id):
    """ Gather email IDs """

    inbox = Inbox.objects.get(id=inbox_id, deleted=False)
    maildir = mailbox.Maildir(mail_path)
    maildir.add_folder(str(inbox))

    return {
            'folder': str(inbox),
            'ids': [email.id for email in Email.objects.filter(inbox=inbox, deleted=False).only('id')]
            }

@task()
def liberate_collect_emails(results, mail_path, options):
    """ Send off data mining tasks """

    msg_tasks = []
    for result in results:
        inbox = [liberate_message.s(mail_path, result['folder'], email_id) for email_id in result['ids']]
        msg_tasks.extend(inbox)

    msg_tasks = chain(
                    group(msg_tasks),
                    liberate_convert_box.s(mail_path, options),
                    liberate_tarball.s(mail_path, options),
                    liberation_finish.s(mail_path, options)
                    )
    msg_tasks.apply_async()

@task(rate='1000/m')
def liberate_message(mail_path, inbox, email_id, debug=False):
    """ Take email from database and put on filesystem """
    maildir = mailbox.Maildir(mail_path).get_folder(inbox)

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

        for inbox in maildir.list_folders():
            folder = maildir.get_folder(inbox)

            for key in folder.iterkeys():
                msg = str(folder.pop(key))
                mbox.add(msg)
            maildir.remove_folder(inbox)

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

    date = str(datetime.now(utc).date())
    dir_name = "inboxen-%s" % date

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

    return {'path': tar_name, 'mime-type': tar_type['mime-type'], 'date': date, 'results': result}

@task()
@transaction.commit_on_success
def liberation_finish(result, mail_path, options):
    """ Create email to send to user """

    archive = Attachment(
                path=result['path'],
                content_type=result['mime-type'],
                content_disposition="emails-%s.%s" % (result['date'], options.get('compressType', 'tar.gz'))
                )
    archive.save()

    profile = liberate_user_profile(options['user'], result['results'], result['date'])
    profile = Attachment(
                data=profile['data'],
                content_type=profile['type'],
                content_disposition=profile['name']
                )
    profile.save()

    inbox_tags = liberate_inbox_tags(options['user'], result['date'])
    inbox_tags = Attachment(
                data=inbox_tags['data'],
                content_type=inbox_tags['type'],
                content_disposition=inbox_tags['name']
                )
    inbox_tags.save()

    inbox = Inbox.objects.filter(tag__tag="Inboxen")
    inbox = inbox.filter(tag__tag="data")
    inbox = inbox.filter(tag__tag="liberation")

    try:
        inbox = inbox.get(user__id=options['user'])
    except Inbox.MultipleObjectsReturned:
        inbox = inbox.filter(user__id=options['user'])[0]
    except Inbox.DoesNotExist:
        user = User.objects.get(id=options['user'])
        inbox = Inbox(
                inbox=gen_inbox(5),
                domain=random.choice(Domain.objects.all()),
                user=user,
                created=datetime.now(utc),
                deleted=False
            )
        inbox.save()
        tags = ["Inboxen", "data", "liberation"]
        for i, tag in enumerate(tags):
            tags[i] = Tag(tag=tag, inbox=inbox)
            tags[i].save()


    send_email(
        inbox=inbox,
        sender="support@inboxen.org",
        subject=settings.LIBERATION_SUBJECT,
        body=settings.LIBERATION_BODY,
        attachments=[archive, profile, inbox_tags]
        )

def liberate_user_profile(user_id, email_results, date):
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
    data["id"] = user.id
    data['username'] = user.username
    data['is_staff'] = user.is_staff
    data['is_superuser'] = user.is_superuser
    data["is_active"] = user.is_active
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
        'name':"user-%s.json" % date
    }

def liberate_inbox_tags(user_id, date):
    """ Grab tags from inboxes """
    data = {}

    inboxes = Inbox.objects.filter(user__id=user_id)
    for inbox in inboxes:
        email = "%s@%s" % (inbox.inbox, inbox.domain)
        tags = [tag.tag for tag in Tag.objects.filter(inbox=inbox)]
        data[email] = {
            "created":inbox.created.isoformat(),
            "deleted":inbox.deleted,
            "tags":tags,
        }

    data = json.dumps(data)

    return {
        "data":data,
        "type":"application/json",
        "name":"inboxes-%s.json" % date
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
# Inbox stuff
##

@task(rate="10/m", default_retry_delay=5 * 60) # 5 minutes
@transaction.commit_on_success
def delete_inbox(email, user=None):
    if type(email) in [types.StringType, types.UnicodeType]:
        if not user:
            raise Exception("Need to give username")
        inbox, domain = email.split("@", 1)
        try:
            domain = Domain.objects.get(domain=domain)
            inbox = Inbox.objects.get(inbox=inbox, domain=domain, user=user)
        except Inbox.DoesNotExist:
            return False
    else:
        user = email.user
        inbox = email

    # delete emails in another task(s)
    emails = Email.objects.filter(inbox=inbox, user=user).only('id')

    # sending an ID over the wire and refetching the Django model on the side
    # is cheaper than serialising the Django model - this appears to be the
    # cause of our previous memory issues! - M
    emails = group([delete_email.s(email.id) for email in emails])
    emails.apply_async()

    # okay now mark the inbox as deleted
    inbox.created = datetime.fromtimestamp(0)
    inbox.save()

    return True

@task(rate_limit=200)
@transaction.commit_on_success
def delete_email(email_id):
    email = Email.objects.filter(id=email_id).only('id')[0]
    email.delete()

@task()
@transaction.commit_on_success
def disown_inbox(result, inbox, futr_user=None):
    if not futr_user:
        futr_user = null_user()

    # delete tags
    tags = Tag.objects.filter(inbox=inbox).only('id')
    tags.delete()

    inbox.user = futr_user
    inbox.save()

@task()
@transaction.commit_on_success
def delete_user(result, user):
    inbox = Inbox.objects.filter(user=user).only('id').exists()
    if inbox:
        logging.warning("Defering user deletion to later")
        # defer this task until later
        raise delete_user.retry(
            exc=Exception("User still has inboxes"),
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
    user.is_active = False
    user.save()

    # get ready to delete all inboxes
    inbox = Inbox.objects.filter(user=user).only('id')
    if len(inbox): # we're going to use all the results anyway, so this saves us calling the ORM twice
        delete = chord([chain(delete_inbox.s(a), disown_inbox.s(a)) for a in inbox], delete_user.s(user))
        delete.apply_async()

    # scrub user info completley
    user_profile(user).delete()
