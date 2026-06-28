FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

LABEL org.opencontainers.image.title="evidence-pack-generator" \
      org.opencontainers.image.description="Containerized evidence pack generator" \
  org.opencontainers.image.source="https://github.com/platinumvoid/evidence-pack-generator" \
      org.opencontainers.image.licenses="MIT"

COPY pyproject.toml README.md /app/
COPY app /app/app
COPY --chmod=755 entrypoint.sh /entrypoint.sh

RUN adduser --disabled-password --gecos "" --home /nonexistent --shell /usr/sbin/nologin appuser \
    && pip install --no-cache-dir . \
    && chown -R appuser:appuser /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

STOPSIGNAL SIGTERM

ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]

USER appuser
