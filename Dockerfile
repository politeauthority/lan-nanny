FROM debian:bullseye-slim

VOLUME /app/
WORKDIR /app/
ADD ./ /app/
ENV LAN_NANNY_APP_PORT=5050
ENV LAN_NANNY_CONFIG=docker
ENV LAN_NANNY_DB_HOST=lan-nanny-mysql
ENV LAN_NANNY_DB_PORT=3306
ENV LAN_NANNY_DB_NAME=lan_nanny
ENV LAN_NANNY_DB_USER=root
ENV LAN_NANNY_DB_PASS=pass
ENV LAN_NANNY_APP_PORT=5000

# Install apt requirements
RUN apt-get update && \
    apt-get install -y \
        python3-dev \
        libpython3-dev \
        python3-pip \
        python3-mysqldb \
        vim \
        nmap \
        arp-scan

# Install Lan Nanny
RUN pip3 install -r /app/requirements.txt  && \
    python3 /app/setup.py build && \
    python3 /app/setup.py install

# Install test suite tools (should be optional)
RUN apt-get install -y \
        screen \
        inetutils-ping && \
    pip3 install -r /app/tests/requirements.txt

CMD tail -f /dev/null