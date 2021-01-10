FROM python:3.6-slim

USER root
WORKDIR /root/
COPY . /root/

RUN mkdir /root/.pip/ \
    && mv pip.conf /root/.pip/ \
    && pip3.6 install -r requirements.txt

EXPOSE 8888
ENTRYPOINT ["/bin/sh", "-c", "exec /usr/local/bin/python main.py --url $URL --user $USER --password $PASSWORD"]
