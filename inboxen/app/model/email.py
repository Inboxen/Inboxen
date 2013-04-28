from inboxen.models import Alias, Attachment, Email, Header
from config.settings import datetime_format, recieved_header_name
from datetime import datetime

def make_email(message, alias, domain):
    inbox = Alias.objects.filter(alias=alias, domain__domain=domain)[0]
    user = inbox.user
    body = message.base.body
    recieved_date = datetime.strptime(message[recieved_header_name], datetime_format)
    del message[recieved_header_name]

    email = Email(inbox=inbox, user=user, body=body, recieved_date=recieved_date)
    email.save()

    head_list = []
    for name in message.keys():
        header = Header(name=name, data=message[name])
        header.save()
        head_list.append(header)
    # add all the headers at once should save us some queries
    email.headers.add(*head_list)

    attach_list = []
    for part in message.walk():
        if not part.body:
            part.body = u''
        attachment = Attachment(
                        content_type=part.content_encoding['Content-Type'][0],
                        content_disposition=part.content_encoding['Content-Disposition'][0],
                        data=part.body
                        )
        attachment.save()
        attach_list.append(attachment)
    # as with headers above
    email.attachments.add(*attach_list)
