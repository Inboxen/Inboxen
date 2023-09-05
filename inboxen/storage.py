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
#    along with Inboxen  If not, see <http://www.gnu.org/licenses/>.
##

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from inboxen.utils.static import generate_maintenance_page


class InboxenStaticFilesStorage(ManifestStaticFilesStorage):
    """Generatate maintenance page after collecting static files"""

    # patterns = ManifestStaticFilesStorage.patterns + (
    #     ("*.css", (
    #         (r"""(/\*#\s*sourceMappingURL=(.*)\s*\*/)""", """/*# sourceMappingURL=%s */"""),
    #     )),
    #     ("*.js", (
    #         (r"""(//#\s*sourceMappingURL=(.*)$)""", """//# sourceMappingURL=%s"""),
    #     )),
    # )

    def post_process(self, *args, **kwargs):
        yield from super().post_process(*args, **kwargs)

        generate_maintenance_page()
