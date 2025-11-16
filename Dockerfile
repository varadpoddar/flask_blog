# ---------- Base image with dependencies ----------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies (for example, to build wheels / SQLite headers if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# ---------- Test stage (runs tests in a container) ----------
FROM base AS test
# tests run during docker build; if they fail, build fails
RUN pytest -q

# ---------- Runtime image ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

WORKDIR /app

# Copy everything from the base image (code + deps already installed)
COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app /app

# Remove tests and other development-only artifacts from the runtime image
RUN rm -rf /app/tests /app/.pytest_cache || true

# Copy entrypoint script and make it executable
COPY --from=base /app/scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

EXPOSE 5000

# Use the flask CLI to start the app so the process stays in the foreground.
# Ensure FLASK_APP is set in the image (set above) so `flask run` picks up the app.
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
