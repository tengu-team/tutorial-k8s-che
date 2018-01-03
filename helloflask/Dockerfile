FROM python:3.5-slim

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "server.py"]
