FROM python:3.7.1

ADD /cobowl /cobowl/cobowl/
ADD /resource /cobowl/resource/
ADD setup.py /cobowl/

WORKDIR /cobowl

RUN python -m pip install --upgrade pip
RUN python -m pip install .
