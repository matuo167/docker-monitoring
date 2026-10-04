#!/usr/bin/env sh

set -eu

BASE_URL="${BASE_URL:-http://localhost:8080}"
REQUESTS="${REQUESTS:-5}"

echo "Generating traffic against ${BASE_URL} (${REQUESTS} requests per endpoint)"

i=1
while [ "$i" -le "$REQUESTS" ]; do
  curl --silent --show-error --output /dev/null "${BASE_URL}/"
  curl --silent --show-error --output /dev/null "${BASE_URL}/slow"
  # /error is intentional, so do not stop the script on HTTP 500.
  curl --fail --silent --show-error --output /dev/null "${BASE_URL}/error" || true
  i=$((i + 1))
done

echo "Done. Open Grafana and set the dashboard time range to include the latest traffic."
