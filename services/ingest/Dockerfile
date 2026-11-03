# Small official Linux + Python base
FROM python:3.14-slim

# No .pyc clutter; logs appear immediately (important for kubectl logs)
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install packages first: Docker caches this layer, so code changes rebuild in seconds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then the code (runtime files only, no tests)
COPY models.py espn.py worker.py ./

# Never run as root: if the app is hacked, the attacker isn't root
RUN useradd --create-home --uid 10001 app
USER app

# Exec form, so SIGTERM reaches Python directly and shutdown stays graceful
CMD ["python", "worker.py"]
