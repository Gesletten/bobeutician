# Using Python 3.10 slim image build as the base
FROM python:3.10-slim

# Set up the working directory inside container
WORKDIR /code

# Install OS-level build dependencies needed for some Python packages
# (mysqlclient, numpy, scikit-learn, faiss, etc.)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   default-libmysqlclient-dev \
	   libpq-dev \
	   pkg-config \
	   libopenblas-dev \
	   liblapack-dev \
	   ca-certificates \
	   bash \
	   curl \
	   git \
	   wget \
	   docker.io \
	   procps \
	   lsb-release \
	   gnupg \

	&& rm -rf /var/lib/apt/lists/*

# Prefer bash for interactive shells inside the devcontainer
ENV SHELL=/bin/bash

# Copy requirements file for Docker layer caching
COPY backend/requirements.txt .

# Installing Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Ensure entrypoint script is executable
RUN chmod +x entrypoint.sh

# Create directories for VS Code Server
RUN mkdir -p /root/.vscode-server /root/.vscode-server-insiders

# Set environment variables to help with ARM64 support
ENV VSCODE_SERVER_ACCEPT_INSECURE_DOWNLOADS=1

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose backend port
EXPOSE 8000

# Start the FastAPI server when the container runs so the API is reachable
# Use 0.0.0.0 so it's accessible from the host and other containers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]