ARG img_user=driplineorg
ARG img_repo=dripline-cpp
ARG img_tag=v2.4.0
#ARG img_arch=arm

from ${img_user}/${img_repo}:${img_tag}
#from ${img_user}/${img_repo}:${img_tag}-${img_arch}

COPY module_bindings /usr/local/src_py/module_bindings
COPY dripline /usr/local/src_py/dripline
COPY bin /usr/local/src_py/bin
COPY .git /usr/local/src_py/.git
COPY setup.py /usr/local/src_py/setup.py
COPY CMakeLists.txt /usr/local/src_py/CMakeLists.txt
COPY tests /usr/local/src_py/tests

## would prefer not to do this, just run ldconfig after the build to get things
## into the ld.so.conf cache... use this only when developing and adding libs
ENV LD_LIBRARY_PATH /usr/local/lib

RUN pip install ipython
RUN pip install pytest

RUN pip install /usr/local/src_py

#RUN cd /usr/local/src_py &&\
#    python setup.py install
RUN ldconfig

