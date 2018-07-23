# Use an official Python runtime as a parent image
FROM python:3.7-slim-stretch

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r zeus && useradd -r -m -g zeus zeus

ENV NVM_DIR /usr/local/nvm
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

# install nvm, node, and npm
# gpg keys listed at https://github.com/nodejs/node
COPY .nvmrc /usr/src/zeus/
ENV YARN_VERSION 1.7.0
RUN set -x \
    && export NODE_VERSION=$(cat /usr/src/zeus/.nvmrc) \
    && export GNUPGHOME="$(mktemp -d)" \
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
    ; do \
      gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key"; \
    done \
    && wget --no-verbose "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz" \
    && wget --no-verbose "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
    && gpg --verify SHASUMS256.txt.asc \
    && grep " node-v$NODE_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
    && tar -xzf "node-v$NODE_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
    && rm -rf "$GNUPGHOME" "node-v$NODE_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc \
    && apt-get purge -y --auto-remove dirmngr gnupg \
    && npm install -g yarn@$YARN_VERSION \
    && npm cache clear --force

COPY requirements-base.txt /usr/src/zeus/
RUN pip install -r requirements-base.txt

COPY requirements-dev.txt /usr/src/zeus/
RUN pip install -r requirements-dev.txt

COPY requirements-test.txt /usr/src/zeus/
RUN pip install -r requirements-test.txt

RUN pip install -e git+https://github.com/pallets/werkzeug.git@8eb665a94aea9d9b56371663075818ca2546e152#egg=werkzeug

COPY yarn.lock /usr/src/zeus/
COPY package.json /usr/src/zeus/
RUN yarn install --production --pure-lockfile --ignore-optional \
    && yarn cache clean

COPY . /usr/src/zeus
RUN pip install -e .
RUN node_modules/.bin/webpack -p

ENV WORKSPACE_ROOT /workspace
ENV REPO_ROOT /workspace/repos
RUN mkdir -p $WORKSPACE_ROOT $REPO_ROOT

ENV PATH /usr/src/zeus/bin:$PATH

# Make port 8080 available to the world outside this container
EXPOSE 8080
EXPOSE 8090

VOLUME /workspace

ENTRYPOINT ["docker-entrypoint"]

# Run Zeus
CMD ["zeus", "run", "--host=0.0.0.0", "--port=8080"]
