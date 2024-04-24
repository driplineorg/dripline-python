ARG img_user=ghcr.io/driplineorg
ARG img_repo=dripline-python
ARG img_tag=latest-dev

FROM ${img_user}/${img_repo}:${img_tag}

RUN apt-get update && \
    apt-get clean && \
    apt-get --fix-missing  -y install \
        bats && \
    rm -rf /var/lib/apt/lists/*
