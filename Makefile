.PHONY: help
help: ## help message, list all command
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: dev
dev:
	pipenv run spotifyconnector

.PHONY: clean
clean:
	rm -rf build dist *.egg-info

.PHONY: publish
publish: clean
	pipenv run python setup.py sdist bdist_wheel
	twine upload --username mre0 dist/*

.PHONY: lint
lint: ## run lint
	pipenv run black spotifyconnector
	pipenv run flake8 spotifyconnector
	pipenv run pylint $$(git ls-files '*.py')

.PHONY: init
init:
	pipenv install --dev