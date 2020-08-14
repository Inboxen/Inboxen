##
#	Inboxen.org specific tasks
##

TODAY := $(shell date "+%Y-%m-%dT%H-%M-%S" -u)

.PHONY: setup-node
setup-node:
	nodeenv -p -n 8.16.0 --with-npm

.PHONY: install-watermelon-py-deps
install-watermelon-py-deps:
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
	pip-sync extra/requirements/watermelon.inboxen.org.txt || pip install -r extra/requirements/watermelon.inboxen.org.txt

.PHONY: install-watermelon-deps
install-watermelon-deps: install-watermelon-py-deps install-js-deps
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)

# common deployment stuff
.PHONY: common-deploy
common-deploy:
	$(MAKE) install-watermelon-deps
	mkdir -p logs run
	$(MAKE) static
	./manage.py migrate
	./manage.py check --deploy
	touch inboxen/wsgi.py
	$(MAKE) celery-start salmon-start

.PHONY: deploy-%
deploy-%:
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
	git fetch --prune
	git verify-tag $@
	$(MAKE) celery-stop salmon-stop
	git checkout $@
	$(MAKE) common-deploy

.PHONY: dev-deploy
dev-deploy:
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
	$(MAKE) celery-stop salmon-stop
	git describe --dirty
	$(MAKE) common-deploy


.PHONY: make-deploy
make-deploy:
	[[ -z `git status --porcelain` ]] || (echo "git repo is dirty, commit your changes first!"; exit 1)
	extra/scripts/release-prep.sh $(TODAY)
	git push origin deploy-$(TODAY)
	git push
