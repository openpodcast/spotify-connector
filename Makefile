.PHONY: help
help: ## help message, list all command
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: dev
dev: ## run connector
	pipenv run spotifyconnector

.PHONY: clean
clean: ## clean build files
	rm -rf build dist *.egg-info

.PHONY: publish
publish: clean ## publish package to pypi
	pipenv run python setup.py sdist bdist_wheel
	twine upload --username __token__ dist/*

.PHONY: lint
lint: ## run lint
	pipenv run black spotifyconnector
	pipenv run flake8 spotifyconnector
	pipenv run pylint $$(git ls-files '*.py') --rcfile=./pylintrc

.PHONY: init
init: ## init virtual pyhton env
	pipenv install --dev
