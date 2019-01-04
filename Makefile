develop: setup-git install-requirements

upgrade: install-requirements
	createdb -E utf-8 zeus || true
	poetry run zeus db upgrade

setup-git:
	pip install "pre-commit>=1.12.0,<1.13.0"
	pre-commit install
	git config branch.autosetuprebase always
	git config --bool flake8.strict true
	cd .git/hooks && ln -sf ../../hooks/* ./

install-requirements: install-python-requirements install-js-requirements

install-python-requirements:
	poetry install --extras=test

install-js-requirements:
	yarn install

test:
	poetry run py.test

db:
	$(MAKE) create-db
	poetry run zeus db upgrade

drop-db:
	dropdb --if-exists zeus

create-db:
	createdb -E utf-8 zeus

reset-db: drop-db db

build-docker-image:
	docker build -t zeus .

run-docker-image:
	docker rm zeus || exit 0
	docker run --init -d -p 8080:8080/tcp -v ~/.zeus:/workspace --name zeus zeus
