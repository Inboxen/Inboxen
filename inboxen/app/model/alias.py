from front-end.models import Alias, Domain

def AliasExists(alias, domain):
    if Alias.objects.filter(alias=alias, domain=domain):
        return True
    else:
        return False

def DomainExists(domain):
    if Domain.objects.filter(domain=domain):
        return True
    else:
        return False
