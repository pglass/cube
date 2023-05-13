SHELL := bash

.PHONY: test dist bump test-release release clean-dist clean

VENV_EXE=python3 -m virtualenv
VENV=.venv
VENV_ACTIVATE=. $(VENV)/bin/activate
BUMPTYPE=patch

$(VENV):
	$(VENV_EXE) $(VENV)
	$(VENV_ACTIVATE); pip install tox ruff bump2version twine wheel 'readme_renderer[md]'

lint: $(VENV)
	$(VENV_ACTIVATE); ruff .

test: $(VENV)
	$(VENV_ACTIVATE); python tests/test.py

test-all: $(VENV)
	$(VENV_ACTIVATE); tox

dist: clean-dist $(VENV)
	$(VENV_ACTIVATE); python setup.py sdist bdist_wheel
	ls -ls dist
	tar tzf dist/*.tar.gz
	$(VENV_ACTIVATE); twine check dist/*

bump: $(VENV)
	$(VENV_ACTIVATE); bump2version $(BUMPTYPE)
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
