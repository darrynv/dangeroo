# syntax=docker/dockerfile:1

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for tree-sitter
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# No need to clone tree-sitter grammars; using pre-built language wheels

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY chroma_mcp_server.py .
# Copy any tree-sitter language sources if needed (assume in same dir for now)
# If you add more language grammars, copy them here

# Expose no ports (uses STDIO)
ENTRYPOINT ["python", "chroma_mcp_server.py"]