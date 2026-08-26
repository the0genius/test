FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY generate.py app.py index.html ./

# Platforms inject PORT; bind to all interfaces so their router can reach us.
ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
