FROM python:3
# prevents python from buffering.
ENV PYTHONUUNBUFFERED 1
# prevents python from creating '.pyc' files.
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
