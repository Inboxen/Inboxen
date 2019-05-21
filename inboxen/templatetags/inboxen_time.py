##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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

from datetime import datetime, timedelta
import calendar

from django import template
from django.utils import timezone
from django.utils.html import avoid_wrapping
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext_lazy

register = template.Library()


TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, ungettext_lazy('a year ago', '%d years ago')),
    (60 * 60 * 24 * 30, ungettext_lazy('a month ago', '%d months ago')),
    (60 * 60 * 24 * 7, ungettext_lazy('a week ago', '%d weeks ago')),
    (60 * 60 * 24, ungettext_lazy('a day ago', '%d days ago')),
    (60 * 60, ungettext_lazy('a hour ago', '%d hours ago')),
    (60, ungettext_lazy('a minute ago', '%d minutes ago'))
)


@register.filter(is_safe=False)
def inboxentime(value):
    """A filter much like Django's timesince and naturaltime, except it only
    gives the most significant unit.

    Much of this function was taken from Django 1.11.12

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice,
           this list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.

        3. Neither the name of Django nor the names of its contributors may be used
           to endorse or promote products derived from this software without
           specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    if not isinstance(value, datetime):
        value = datetime(value.year, value.month, value.day)

    now = timezone.now()

    delta = now - value

    # Deal with leapyears by substracting leapdays
    leapdays = calendar.leapdays(value.year, now.year)
    if leapdays != 0:
        if calendar.isleap(value.year):
            leapdays -= 1
        elif calendar.isleap(now.year):
            leapdays += 1
    delta -= timedelta(leapdays)

    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 60:
        # if it's less than a minute ago, it was just now
        return avoid_wrapping(_("just now"))

    for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
        count = since // seconds
        if count != 0:
            break

    name = name % count
    return avoid_wrapping(name)
