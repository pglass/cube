.PHONY: test dist bump test-release release clean-dist clean

VENV=.venv
VENV_ACTIVATE=. $(VENV)/bin/activate
BUMPTYPE=patch

$(VENV):
	virtualenv $(VENV)
	$(VENV_ACTIVATE); pip install tox bumpversion twine wheel 'readme_renderer[md]'

test: $(VENV)
	$(VENV_ACTIVATE); tox

dist: clean-dist $(VENV)
	$(VENV_ACTIVATE); python setup.py sdist bdist_wheel
	ls -ls dist
	tar tzf dist/*.tar.gz
	$(VENV_ACTIVATE); twine check dist/*

bump: $(VENV)
	$(VENV_ACTIVATE); bumpversion $(BUMPTYPE)
	git show -q
	@echo
	@echo "SUCCESS: Version was bumped and committed"

test-release: clean test dist
	$(VENV_ACTIVATE); twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: clean test dist
	$(VENV_ACTIVATE); twine upload dist/*

clean-dist:
	rm -rf dist
	rm -rf *.egg-info

clean: clean-dist
	rm -rf $(VENV) .tox
