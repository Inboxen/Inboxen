from datetime import datetime
from inboxen.models import Tag, Alias, Domain, Email
from celery import task

@task(default_retry_delay=5 * 60) # 5 minutes
def delete_alias(email, user):
    alias, domain = email.split("@", 1)
    
    try:
        domain = Domain.objects.get(domain=domain)
        alias = Alias.objects.get(alias=alias, domain=domain, user=user, deleted=False)
    except Alias.DoesNotExist:
        return False

    # delete emails
    emails = Email.objects.filter(inbox=alias, user=user)
    emails.delete()

    # delete tags
    tags = Tag.objects.filter(alias=alias)
    tags.delete()

    # okay now mark the alias as deleted
    alias.deleted = True
    alias.created = datetime.fromtimestamp(0)
    alias.save()

    return True

@task(default_retry_delay=10 * 60)
def delete_account(user):
    # first we have to transfer all the Aliases
    pass
