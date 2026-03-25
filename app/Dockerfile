# Dockerfile multi-stage pour l'API quotes
# Stage 1 lance les tests, stage 2 build l'image de prod

# Stage 1 : Test
FROM python:3.12-alpine AS test
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY test/ ./test/
RUN python -m pytest test/ -v

# Stage 2 : Production
FROM python:3.12-alpine AS production
WORKDIR /app

# User non-root pour la securite
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://127.0.0.1:5000/health >/dev/null || exit 1

# Gunicorn en prod, pas le serveur de dev Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "src", "app:app"]
