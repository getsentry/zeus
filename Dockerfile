# Use an official Python runtime as a parent image
FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

ENV NODE_ENV production

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN set -x \
    && apt-get -qy update \
    && apt-get -qy install -y --no-install-recommends \
        gcc git python3-all python3-all-dev python3-pip \
        libxml2-dev libxslt1-dev libpq-dev libffi-dev

RUN set -x \
    && export NODE_VERSION=8.1.4 \
    && export GNUPGHOME="$(mktemp -d)" \
    # gpg keys listed at https://github.com/nodejs/node
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
    && apt-get purge -y --auto-remove wget

RUN npm install -g yarn

COPY yarn.lock /usr/src/app/
COPY package.json /usr/src/app/
RUN yarn install

COPY requirements-base.txt /usr/src/app/
RUN pip install -r requirements-base.txt

COPY requirements-dev.txt /usr/src/app/
RUN pip install -r requirements-dev.txt

COPY requirements-test.txt /usr/src/app/
RUN pip install -r requirements-test.txt

COPY . /usr/src/app
RUN pip install -e .
RUN node_modules/.bin/webpack --config=config/webpack.config.dev.js

# Make port 8080 available to the world outside this container
EXPOSE 5000

# Run Zeus
CMD ["zeus", "run", "-p 5000"]
