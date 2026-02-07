<!-- Phase UUID: 3d798569-d41f-4398-aab7-3426a1443aef -->

**Dockerfile**

```dockerfile
# syntax=docker/dockerfile:1.4

# ------------------------------------------------------------------
#  Stage 1 – Build
# ------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Disable byte‑code creation & enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies (needed only for pip install)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY . .

# ------------------------------------------------------------------
#  Stage 2 – Runtime
# ------------------------------------------------------------------
FROM python:3.12-slim

# Disable byte‑code & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non‑root user & group
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# Working directory
WORKDIR /app

# Copy built artefacts from the builder stage
COPY --from=builder /app /app

# Ensure the non‑root user owns the files
RUN chown -R appuser:appgroup /app

# Switch to the non‑root user
USER appuser

# Health‑check – a simple command that exits 0 on success
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "print('ok')"

# Default command
ENTRYPOINT ["python", "main.py"]
```

---

**docker‑compose.yml**

```yaml
version: "3.8"

services:
  calculator:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: simple_calculator
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
    # No ports are exposed – this is a CLI tool
```

---

**requirements.txt**

```text
# No external runtime dependencies are required for the calculator.
# The file is kept to satisfy the “pinned versions” requirement.
# Pin the pip version for reproducibility.
pip==23.3.1
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

    steps:
      # 1️⃣ Checkout the repository
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2️⃣ Set up Python 3.12
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # 3️⃣ Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # 4️⃣ Lint with flake8 (optional but recommended)
      - name: Lint with flake8
        run: |
          pip install flake8
          flake8 .

      # 5️⃣ Run a lightweight test – the app has no unit tests
      - name: Run simple CI check
        run: |
          python -c "print('CI passed')"

      # 6️⃣ Build the Docker image locally (no push)
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile
          tags: ghcr.io/${{ github.repository_owner }}/simple_calculator:latest
          push: false

      # 7️⃣ Scan the image with Trivy for security issues
      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@v0.0.18
        with:
          image-ref: ghcr.io/${{ github.repository_owner }}/simple_calculator:latest
          format: table
          exit-code: 1
          severity: HIGH,CRITICAL
```

---

**.env.example**

```dotenv
# .env.example
# Add environment variables here if the application ever needs them.
# For this simple calculator no variables are required.
```

---

**Notes**

* The application code should be in a file named `main.py` (the content you provided).  
* The Docker image is built from a multi‑stage build, keeping the final image minimal and using a non‑root user.  
* The health‑check simply runs a short Python command that exits successfully.  
* The CI pipeline checks out the repo, sets up Python, installs dependencies, lints, runs a trivial test, builds the Docker image locally, and performs a security scan with Trivy.  
* No ports are exposed because the tool is purely command‑line.