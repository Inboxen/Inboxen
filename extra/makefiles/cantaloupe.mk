
.PHONY: install-cantaloupe-py-deps
install-cantaloupe-py-deps:
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
	pip-sync extra/requirements/cantaloupe.inboxen.org.txt || pip install -r extra/requirements/cantaloupe.inboxen.org.txt

.PHONY: install-cantaloupe-deps
install-cantaloupe-deps: install-cantaloupe-py-deps install-js-deps
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
