FROM python:3.13-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY . /app

# Install dependencies using uv
RUN uv pip install --system --no-cache \
    "kubernetes>=32.0.1" \
    "mcp[cli]>=1.28.0,<2" \
    "ruff>=0.11.5" \
    "pyyaml"

CMD ["python", "k8s_pilot.py"]
