##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

import logging

from django.conf import settings
from django.core.mail import mail_admins
from django.db.models.loading import get_model

from celery import task

log = logging.getLogger(__name__)

SUBJECT_TMPL = "[{site_name} ticket]: #{id}  {subject}"

BODY_TMPL = """
Admins,

{user} has a question:

Subject: {subject}

Message:
{body}
"""

@task(ignore_result=True)
def new_question_notification(question_id):
    question = get_model("tickets", "question").objects.select_related("author").get(id=question_id)
    subject = SUBJECT_TMPL.format(site_name=settings.SITE_NAME, subject=question.subject, id=question.id)
    body = BODY_TMPL.format(user=question.author, subject=question.subject, body=question.body)

    try:
        mail_admins(subject, body)
        log.info("Sent admin email for Question: %s", question.pk)
    except Exception as exc:
        raise new_question_notification.retry(countdown=300, exc=exc)
