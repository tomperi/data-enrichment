FROM python:3.8
EXPOSE 5050/tcp

RUN apt-get update -y && apt-get install -y libgeos-dev
COPY app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY app/ /app

CMD ["python", "main.py"]
