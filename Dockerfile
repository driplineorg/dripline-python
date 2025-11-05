ARG img_user=ghcr.io/driplineorg
ARG img_repo=dripline-cpp
#ARG img_tag=dlcpp-hf2.10.8
ARG img_tag=v2.10.8

FROM ${img_user}/${img_repo}:${img_tag} AS deps

## would prefer not to do this, just run ldconfig after the build to get things
## into the ld.so.conf cache... use this only when developing and adding libs
ENV LD_LIBRARY_PATH=/usr/local/lib

RUN apt-get update && \
    apt-get clean && \
    apt-get --fix-missing  -y install \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install ipython pytest &&\
    pip install aiohttp sqlalchemy psycopg2 PyYAML uuid asteval colorlog

FROM deps

COPY . /usr/local/src_py/

RUN pip install -v /usr/local/src_py

#RUN cd /usr/local/src_py &&\
#    python setup.py install
RUN ldconfig

