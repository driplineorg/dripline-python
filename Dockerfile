ARG img_user=ghcr.io/driplineorg
ARG img_repo=dripline-cpp
#ARG img_tag=hotfix_2.6.2
ARG img_tag=v2.8.5
#ARG img_arch=arm

FROM ${img_user}/${img_repo}:${img_tag}
#FROM ${img_user}/${img_repo}:${img_tag}-${img_arch}
#FROM dlc_temp

## would prefer not to do this, just run ldconfig after the build to get things
## into the ld.so.conf cache... use this only when developing and adding libs
ENV LD_LIBRARY_PATH /usr/local/lib

RUN /usr/local/bin/python -m pip install --upgrade pip &&\
    pip install ipython &&\
    pip install pytest

COPY module_bindings /usr/local/src_py/module_bindings
COPY dripline /usr/local/src_py/dripline
COPY bin /usr/local/src_py/bin
COPY .git /usr/local/src_py/.git
COPY setup.py /usr/local/src_py/setup.py
COPY CMakeLists.txt /usr/local/src_py/CMakeLists.txt
COPY tests /usr/local/src_py/tests

RUN pip install /usr/local/src_py

#RUN cd /usr/local/src_py &&\
#    python setup.py install
RUN ldconfig

