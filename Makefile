.PHONY: dev
dev:
	pipenv run spotifyconnector

.PHONY: clean
clean:
	rm -rf build dist *.egg-info

.PHONY: publish
publish: clean
	pipenv run python setup.py sdist bdist_wheel
	twine upload dist/*