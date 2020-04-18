FROM frolvlad/alpine-python3

VOLUME /app/

WORKDIR /app/

ADD ./ /app/

RUN  apk update && \
    apk add bash && \
    pip3 install -r /app/requirements.txt && \
    pip3 install -r /app/tests/requirements.txt

RUN  python3 /app/setup.py build && \
    python3 /app/setup.py install

CMD tail -f /dev/null