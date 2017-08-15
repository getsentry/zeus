# Use an official Python runtime as a parent image
FROM python:3.6-slim

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r zeus && useradd -r -m -g zeus zeus

ENV PYTHONUNBUFFERED 1
ENV NODE_ENV production

# Sane defaults for pip
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN mkdir -p /usr/src/zeus
WORKDIR /usr/src/zeus

RUN set -x \
    && apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        git \
        libffi-dev \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# grab gosu for easy step-down from root
RUN set -x \
    && export GOSU_VERSION=1.10 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true \
    && apt-get purge -y --auto-remove wget

# grab tini for signal processing and zombie killing
RUN set -x \
    && export TINI_VERSION=0.15.0 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini" \
    && wget -O /usr/local/bin/tini.asc "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys 6380DC428747F6C393FEACA59A84159D7001A4E5 \
    && gpg --batch --verify /usr/local/bin/tini.asc /usr/local/bin/tini \
    && rm -r "$GNUPGHOME" /usr/local/bin/tini.asc \
    && chmod +x /usr/local/bin/tini \
    && tini -h \
    && apt-get purge -y --auto-remove wget

# gpg keys listed at https://github.com/nodejs/node
RUN set -x \
    && export NODE_VERSION=8.1.4 \
    && export YARN_VERSION=0.27.5 \
    && export GNUPGHOME="$(mktemp -d)" \
    && for key in \
      9554F04D7259F04124DE6B476D5A82AC7E37093B \
      94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
      0034A06D9D9B0064CE8ADF6BF1747F4AD2306D93 \
      FD3A5288F042B6850C66B31F09FE44734EB7990E \
      71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
      DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
      B9AE9905FFD7803F25714661B63B535A4C206CA9 \
      C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
    ; do \
      gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key"; \
    done \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz" \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
    && gpg --verify SHASUMS256.txt.asc \
    && grep " node-v$NODE_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
    && tar -xzf "node-v$NODE_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
    && rm -r "$GNUPGHOME" "node-v$NODE_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc \
    && apt-get purge -y --auto-remove wget \
    && npm install -g yarn@$YARN_VERSION \
    && npm cache clear --force

COPY requirements-base.txt /usr/src/zeus/
RUN pip install -r requirements-base.txt

COPY requirements-dev.txt /usr/src/zeus/
RUN pip install -r requirements-dev.txt

COPY requirements-test.txt /usr/src/zeus/
RUN pip install -r requirements-test.txt

COPY yarn.lock /usr/src/zeus/
COPY package.json /usr/src/zeus/
RUN yarn install --production --pure-lockfile --ignore-optional \
    && yarn cache clean

COPY . /usr/src/zeus
RUN pip install -e .
RUN node_modules/.bin/webpack -p

ENV REPO_ROOT /workspace/repos
RUN mkdir -p $REPO_ROOT

ENV PATH /usr/src/zeus/bin:$PATH

# Make port 8080 available to the world outside this container
EXPOSE 8080

VOLUME /workspace

ENTRYPOINT ["docker-entrypoint"]

# Run Zeus
CMD ["zeus", "run", "--host=0.0.0.0", "--port=8080"]
