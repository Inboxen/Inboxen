from setuptools import setup, find_packages

setup(
    name="Inboxen",
    version=0.2,
    author="Jessica and Matthew",
    author_email="support@inboxen.org",
    description="Provides perminant read-only inboxes",
    long_description="A service which allows you to easily create many email addresses so that websites can't identify you by your email",
    license="AGPL v3",
    keywords="inboxen email inboxen privacy",
    url="https://inboxen.org",

 
    # requirements
    packages=find_packages(),

    install_requires = [
        "Markdown >= 2.3.1",
        "django >= 1.5.1",
        "lamson >= 1.3.4",
        "pytz >= 2013b",
        "Celery >= 3.0.19",
        "django-celery >= 3.0.17",
        "south >= 0.8.1",
        "django-extensions >= 1.1.1",
    ],

    extras_require = {
        "couchdb":[
            "celery-with-couchdb >= 3.0",
        ],
        "mongodb":[
            "celery-with-mongodb >= 3.0",
        ],
        "redis":[
            "celery-with-redis >= 3.0",
        ],
        "mysql":[
            "MySQL-python >= 1.2.4",
       ],
    },

)

