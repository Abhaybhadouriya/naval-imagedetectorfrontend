FROM python:3.10-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libgl1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -------- Runtime Stage --------
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/naval/.local

# Copy application code and model
COPY app.py .
COPY unet_model.h5 .

# Create non-root user and setup directories
RUN useradd -m naval && \
    mkdir -p /app/Uploads /app/output && \
    chown -R naval:naval /app /app/Uploads /app/output

USER naval

# Set PATH for pip-installed binaries
ENV PATH="/home/naval/.local/bin:$PATH"

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:5000", "app:app"]