# Note that these default values are *not* used in travis builds
# To update the automatically built container images, you must update .travs.yml
ARG img_user=amd64
ARG img_repo=debian
ARG img_tag=10

FROM ${img_user}/${img_repo}:${img_tag}

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy

COPY . /dripline-python
RUN pip3 install /dripline-python
