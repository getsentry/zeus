develop: setup-git install-requirements

upgrade: install-requirements
	createdb -E utf-8 zeus || true
	pipenv run zeus db upgrade

setup-git:
	pip install "pre-commit>=1.10.1,<1.11.0"
	pre-commit install
	git config branch.autosetuprebase always
	git config --bool flake8.strict true
	cd .git/hooks && ln -sf ../../hooks/* ./

install-requirements: install-python-requirements install-js-requirements

install-python-requirements:
	pipenv install --dev

install-js-requirements:
	yarn install

test:
	pipenv run py.test

reset-db:
	$(MAKE) drop-db
	$(MAKE) create-db
	pipenv run zeus db upgrade

drop-db:
	dropdb --if-exists zeus

create-db:
	createdb -E utf-8 zeus

build-docker-image:
	docker build -t zeus .

run-docker-image:
	docker rm zeus || exit 0
	docker run --init -d -p 8080:8080/tcp -v ~/.zeus:/workspace --name zeus zeus
