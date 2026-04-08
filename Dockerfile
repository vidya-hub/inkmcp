# InkMCP Server - Dockerized MCP Server for Inkscape/Embroidery
# Supports HTTP (Streamable HTTP) and SSE transport modes

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY inkmcp/ ./inkmcp/
COPY examples/ ./examples/

# Set Python path to include inkmcp directory
ENV PYTHONPATH=/app/inkmcp:$PYTHONPATH

# Default environment variables
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV MCP_LOG_LEVEL=INFO

# Expose the default port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${MCP_PORT}/mcp || exit 1

# Run the MCP server
WORKDIR /app/inkmcp
CMD ["sh", "-c", "python3 inkscape_mcp_server.py --transport ${MCP_TRANSPORT} --host ${MCP_HOST} --port ${MCP_PORT} --log-level ${MCP_LOG_LEVEL}"]
