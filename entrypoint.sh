#!/usr/bin/env sh
set -eu

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"
WORKERS="${WORKERS:-1}"`r`nAPP_MODULE="${APP_MODULE:-app.main:app}"

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
    exec uvicorn "$APP_MODULE" \\
      --host "$HOST" \
      --port "$PORT" \
      --log-level "$LOG_LEVEL" \
      --workers "$WORKERS"
    ;;
  help|-h|--help)
    echo "Usage: /entrypoint.sh [generate|api|serve|help|<raw command>]"
    ;;
  *)
    exec "$cmd" "$@"
    ;;
esac


