FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install necessary system dependencies
RUN apk add --no-cache \
    bash \
    curl \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    unzip \
    git

RUN pip install --upgrade pip setuptools wheel

# Install Poetry package manager
RUN pip install poetry

# Copy dependency files
COPY PYTHON/pyproject.toml PYTHON/poetry.lock ./

# Configure Poetry to avoid creating virtual environments and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy application source code
COPY PYTHON/api/ /app/api/
COPY PYTHON/application/ /app/application/
COPY PYTHON/domain/ /app/domain/
COPY PYTHON/infrastructure/ /app/infrastructure/
COPY PYTHON/config/ /app/config/
COPY PYTHON/data/ /app/data/
COPY tableOrders.json /app/tableOrders.json

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && chown -R appuser:appgroup /app
RUN mkdir -p /var/lib/etq && chown -R appuser:appgroup /var/lib/etq
USER appuser

# Expose port 8080 for the application
EXPOSE 8080

# Start the app with Gunicorn using Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "--timeout", "300", "api.main:app"]