from django.contrib import messages

from inboxen.async_messages import get_messages


class AsyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Check for messages for this user and, if it exists,
        call the messages API with it
        """
        response = self.get_response(request)
        if hasattr(request, "session") and hasattr(request, "user") and request.user.is_authenticated:
            msgs = get_messages(request.user)
            if msgs:
                for msg, level in msgs:
                    messages.add_message(request, level, msg)
        return response
