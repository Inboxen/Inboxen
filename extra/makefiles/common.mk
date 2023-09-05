##
#	Inboxen.org specific tasks
##

TODAY := $(shell date +'%-Y.%-m.%-d.%-H.%-M.%-S' -u)
server ?= $(shell hostname --short)

# common deployment stuff
.PHONY: common-deploy
common-deploy:
	$(MAKE) install-$(server)-deps
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
	echo git push origin deploy-$(TODAY)
	echo git push
