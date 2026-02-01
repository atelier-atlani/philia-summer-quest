#!/usr/bin/env bash
# scripts/check_before_merge.sh
# Pre-merge validation: tests + Streamlit health check
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# --- 1. Activate venv if present ---
if [[ -d ".venv" ]]; then
    echo "🐍 Activating .venv..."
    source .venv/bin/activate
fi

# --- 2. Run contract FAQ tests ---
echo ""
echo "🧪 Running tests_contract_faq.py..."
python scripts/tests_contract_faq.py

# --- 3. Run smoke tests ---
echo ""
echo "🧪 Running test_smoke.py..."
python scripts/test_smoke.py

# --- 4. Streamlit health check ---
echo ""
echo "🌐 Starting Streamlit for health check..."
STREAMLIT_PORT=8501
streamlit run app.py --server.headless true --server.port $STREAMLIT_PORT &
STREAMLIT_PID=$!

# Cleanup on exit
cleanup() {
    if kill -0 "$STREAMLIT_PID" 2>/dev/null; then
        echo "🛑 Stopping Streamlit (PID $STREAMLIT_PID)..."
        kill "$STREAMLIT_PID" 2>/dev/null || true
        wait "$STREAMLIT_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "⏳ Waiting 5s for Streamlit to start..."
sleep 5

echo "🔍 Checking Streamlit response..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$STREAMLIT_PORT" || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "✅ Streamlit responds with HTTP 200"
else
    echo "❌ Streamlit health check failed (HTTP $HTTP_CODE)"
    exit 1
fi

# --- Done ---
echo ""
echo "✅ ALL CHECKS PASSED"
exit 0
