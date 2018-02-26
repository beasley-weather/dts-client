FROM python:3.6-slim

ENV PASS="pass"
ENV USER="badger"

ENV WEEWX_DATABASE="/var/lib/weewx/weewx.sdb"
ENV DTS_INTERVAL=600
ENV DTS_SERVER='localhost'

RUN useradd -m $USER
RUN echo $USER:$PASS | chpasswd

# Packages
RUN apt-get update && apt-get -y install curl wget git
RUN pip install pipenv

# App
USER badger
WORKDIR /home/$USER
RUN mkdir dts-client && cd dts-client
RUN curl -L https://api.github.com/repos/beasley-weather/dts-client/tarball | \
    tar xz --strip-components=1
USER root
RUN pipenv install --system --skip-lock

# Cleanup
# UNCOMMENT BEFORE PROD
# RUN apt-get -y purge curl git wget && apt-get -y autoclean && apt-get -y autoremove

USER badger
ENTRYPOINT python -m dts_client
