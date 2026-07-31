FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing pyc files to disc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# Install dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application files
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
