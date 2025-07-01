.PHONY: help
help: ## help message, list all command
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: dev
dev: ## run connector
	pipenv run spotifyconnector

.PHONY: test
test: ## run all tests
	python -m pytest tests/

.PHONY: test-verbose
test-verbose: ## run tests with verbose output
	python -m pytest tests/ -v

.PHONY: test-fast
test-fast: ## run tests excluding slow ones
	python -m pytest tests/ -m "not slow"

.PHONY: test-connection
test-connection: ## run only connection handling tests
	python -m pytest tests/test_connection_handling.py -v

.PHONY: ci-test
ci-test: ## run tests as in CI environment
	python -m pytest tests/ -v --tb=short --cov=spotifyconnector --cov-report=xml --cov-report=term-missing

.PHONY: ci-lint
ci-lint: ## run linting as in CI environment
	python -m black --check --diff spotifyconnector/ tests/
	python -m isort --check-only --diff spotifyconnector/ tests/
	python -m flake8 spotifyconnector/ --max-line-length=88 --extend-ignore=E203,W503 || echo "flake8 not available, skipping"
	python -m pylint spotifyconnector/ --rcfile=./pylintrc || echo "pylint not available, skipping"

.PHONY: ci-security
ci-security: ## run security checks as in CI environment
	pip install safety bandit
	safety check --short-report
	bandit -r spotifyconnector/

.PHONY: format
format: ## format code with black and isort
	black spotifyconnector/ tests/
	isort spotifyconnector/ tests/

.PHONY: clean
clean: ## clean build files
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: publish
publish: clean ## publish package to pypi
	pipenv run python setup.py sdist bdist_wheel
	twine upload --username mre0 dist/*

.PHONY: lint
lint: ## run lint
	pipenv run black spotifyconnector
	pipenv run flake8 spotifyconnector
	pipenv run pylint $$(git ls-files '*.py') --rcfile=./pylintrc

.PHONY: init
init: ## init virtual pyhton env
	pipenv install --dev
