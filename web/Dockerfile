FROM python:3.6

MAINTAINER Linus Törngren <linus@etnolit.se>

RUN mkdir -p /usr/src
WORKDIR /usr/src

RUN pip install --no-cache-dir -U pip

RUN pip install --no-cache-dir gunicorn

COPY requirements.txt /usr/src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src
RUN chmod +x manage.py

CMD ["./manage.py", "run"]
