FROM frolvlad/alpine-python3

VOLUME /app/

WORKDIR /app/

ADD ./ /app/

RUN pip3 install -r /app/requirements.txt  && \
    python3 /app/setup.py build && \
    python3 /app/setup.py install

# Install Test suite requirements and helpers, not required for typical usage.
RUN apk update && \
    apk add bash sqlite && \
    pip3 install -r /app/tests/requirements.txt

CMD tail -f /dev/null