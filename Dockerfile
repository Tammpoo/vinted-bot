FROM python:3.11-slim

WORKDIR /app

# Create appuser
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force cache bust to pick up latest code
ARG CACHEBUST=1

# Copy the rest of the application
COPY . .

# Switch to non-root user
USER appuser

# Railway will set PORT environment variable
ENV PORT=8000
EXPOSE 8000
EXPOSE 8080

CMD ["python", "vinted_notifications.py"]
