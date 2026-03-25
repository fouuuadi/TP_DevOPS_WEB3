# Dockerfile multi-stage optimise pour l'API quotes
# 3 stages : deps -> test -> production

# Stage 1 : Dependencies (cache les pip install)
FROM python:3.12-alpine AS deps
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 : Test (valide le code avant de builder la prod)
FROM deps AS test
COPY src/ ./src/
COPY test/ ./test/
RUN python -m pytest test/ -v

# Stage 3 : Production
FROM python:3.12-alpine AS production
WORKDIR /app

# User non-root pour la securite
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge 2>/dev/null || true

COPY src/ ./src/

LABEL maintainer="devops-team"
LABEL version="1.0"

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:5000/health >/dev/null || exit 1

# Gunicorn en prod, pas le serveur de dev Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "src", "app:app"]
