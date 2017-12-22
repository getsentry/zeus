CPUS ?= $(shell sysctl -n hw.ncpu || echo 1)
MAKEFLAGS += --jobs=$(CPUS)

develop: setup-git install-requirements

upgrade: install-requirements
	createdb -E utf-8 zeus || true
	zeus db upgrade

setup-git:
	pip install pre-commit==0.15.0
	pre-commit install
	git config branch.autosetuprebase always
	git config --bool flake8.strict true
	cd .git/hooks && ln -sf ../../hooks/* ./

install-requirements: install-python-requirements install-js-requirements

install-python-requirements:
	pip install "setuptools>=17.0"
	pip install "pip>=9.0.0,<10.0.0"
	pip install -e .
	pip install "file://`pwd`#egg=zeus[tests]"
	pip install -e git+https://github.com/pallets/werkzeug.git@8eb665a94aea9d9b56371663075818ca2546e152#egg=werkzeug

install-js-requirements:
	yarn install

test:
	py.test tests

reset-db:
	$(MAKE) drop-db
	$(MAKE) create-db
	zeus db upgrade

drop-db:
	dropdb --if-exists zeus

create-db:
	createdb -E utf-8 zeus

build-docker-image:
	docker build -t zeus .

run-docker-image:
	docker rm zeus || exit 0
	docker run  -d -p 8080:8080/tcp -v ~/.zeus:/workspace --name zeus zeus
