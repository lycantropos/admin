FROM python:3

# Workaround for `click` and python3
# http://click.pocoo.org/5/python3/#python-3-surrogate-handling
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

WORKDIR /opt/collector

COPY ./requirements.txt ./
RUN python3 -m pip install -r requirements.txt

COPY . /opt/collector/
RUN python3 -m pip install .

ENTRYPOINT ["python3", "manage.py"]
