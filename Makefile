.PHONY: dev
dev:
	python -m spotifyconnector

.PHONY: clean
clean:
	rm -rf build dist *.egg-info

.PHONY: publish
publish: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*