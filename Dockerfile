FROM python:3.11.3

WORKDIR /app

COPY . /app

EXPOSE 8080

ENV NAME Bot

CMD ["python", "main.py"]

