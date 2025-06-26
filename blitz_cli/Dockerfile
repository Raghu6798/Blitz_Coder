# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better cache
COPY blitz_cli/requirements.txt blitz_cli/pyproject.toml /app/

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the code
COPY blitz_cli /app

# Install the package (editable mode for dev, or just pip install . for prod)
RUN pip install .   

# Set the default entrypoint for the CLI
ENTRYPOINT ["blitzcode"]

# Show help by default (optional)
CMD ["--help"]