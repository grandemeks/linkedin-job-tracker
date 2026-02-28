# Base image - koristimo slim varijantu za manji image
FROM python:3.13-slim

# Metadata
LABEL maintainer="tvoje-ime"
LABEL description="Job Tracker - DevOps Portfolio Project"

# Security best practice - ne koristimo root usera
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Kopiramo requirements prvi (Docker layer caching!)
COPY requirements.txt .

# Instaliramo dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo source code
COPY src/ ./src/

# Mijenjamo ownership na appuser
RUN chown -R appuser:appuser /app

# Switchujemo na non-root usera
USER appuser

# Environment varijable sa default vrijednostima
ENV CHECK_INTERVAL_MINUTES=30
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Pokrecemo aplikaciju
CMD ["python3", "src/main.py"]