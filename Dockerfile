FROM python:rc-alpine3.12

VOLUME /app/
WORKDIR /app/
ADD ./ /app
ENV LAN_NANNY_CONFIG=docker
ENV LAN_NANNY_DB_HOST=lan-nanny-mysql
ENV LAN_NANNY_DB_PORT=3306
ENV LAN_NANNY_DB_NAME=lan_nanny
ENV LAN_NANNY_DB_USER=root
ENV LAN_NANNY_DB_PASS=pass
ENV LAN_NANNY_STATIC_PATH='/static'
ENV LAN_NANNY_APP_PORT=5000
ENV LAN_NANNY_LOG_DIR=/app/logs
ENV LAN_NANNY_TMP_DIR=/tmp/lan_nanny
ENV LAN_NANNY_GIT_BRANCH=0.0.1


# Install apk requirements
RUN apk update
RUN apk add --virtual \
    build-deps \
    gcc \
    python3-dev \
    musl-dev \
    mariadb-dev \
    py3-pip \
    bash \
    git

# Install Lan Nanny
RUN cd /app && \
    pip3 install -r /app/requirements.txt  && \
    python3 /app/setup.py build && \
    python3 /app/setup.py install && \
    mkdir -p /app/logs && \
    mkdir -p /tmp/lan_nanny