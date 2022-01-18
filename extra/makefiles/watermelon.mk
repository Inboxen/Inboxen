
.PHONY: install-watermelon-py-deps
install-watermelon-py-deps:
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
	pip-sync extra/requirements/watermelon.inboxen.org.txt || pip install -r extra/requirements/watermelon.inboxen.org.txt

.PHONY: install-watermelon-deps
install-watermelon-deps: install-watermelon-py-deps install-js-deps
	$(warning This command is very specific to inboxen.org. It will be removed in the near future.)
