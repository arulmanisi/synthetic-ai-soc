#!/usr/bin/env bash
set -euo pipefail

# Serve the alert viewer page locally.
# Usage: ./scripts/serve_alert_viewer.sh [PORT]
# Default port: 8000

PORT="${1:-8000}"

cd "$(dirname "$0")/../ui"
echo "Serving alert viewer on http://localhost:${PORT}/alert_viewer.html"
echo "Pass alertStoreUrl query param if needed, e.g.:"
echo "  http://localhost:${PORT}/alert_viewer.html?alertStoreUrl=http://localhost:8003/alerts"
python3 -m http.server "${PORT}"
