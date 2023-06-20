FROM python:3.10.4-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install gunicorn==20.1.0
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]