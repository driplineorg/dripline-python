# Note that these default values are *not* used in travis builds
# To update the automatically built container images, you must update .travs.yml
ARG img_user=amd64
ARG img_repo=python
ARG img_tag=3.6

FROM ${img_user}/${img_repo}:${img_tag}

COPY . /dripline-python
RUN pip install /dripline-python
