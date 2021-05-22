FROM python:3
ENV PYTHONUUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY run.sh .
RUN chmod 755 run.sh
ENTRYPOINT ["/code/run.sh"]