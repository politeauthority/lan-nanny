FROM politeauthority/lan-nanny:latest

VOLUME /app/
WORKDIR /app/
ENV LAN_NANNY_CONFIG=docker
ENV LAN_NANNY_DB_HOST=lan-nanny-mysql
ENV LAN_NANNY_DB_PORT=3306
ENV LAN_NANNY_DB_NAME=lan_nanny
ENV LAN_NANNY_DB_USER=root
ENV LAN_NANNY_DB_PASS=pass
ENV LAN_NANNY_APP_PORT=5050
ENV LAN_NANNY_STATIC_PATH='/static'
ENV LAN_NANNY_LOG_DIR=/app/logs
ENV LAN_NANNY_TMP_DIR=/tmp/lan_nanny
ENV LAN_NANNY_GIT_BRANCH=0.0.1

# Install apt requirements for development
RUN apt-get update && \
    apt-get install -y \
        vim \
        screen \
        inetutils-ping

# Install test suite pip requirements
# RUN pip3 install -r /app/tests/requirements.txt

CMD tail -f /dev/null