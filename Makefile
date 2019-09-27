##
# Dev
##

# this rule should be the default
.PHONY: dev-setup
dev-setup: install-dev-deps
	mkdir -p logs run
	$(MAKE) static
	./manage.py
	./manage.py migrate
	touch inboxen/wsgi.py
	echo "You're now set for Inboxen development."
	echo "If you require salmon, run 'make salmon-start'"
	echo "If you require celery, run 'make celery-start'"

.PHONY: install-dev-deps
install-dev-deps: install-dev-py-deps install-js-deps

.PHONY: install-dev-py-deps
install-dev-py-deps:
	pip-sync requirements-dev.txt || pip install -r requirements-dev.txt

.PHONY: install-js-deps
install-js-deps:
	npm install

.PHONY: tests-py
tests-py: install-dev-deps
	DJANGO_SETTINGS_MODULE=inboxen.tests.settings $(MAKE) static
	./manage.py test

.PHONY: tests-py-coverage
tests-py-coverage: install-dev-deps
	DJANGO_SETTINGS_MODULE=inboxen.tests.settings $(MAKE) static
	pip install coverage
	coverage run --branch ./manage.py test

.PHONY: tests-js
tests-js: install-dev-deps
	npx grunt tests

##
# Update requirements
##

.PHONY: udpate-requirements
update-requirements: update-py-requirements update-js-requirements

.PHONY: update-py-requirements
update-py-requirements:
	# pip-compile turns "-e ." into "-e file:///full/path/", which makes the
	# output file useless on other machines - we use sed to reverse this
	pip-compile -U -o requirements.txt inboxen/data/requirements.in
	sed -i "s/-e file:\/\/.*/-e \./" requirements.txt
	pip-compile -U -o requirements-dev.txt requirements-dev.in | sed "s/-e file:\/\/.*/-e \./" > requirements-dev.txt
	sed -i "s/-e file:\/\/.*/-e \./" requirements-dev.txt
	pip-compile -U -o extra/requirements/watermelon.inboxen.org.txt extra/requirements/watermelon.inboxen.org.in
	sed -i "s/-e file:\/\/.*/-e \./" extra/requirements/watermelon.inboxen.org.txt

.PHONY: update-js-requirements
update-js-requirements:
	npm update

##
# Static assets
##

.PHONY: static
static:
	npx grunt
	./manage.py compilemessages
	./manage.py collectstatic --clear --noinput

##
# Daemon control
##

.PHONY: celery-stop
celery-stop:
	pkill -f "celery worker"

.PHONY: celery-start
celery-start:
	DJANGO_SETTINGS_MODULE=inboxen.settings celery -A inboxen worker -l warn -B -E -D -f celery.log

.PHONY: salmon-stop
salmon-stop:
	SALMON_SETTINGS_MODULE=inboxen.router.config.settings salmon stop --pid run/router.pid

.PHONY: salmon-start
salmon-start:
	SALMON_SETTINGS_MODULE=inboxen.router.config.settings salmon start --pid run/router.pid --boot inboxen.router.config.boot
	sleep 5
	SALMON_SETTINGS_MODULE=inboxen.router.config.settings salmon status --pid run/router.pid

##
# Includes
##

include extra/makefiles/watermleon.mk
-include local.mk
