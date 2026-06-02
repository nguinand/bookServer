#!/usr/bin/env sh
set -eu

attempt=1
max_attempts=30
delay_seconds=5

while [ "$attempt" -le "$max_attempts" ]; do
    echo "Running database migrations (attempt ${attempt}/${max_attempts})..."

    if alembic upgrade heads; then
        echo "Database migrations completed."
        break
    fi

    if [ "$attempt" -eq "$max_attempts" ]; then
        echo "Database migrations failed after ${max_attempts} attempts." >&2
        exit 1
    fi

    echo "Database migrations failed. Retrying in ${delay_seconds} seconds..." >&2
    attempt=$((attempt + 1))
    sleep "$delay_seconds"
done

exec "$@"
