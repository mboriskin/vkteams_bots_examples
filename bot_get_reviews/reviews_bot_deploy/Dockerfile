FROM almalinux:9-default-amd64

ARG VERSION=0.0.1
ARG PY_VERSION=3.11.7-1
ARG PY_VERSION_SHORT=3.11
ARG PIP3_VERSION=22.3.1

ARG STAGE
ARG CHAT

ARG VKT_BOT_TOKEN
ARG RUSTORE_PROJECT_KEY
ARG RUSTORE_PROJECT_KEY_ID

LABEL "maintainer"="Makary Boriskin <m.boriskin>" \
      "app"="reviews_bot" \
      "version"="${VERSION}" \
      "descriprion"="An image for running reviews_bot"

COPY etc/pip.conf /etc/pip.conf

COPY etc/config.yaml.j2 /etc/config.yaml.j2

RUN echo "VKT_BOT_TOKEN: ${VKT_BOT_TOKEN}" >> /etc/config.yaml.j2 && \
    echo "RUSTORE_PROJECT_KEY: ${RUSTORE_PROJECT_KEY}" >> /etc/config.yaml.j2 && \
    echo "RUSTORE_PROJECT_KEY_ID: ${RUSTORE_PROJECT_KEY_ID}" >> /etc/config.yaml.j2 && \
    echo "VKT_REVIEWS_CHAT: ${CHAT}" >> /etc/config.yaml.j2

RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime

RUN yum install -y python${PY_VERSION_SHORT}-${PY_VERSION}.el9_4.1.x86_64 && \
    python${PY_VERSION_SHORT} -m ensurepip --upgrade && \
    python${PY_VERSION_SHORT} -m pip install pip==${PIP3_VERSION}
