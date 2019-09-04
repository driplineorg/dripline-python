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

# I'd really like to figure out how to get the dripline libraries installed to /usr/local/lib, outside of python...
RUN echo "# cmake installed libraries" > /etc/ld.so.conf.d/dripline.conf &&\
    echo "/usr/local/lib/python3.5/site-packages" >> /etc/ld.so.conf.d/dripline.conf &&\
    ldconfig

RUN pip3 install --upgrade pip
RUN pip3 install -v /usr/local/src
RUN ldconfig
