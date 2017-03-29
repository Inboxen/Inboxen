from django.http import Http404


def user_editing_disabled_view(request):
    raise Http404("User editing disabled")
