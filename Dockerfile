from python:3.5

RUN apt-get update && apt-get install -y \
        cmake \
        # for dripline-cpp
        build-essential \
        gdb \
        libboost-all-dev \
        librabbitmq-dev \
        wget &&\
    rm -rf /var/lib/apt/lists/*

COPY dripline-cpp /usr/local/src/dripline-cpp
COPY module_bindings /usr/local/src/module_bindings
COPY dripline /usr/local/src/dripline
COPY bin /usr/local/src/bin
COPY .git /usr/local/src/.git
COPY setup.py /usr/local/src/setup.py
COPY CMakeLists.txt /usr/local/src/CMakeLists.txt

## would prefer not to do this, just run ldconfig after the build to get things
## into the ld.so.conf cache... use this only when developing and adding libs
ENV LD_LIBRARY_PATH /usr/local/lib

RUN pip install ipython

RUN cd /usr/local/src &&\
    python setup.py install
RUN ldconfig

