.PHONY: help
help: ## help message, list all command
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: install
install: ## install dependencies into .venv via uv
	uv sync --all-extras --group dev

.PHONY: dev
dev: ## run connector
	uv run spotifyconnector

.PHONY: test
test: ## run all tests
	uv run pytest tests/

.PHONY: test-verbose
test-verbose: ## run tests with verbose output
	uv run pytest tests/ -v

.PHONY: test-fast
test-fast: ## run tests excluding slow ones
	uv run pytest tests/ -m "not slow"

.PHONY: test-connection
test-connection: ## run only connection handling tests
	uv run pytest tests/test_connection_handling.py -v

.PHONY: clean
clean: ## clean build files
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache/
	rm -rf reports/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: build
build: clean ## build sdist and wheel with uv
	uv build

.PHONY: publish
publish: build ## publish package to pypi
	uv run twine upload --username __token__ dist/*

.PHONY: lint
lint: ## run lint
	uv run black spotifyconnector
	uv run flake8 spotifyconnector
	uv run pylint $$(git ls-files '*.py') --rcfile=./pylintrc

.PHONY: security-check
security-check: ## run comprehensive security check (bandit, safety, semgrep)
	@echo "Running Security Analysis..."
	@echo "1. Running Safety check for known vulnerabilities..."
	uv run safety --disable-optional-telemetry check --short-report || true
	@echo "2. Running Bandit security linter..."
	uv run bandit -r spotifyconnector/ || true
	@echo "3. Running Semgrep security scanner..."
	uv run semgrep --config=auto spotifyconnector/ || true
	@echo "Security analysis completed."

.PHONY: security-check-reports
security-check-reports: ## run security check and generate JSON reports
	@echo "Running Security Analysis with report generation..."
	@mkdir -p reports
	@echo "1. Running Safety check for known vulnerabilities..."
	uv run safety --disable-optional-telemetry check --json --output reports/safety-report.json || true
	uv run safety --disable-optional-telemetry check --short-report || true
	@echo "2. Running Bandit security linter..."
	uv run bandit -r spotifyconnector/ -f json -o reports/bandit-report.json || true
	uv run bandit -r spotifyconnector/
	@echo "3. Running Semgrep security scanner..."
	uv run semgrep --config=auto spotifyconnector/ --json --output=reports/semgrep-report.json || true
	uv run semgrep --config=auto spotifyconnector/
	@echo "Security reports generated in reports/ directory"

.PHONY: init
init: install ## init virtual python env