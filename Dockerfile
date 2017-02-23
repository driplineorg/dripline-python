FROM python:2.7

ADD . /dripline-python
RUN pip install -r /dripline-python/requirements.txt
RUN cd /dripline-python && python setup.py install
