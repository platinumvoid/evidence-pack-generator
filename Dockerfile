FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\`r`n    PYTHONUNBUFFERED=1 \\`r`n    PIP_NO_CACHE_DIR=1 \\`r`n    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

LABEL org.opencontainers.image.title="evidence-pack-generator" \`r`n      org.opencontainers.image.description="Containerized evidence pack generator" \`r`n      org.opencontainers.image.source="https://github.com/platinumvoid/evidence-pack-generator"`r`n`r`nCOPY pyproject.toml README.md /app/
COPY app /app/app
COPY --chmod=755 entrypoint.sh /entrypoint.sh

RUN adduser --disabled-password --gecos "" --home /nonexistent --shell /usr/sbin/nologin appuser && pip install --no-cache-dir . && chown -R appuser:appuser /app

ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]






USER appuser
