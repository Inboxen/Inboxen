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
