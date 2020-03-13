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

from setuptools import find_packages, setup

import versioneer

setup(
    name="inboxen",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Inboxen.org",
    description="An email privacy tool",
    url="https://inboxen.org",
    download_url="https://github.com/Inboxen/Inboxen",
    license="AGPLv3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=2.2,<2.3",
        "Markdown",
        "celery>=4.1,<4.2",
        "configobj",
        "django-annoying",
        "django-bootstrap-form",
        "django-csp>3.0",
        "django-cursor-pagination",
        "django-extensions",
        "django-mptt",
        "django-otp",
        "django-ratelimit-backend",
        "django-sendfile2",
        "django-elevate",
        "django-two-factor-auth>=1.5.0",
        "factory-boy",
        "lxml",
        # make sure django-phonenumbers uses the smaller package
        "phonenumberslite",
        "pillow",
        "premailer",
        "progress",
        "psycopg2",
        "pytz",
        "salmon-mail>=3.2.0",
    ],
    extras_require={
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
        ],
        "cache-memcache": [
            "pylibmc",
        ],
    },
)
