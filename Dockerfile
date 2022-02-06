FROM python:3.9
ENV PYTHONUNBUFFERED 1
ENV REDIS_HOST "redis"

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    netcat \
    iputils-ping

COPY requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/

RUN chmod 755 /
RUN chmod 755 run.sh
ENTRYPOINT ["/code/run.sh"]
