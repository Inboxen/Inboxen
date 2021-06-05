##
#    Copyright (C) 2021 Jessica Tallon & Matt Molyneaux
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

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from inboxen import validators


class LiberationQuerySet(QuerySet):
    def user_can_request_another(self, user):
        time_after = timezone.now() - self.model.TIME_BETWEEN
        last_run = self.filter(user=user, deleted=False).first()
        if last_run is None:
            return True
        elif last_run.started is None or last_run.finished is None:
            return False
        else:
            return last_run.started < time_after and last_run.finished < time_after

    def pending(self):
        return self.filter(finished__isnull=True, deleted=False, errored=False)


class Liberation(models.Model):
    """Liberation log"""
    TIME_BETWEEN = timedelta(days=7)

    TAR_GZ = 0
    TAR_BZ = 1
    TAR = 2
    ARCHIVE_TYPES = {
        TAR_GZ: {
            "ext": "tar.gz",
            "writer": "w:gz",
            "mime-type": "application/x-gzip",
            "label": _("Tarball (gzip compressed)"),
        },
        TAR_BZ: {
            "ext": "tar.bz2",
            "writer": "w:bz2",
            "mime-type": "application/x-bzip2",
            "label": _("Tarball (bzip2 compression)"),
        },
        TAR: {
            "ext": "tar",
            "writer": "w:",
            "mime-type": "application/x-tar",
            "label": _("Tarball (no compression)"),
        }
    }

    COMPRESSION_TYPES = [(k, v["label"]) for k, v in ARCHIVE_TYPES.items()]

    MAILDIR = 0
    MAILBOX = 1
    STORAGE_TYPES = (
        (MAILDIR, _("Maildir")),
        (MAILBOX, _("Mailbox .mbox")),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    compression_type = models.PositiveSmallIntegerField(choices=COMPRESSION_TYPES)
    storage_type = models.PositiveSmallIntegerField(choices=STORAGE_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    finished = models.DateTimeField(null=True)
    errored = models.BooleanField(default=False)
    error_message = models.CharField(max_length=255, null=True)
    error_traceback = models.TextField(null=True)
    deleted = models.BooleanField(default=False)

    objects = LiberationQuerySet.as_manager()

    class Meta:
        ordering = ["-created", "id"]

    def __str__(self):
        return "Liberation for %s" % self.user

    @cached_property
    def path(self):
        """Path to final archive"""
        return pathlib.Path(settings.SENDFILE_ROOT, "archives", self.pk)

    @cached_property
    def tmp_dir(self):
        """Path to temporary directory that can be removed once liberation is
        finished"""
        return pathlib.Path(settings.SENDFILE_ROOT, "tmp", self.pk)

    @cached_property
    def maildir(self):
        return mailbox.Maildir(self.tmp_dir / "emails", factory=None)
