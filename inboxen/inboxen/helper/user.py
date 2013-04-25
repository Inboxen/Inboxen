from inboxen.models import UserProfile

def user_profile(user):
    """ Gets or creates a user profile """
    try:
        return UserProfile.objects.get(user=user)
    except:
        # doesn't exist
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        return user_profile
