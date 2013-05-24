import types

from datetime import datetime
from django.db import transaction
from inboxen.models import Tag, Alias, Domain, Email
from celery import task, chain
from inboxen.helper.user import null_user, user_profile

import logging

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
