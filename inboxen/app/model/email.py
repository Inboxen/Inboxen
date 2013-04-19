from inboxen.models import Alias, Attachment, Email, Header
from config.settings import datetime_format, recieved_header_name
from datetime import datetime

def make_email(message, alias, domain):
    inbox = Alias.objects.filter(alias=alias, domain__domain=domain)[0]
    user = inbox.user
    body = message.base.body
    recieved_date = datetime.strptime(message[recieved_header_name], datetime_format)
    del message[recieved_header_name]

    email = Email(user=user, inbox=inbox, recieved_date=recieved_date)

    for name in message.keys():
        email.headers.create(name=name, data=message[name])

    for part in message.all_parts():
        email.attachments.create(
                        content_type=part.content_encoding['Content-Type'][0],
                        content_disposition=content_encoding['Content-Disposition'][0]
                        )

    email.save()
