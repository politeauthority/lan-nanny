FROM debian:bullseye-slim

VOLUME /app/
WORKDIR /app/
ADD ./ /app/

# Install apt requirements
RUN apt-get update && \
    apt-get install -y \
        python3-dev \
        libpython3-dev \
        python3-pip \
        python3-mysqldb \
        nmap

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