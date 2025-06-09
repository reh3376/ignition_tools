# IGN Scripts Testing Environment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
COPY requirements-test.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/test-results /app/coverage-reports

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=DEBUG
ENV TESTING_MODE=true

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash ignuser
RUN chown -R ignuser:ignuser /app
USER ignuser

# Expose port for Streamlit UI testing
EXPOSE 8501

# Default command runs the test suite
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--log-cli-level=INFO"] 