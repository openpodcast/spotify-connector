.PHONY: dev
dev:
	python -m spotifyconnector

.PHONY: publish
publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*