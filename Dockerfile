# Use an official Python runtime as a parent image
FROM python:3.9.19-slim-bullseye

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r zeus && useradd -r -m -g zeus zeus

ENV PATH /usr/src/zeus/bin:/root/.local/bin:$PATH

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
  libz-dev \
  openssl \
  ssh \
  wget \
  && rm -rf /var/lib/apt/lists/*

# install node and yarn
# gpg keys listed at https://github.com/nodejs/node
ARG YARN_VERSION=4.1.1
ENV YARN_VERSION $YARN_VERSION
ARG NODE_VERSION=20.0.9
ENV NODE_VERSION $NODE_VERSION
RUN set -x \
  && export GNUPGHOME="$(mktemp -d)" \
  && export NPM_CONFIG_CACHE="$(mktemp -d)" \
  && apt-get update && apt-get install -y --no-install-recommends dirmngr gnupg && rm -rf /var/lib/apt/lists/* \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys 4ED778F539E3634C779C87C6D7062848A1AB005C \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys 141F07595B7B3FFE74309A937405533BE57C7D57 \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys 74F12602B6F1C4E913FAA37AD3A89613643B6201 \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys DD792F5973C6DE52C432CBDAC77ABFA00DDBF2B7 \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys CC68F5A3106FF448322E48ED27F5E38D5B0A215F \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys 8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys 890C08DB8579162FEE0DF9DB8BEAB4DFCF555EF4 \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys C82FA3AE1CBEDC6BE46B9360C43CEC45C17AB93C \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys 108F52B48DB57BB0CC439B2997B01419BD92F80A \
  && gpg --keyserver hkps://keys.openpgp.org --recv-keys A363A499291CBBC940DD62E41F10027AF002F8B0 \
  && wget --no-verbose "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-arm64.tar.gz" \
  && wget --no-verbose "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
  && gpg --batch --verify SHASUMS256.txt.asc \
  && grep " node-v$NODE_VERSION-linux-arm64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
  && tar -xzf "node-v$NODE_VERSION-linux-arm64.tar.gz" -C /usr/local --strip-components=1 \
  && rm -rf "$GNUPGHOME" "node-v$NODE_VERSION-linux-arm64.tar.gz" SHASUMS256.txt.asc \
  && apt-get purge -y --auto-remove dirmngr gnupg \
  && npm install -g yarn \
  && rm -r "$NPM_CONFIG_CACHE"

RUN corepack enable

RUN curl -sSL https://install.python-poetry.org | python3 - \
  && poetry config virtualenvs.create false

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
