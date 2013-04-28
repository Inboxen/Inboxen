from inboxen.models import Alias, Domain

def alias_exists(alias, domain):
    if Alias.objects.filter(alias=alias, domain__domain=domain).exists():
        return True
    else:
        return False

def domain_exists(domain):
    if Domain.objects.filter(domain=domain).exists():
        return True
    else:
        return False
