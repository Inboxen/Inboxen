.PHONY: install-dev-deps
install-dev-deps: install-dev-py-deps install-js-deps

.PHONY: install-dev-py-deps
install-dev-py-deps:
	pip-sync requirements-dev.txt || pip install -r requirements-dev.txt

.PHONY: install-js-deps
install-js-deps:
	npm install

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
# Daemon control
##

.PHONY: celery-stop
celery-stop:
	-pkill -f "celery worker" || echo "No celery worker found"

.PHONY: celery-start
celery-start:
	DJANGO_SETTINGS_MODULE=inboxen.settings celery -A inboxen worker -l warn -B -E -D -f celery.log

.PHONY: salmon-stop
salmon-stop:
	./manage.py router --stop

.PHONY: salmon-start
salmon-start:
	./manage.py router --start

##
#	Inboxen.org specific tasks
##

.PHONY: install-watermelon-py-deps
install-watermelon-py-deps:
	echo "Warning: this command is very specific to inboxen.org. It will be removed in the near future."
	pip-sync extra/requirements/watermelon.inboxen.org.txt || pip install -r extra/requirements/watermelon.inboxen.org.txt

.PHONY: install-watermelon-deps
install-watermelon-deps: install-watermelon-py-deps install-js-deps
	echo "Warning: this command is very specific to inboxen.org. It will be removed in the near future."

# common deployment stuff
.PHONY: common-deploy
common-deploy:
	$(MAKE) install-watermelon-deps
	mkdir -p logs run
	./manage.py compilemessages
	./manage.py check --deploy
	./manage.py collectstatic --no-input
	touch inboxen/wsgi.py
	$(MAKE) celery-start salmon-start

.PHONY: deploy-%
deploy-%:
	echo "Warning: this command is very specific to inboxen.org. It will be removed in the near future."
	git verify-tag $@
	$(MAKE) celery-stop salmon-stop
	git checkout $@
	$(MAKE) common-deploy

.PHONY: dev-deploy
dev-deploy:
	echo "Warning: this command is very specific to inboxen.org. It will be removed in the near future."
	$(MAKE) celery-stop salmon-stop
	git describe --dirty
	$(MAKE) common-deploy
