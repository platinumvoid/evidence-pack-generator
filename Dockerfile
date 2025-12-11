FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\`r`n    PYTHONUNBUFFERED=1 \\`r`n    PIP_NO_CACHE_DIR=1 \\`r`n    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

LABEL org.opencontainers.image.title="evidence-pack-generator" \`r`n      org.opencontainers.image.description="Containerized evidence pack generator" \`r`n      org.opencontainers.image.source="https://github.com/platinumvoid/evidence-pack-generator"`r`n`r`nCOPY pyproject.toml README.md /app/
COPY app /app/app
COPY --chmod=755 entrypoint.sh /entrypoint.sh

RUN adduser --disabled-password --gecos "" --home /nonexistent --shell /usr/sbin/nologin appuser && pip install --no-cache-dir . && chown -R appuser:appuser /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8000/health\", timeout=2)" || exit 1`r`n`r`nENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]






USER appuser

