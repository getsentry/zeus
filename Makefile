CPUS ?= $(shell sysctl -n hw.ncpu || echo 1)
MAKEFLAGS += --jobs=$(CPUS)

develop: setup-git install-requirements

upgrade: install-requirements
	bin/upgrade

setup-git:
	git config branch.autosetuprebase always
	cd .git/hooks && ln -sf ../../hooks/* ./

install-requirements: install-python-requirements install-js-requirements

install-python-requirements:
	pip install "setuptools>=17.0"
	pip install "pip>=9.0.0,<10.0.0"
	pip install -e .
	pip install "file://`pwd`#egg=zeus[tests]"

install-js-requirements:
	yarn install

test:
	py.test tests --tb=short
