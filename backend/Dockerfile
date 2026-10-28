
FROM python:3.11-slim

WORKDIR /app

COPY backend/ ./backend/
COPY *.html ./
COPY style.css ./

RUN pip install --no-cache-dir flask

EXPOSE 5000

CMD ["python", "backend/app.py"]
