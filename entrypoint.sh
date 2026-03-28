#!/usr/bin/env sh
set -eu

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"
WORKERS="${WORKERS:-1}"
APP_MODULE="${APP_MODULE:-app.main:app}"`r`nUVICORN_EXTRA_ARGS="${UVICORN_EXTRA_ARGS:-}"

if ! printf "%s" "$PORT" | grep -Eq "^[0-9]+$"; then
  echo "PORT must be numeric" >&2
  exit 2
fi

if ! printf "%s" "$WORKERS" | grep -Eq "^[1-9][0-9]*$"; then
  echo "WORKERS must be a positive integer" >&2
  exit 2
fi

if [ "$#" -eq 0 ]; then
  set -- api
fi

cmd="$1"
shift

case "$cmd" in
  generate)
    exec python -m app.cli generate "$@"
    ;;
  api|serve)
    exec uvicorn "$APP_MODULE" \
      --host "$HOST" \
      --port "$PORT" \
      --log-level "$LOG_LEVEL" \
      --workers "$WORKERS" `r`n      $UVICORN_EXTRA_ARGS
    ;;
  help|-h|--help)
    echo "Usage: /entrypoint.sh [generate|api|serve|help|<raw command>]"
    ;;
  *)
    exec "$cmd" "$@"
    ;;
esac

