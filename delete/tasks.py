import logging
import types
from datetime import datetime

from celery import chain, chord, group, task
from pytz import utc

from django.db import transaction

from inboxen.helper.user import null_user, user_profile
from inboxen.models import Domain, Email, Inbox, Tag

##
# Delete stuff
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
    inbox.created = datetime.fromtimestamp(0, utc)
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
    user.delete()
