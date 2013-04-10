from frontend.models import Alias, Domain

def alias_exists(alias, domain):
    if Alias.objects.filter(alias=alias, domain=domain):
        return True
    else:
        return False

def domain_exists(domain):
    if Domain.objects.filter(domain=domain):
        return True
    else:
        return False
