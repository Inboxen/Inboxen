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

import os

from setuptools import find_packages, setup
import versioneer


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="inboxen",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Inboxen.org",
    author_email="support@inboxen.org",
    description="An email privacy tool",
    url="https://inboxen.org",
    download_url="https://github.com/Inboxen/Inboxen",
    license="AGPLv3",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2rc1,<4.0",
        "Markdown",
        "celery<5,!=4.4.7",
        "django-annoying",
        "django-bootstrap-form",
        "django-celery-results",
        "django-csp>3.0",
        # vendored until 0.1.5 has been released
        # "django-cursor-pagination",
        "django-elevate",
        "django-extensions",
        "django-mptt",
        "django-otp",
        "django-sendfile2",
        "django-two-factor-auth>=1.5.0",
        "factory-boy>=3.0",
        "lxml",
        # make sure django-phonenumbers uses the smaller package
        "phonenumberslite",
        "pillow",
        "premailer",
        "progress",
        "psycopg2",
        "pytz",
        "ruamel.yaml",
        "salmon-mail>=3.2.0",
    ],
    extras_require={
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
        ],
    },
    entry_points={
        "console_scripts": ['inboxen = inboxen.bin.manage:main'],
    },
)
