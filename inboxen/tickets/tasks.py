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

from pathlib import PurePath
import logging

from django.conf import settings
from django.core.mail import mail_admins
from django.template import loader
from django.urls import reverse

from inboxen.celery import app

log = logging.getLogger(__name__)


SUBJECT_TMPL = "[{site_name} ticket]: #{id}  {subject}"


@app.task(ignore_result=True)
def new_question_notification(question_id):
    from inboxen.tickets.models import Question

    question = Question.objects.select_related("author").get(id=question_id)
    plain_template = loader.get_template("tickets/new_question_email.txt")
    html_template = loader.get_template("tickets/new_question_email.html")

    context = {
        "question": question,
        "admin_url": PurePath(settings.SITE_URL,
                              reverse("admin:tickets:response", kwargs={"question_pk": question.pk})),
    }
    subject = SUBJECT_TMPL.format(site_name=settings.SITE_NAME, subject=question.subject, id=question.id)
    plain_body = plain_template.render(context)
    html_body = html_template.render(context)

    try:
        mail_admins(subject, plain_body, html_message=html_body)
        log.info("Sent admin email for Question: %s", question.pk)
    except Exception as exc:
        raise new_question_notification.retry(countdown=300, exc=exc)
