FROM python:3.10-slim

RUN apt-get update && apt-get install

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

WORKDIR /app/src

# Do not use more than 1 worker per container
# gunicorn --workers 1 --threads 4 --bind 0.0.0.0:8000 backend_main.wsgi:application
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:8000", "backend_main.wsgi:application"]
