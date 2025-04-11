FROM almalinux:9-default-amd64

ARG VERSION=0.0.1
ARG PY_VERSION=3.11.7-1
ARG PY_VERSION_SHORT=3.11
ARG PIP3_VERSION=22.3.1
ARG SETUPTOOLS_VERSION=65.5.0

LABEL "maintainer"="Makary Boriskin <m.boriskin>" \
      "app"="wheelbuild" \
      "version"="${VERSION}" \
      "descriprion"="A simple image for building python wheels"

COPY ./etc/pip.conf /etc/pip.conf

RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime

RUN yum install -y gcc libffi-devel python${PY_VERSION_SHORT}-${PY_VERSION}.el9_4.1.x86_64 && \
    python${PY_VERSION_SHORT} -m ensurepip --upgrade && \
    python${PY_VERSION_SHORT} -m pip install pip==${PIP3_VERSION} && \
    python${PY_VERSION_SHORT} -m pip install setuptools==${SETUPTOOLS_VERSION} wheel==0.37.1 twine==4.0.2
