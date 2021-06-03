# this rule should be the default
.PHONY: dev-setup
dev-setup: install-deps
	mkdir -p logs run
	$(MAKE) static-local
	./manage.py migrate
	touch inboxen/wsgi.py
	$(info You're now set for Inboxen development)

.PHONY: install-deps
install-deps: install-py-deps install-js-deps

.PHONY: install-py-deps
install-py-deps:
	pip install -U -e .

.PHONY: install-js-deps
install-js-deps:
	npm install

.PHONY: tests-py
tests-py: install-deps
	DJANGO_SETTINGS_MODULE=inboxen.tests.settings$(MAKE) static-local
	./manage.py test

.PHONY: tests-py-coverage
tests-py-coverage: install-deps
	DJANGO_SETTINGS_MODULE=inboxen.tests.settings $(MAKE) static-local
	pip install coverage
	coverage run --branch ./manage.py test
	coverage report
	coverage html
	coverage xml

.PHONY: tests-js
tests-js: install-deps
	npx grunt tests

.PHONY: update-js-requirements
update-js-requirements:
	npm update
	npm audit fix

.PHONY: static
static:
	npx grunt

.PHONY: static-local
static-local: static
	./manage.py compilemessages
	./manage.py collectstatic --clear --noinput

.PHONY: release
release: install-deps
	[[ -z `git status --porcelain` ]] || (echo "git repo is dirty, commit your changes first!"; exit 1)
	_scripts/release-prep.sh
	$(MAKE) static
	# maybe in the future
	#python setup.py sdist
	#twine check dist/*
	#twine upload dist/*

.PHONY: version
version:
	git describe --dirty
