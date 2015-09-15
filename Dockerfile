FROM python:3.4-onbuild

RUN python setup.py develop

ENTRYPOINT ["mx"]
