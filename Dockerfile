# Use an official Python runtime as a parent image
FROM python:3.7-slim-stretch

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r zeus && useradd -r -m -g zeus zeus

ENV PATH /usr/src/zeus/bin:/root/.poetry/bin:$PATH

ENV NODE_ENV production

ENV PYTHONUNBUFFERED 1

# Sane defaults for pip
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN mkdir -p /usr/src/zeus
WORKDIR /usr/src/zeus

RUN set -ex \
  && apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  curl \
  gcc \
  git \
  gosu \
  libffi-dev \
  libpq-dev \
  libxml2-dev \
  libxslt-dev \
  openssl \
  ssh \
  wget \
  && rm -rf /var/lib/apt/lists/*

# install node and yarn
# gpg keys listed at https://github.com/nodejs/node
ARG YARN_VERSION=1.13.0
ENV YARN_VERSION $YARN_VERSION
ARG NODE_VERSION=8.11.3
ENV NODE_VERSION $NODE_VERSION
RUN set -x \
  && export GNUPGHOME="$(mktemp -d)" \
  && export NPM_CONFIG_CACHE="$(mktemp -d)" \
  && apt-get update && apt-get install -y --no-install-recommends dirmngr gnupg && rm -rf /var/lib/apt/lists/* \
  && for key in \
  94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
  B9AE9905FFD7803F25714661B63B535A4C206CA9 \
  77984A986EBC2AA786BC0F66B01FBB92821C587A \
  71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
  FD3A5288F042B6850C66B31F09FE44734EB7990E \
  8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 \
  C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
  DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
  9554F04D7259F04124DE6B476D5A82AC7E37093B \
  93C7E9E91B49E432C2F75674B0A78B0A6C481CF6 \
  56730D5401028683275BD23C23EFEFE93C4CFFFE \
  114F43EE0176B71C7BC219DD50A3051F888C628D \
  7937DFD2AB06298B2293C3187D33FF9D0246406D \
  ; do \
  gpg --batch --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys "$key" || \
  gpg --batch --keyserver hkp://ipv4.pool.sks-keyservers.net --recv-keys "$key" || \
  gpg --batch --keyserver hkp://pgp.mit.edu:80 --recv-keys "$key" ; \
  done \
  && wget --no-verbose "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz" \
  && wget --no-verbose "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
  && gpg --batch --verify SHASUMS256.txt.asc \
  && grep " node-v$NODE_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
  && tar -xzf "node-v$NODE_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
  && rm -rf "$GNUPGHOME" "node-v$NODE_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc \
  && apt-get purge -y --auto-remove dirmngr gnupg \
  && npm install -g yarn@$YARN_VERSION \
  && rm -r "$NPM_CONFIG_CACHE"

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/0.12.14/get-poetry.py | python \
  && poetry config settings.virtualenvs.create false

COPY pyproject.toml /usr/src/zeus/
COPY poetry.lock /usr/src/zeus/
RUN poetry install --no-dev

COPY yarn.lock /usr/src/zeus/
COPY package.json /usr/src/zeus/
RUN export YARN_CACHE_FOLDER="$(mktemp -d)" \
  && yarn install --production --pure-lockfile --ignore-optional \
  && rm -r "$YARN_CACHE_FOLDER"

COPY . /usr/src/zeus
# # we run poetry install again to ensure the 'zeus' module gets installed
RUN poetry install --no-dev
RUN node_modules/.bin/webpack -p

ENV WORKSPACE_ROOT /workspace
ENV REPO_ROOT /workspace/repos
RUN mkdir -p $WORKSPACE_ROOT $REPO_ROOT

ARG BUILD_REVISION
ENV BUILD_REVISION $BUILD_REVISION

# Make port 8080 available to the world outside this container
EXPOSE 8080
EXPOSE 8090

VOLUME /workspace

ENTRYPOINT ["docker-entrypoint"]

# Run Zeus
CMD ["zeus", "run", "--host=0.0.0.0", "--port=8080"]
