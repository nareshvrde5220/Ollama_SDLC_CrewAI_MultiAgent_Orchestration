<!-- Phase UUID: c14a3edc-76cb-4f86-ba3a-d54d5001cb67 -->

**Dockerfile**

```dockerfile
# syntax=docker/dockerfile:1.4
# ---- Build stage ----
FROM python:3.11-slim AS builder
WORKDIR /app
COPY todo_cli.py .
# No external dependencies, but keep pip updated for future use
RUN python -m pip install --no-cache-dir --upgrade pip

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /app /app

# Create a non‑root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

USER appuser

# Health check – simply verifies that the interpreter can start
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

ENTRYPOINT ["python", "todo_cli.py"]
```

---

**docker-compose.yml**

```yaml
version: "3.9"

services:
  todo-cli:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: todo_cli
    volumes:
      # Persist tasks.json on the host so data survives container restarts
      - ./data:/app/data
    environment:
      # Example environment variable – can be overridden in .env
      - LOG_LEVEL=INFO
    # Optional: expose a port if you want to run a health‑check endpoint
    # ports:
    #   - "8080:8080"
    restart: unless-stopped
```

---

**requirements.txt**

```
# No external dependencies required for the current CLI.
# This file is kept for future use and to enable pip‑based caching.
```

---

**.env.example**

```
# Example environment variables for the Todo CLI container.
# Copy this file to .env and adjust as needed.

# Logging level – can be DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

---

**.github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write  # Needed for pushing to ghcr.io

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install flake8 for linting
        run: |
          python -m pip install --upgrade pip
          pip install flake8

      - name: Run flake8 lint
        run: flake8 todo_cli.py

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/todo-cli:latest
            ghcr.io/${{ github.repository_owner }}/todo-cli:${{ github.sha }}

      - name: Run container health check
        run: |
          docker run --rm ghcr.io/${{ github.repository_owner }}/todo-cli:latest \
            python -c "import sys; sys.exit(0)"
```

---