# build with
#   docker build -t some_tag_storage-admin -f Dockerfile ../..
FROM ubuntu:jammy

# Update apt sources in china
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# System deps:
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y rsync unzip wget curl glances \
    && rm -rf /var/lib/apt/lists/*
RUN curl https://rclone.org/install.sh | bash

ENTRYPOINT ["sleep", "infinity"]
