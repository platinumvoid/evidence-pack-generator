FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\`r`n    PYTHONUNBUFFERED=1 \\`r`n    PIP_NO_CACHE_DIR=1 \\`r`n    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY app /app/app
COPY --chmod=755 entrypoint.sh /entrypoint.sh

RUN pip install --no-cache-dir .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]



