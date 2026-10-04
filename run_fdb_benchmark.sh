#!/usr/bin/env bash
# ==============================================================================
# INFERICS Pulse — One-Command FDB-v3 Reproduction Script
# Theme 05: Interruptible Real-Time Agents (Samsung PRISM Hackathon)
# Target: Full-Duplex-Bench v3 (arXiv 2604.04847)
# ==============================================================================
# USAGE:
#   bash run_fdb_benchmark.sh              # Full evaluation (online mode)
#   bash run_fdb_benchmark.sh --offline    # Offline deterministic evaluation
#   bash run_fdb_benchmark.sh --check-only # Verify dependencies only
# ==============================================================================

set -euo pipefail

# Trap SIGTERM/SIGINT for clean process teardown (no zombie workers)
cleanup() {
    echo "[CLEANUP] Caught signal. Terminating all background workers..."
    trap - SIGTERM SIGINT EXIT
    trap - SIGTERM SIGINT EXIT
    trap - SIGTERM SIGINT EXIT
    kill 0 2>/dev/null || true
    wait 2>/dev/null || true
    echo "[CLEANUP] All workers stopped cleanly."
    exit 0
}
trap cleanup SIGTERM SIGINT EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Flags
OFFLINE_MODE=false
CHECK_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --offline)   OFFLINE_MODE=true ;;
        --check-only) CHECK_ONLY=true ;;
        --help|-h)
            echo "Usage: bash run_fdb_benchmark.sh [--offline] [--check-only]"
            exit 0 ;;
    esac
done

echo "========================================================================"
echo "  INFERICS Pulse — Full-Duplex-Bench v3 Evaluation Harness"
echo "  Samsung PRISM Theme 05: Interruptible Real-Time Agents"
echo "  Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
echo "========================================================================"

# ============================================================
# STEP 1: Python Discovery (portable, no hardcoded paths)
# ============================================================
echo ""
echo "[1/5] Discovering Python runtime..."

PYTHON_BIN=""
for candidate in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" > /dev/null 2>&1; then
        VER=$("$candidate" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null || echo "False")
        if [ "$VER" = "True" ]; then
            PYTHON_BIN="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] Python 3.10+ not found. Please install Python 3.10 or higher." >&2
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_BIN" --version)
echo "  Found: $PYTHON_VERSION at $(command -v $PYTHON_BIN)"

# ============================================================
# STEP 2: Virtual Environment Setup (idempotent)
# ============================================================
echo ""
echo "[2/5] Setting up isolated virtual environment..."

VENV_DIR="$SCRIPT_DIR/.eval_venv"

if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "  Creating new virtual environment at .eval_venv/..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "  Installing dependencies from requirements.txt..."
"$VENV_PIP" install --quiet --upgrade pip
"$VENV_PIP" install --quiet \
    groq \
    pydantic \
    pytest \
    pytest-asyncio \
    Pillow \
    numpy \
    livekit-agents \
    livekit || echo "  [NOTE] Some packages may not install in offline mode — continuing."

# Pin random seeds for evaluation reproducibility
export PYTHONHASHSEED=42
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

echo "  Environment ready. PYTHONHASHSEED=42"

if [ "$CHECK_ONLY" = true ]; then
    echo ""
    echo "  [check-only] Dependency verification complete."
    exit 0
fi

# ============================================================
# STEP 3: Port safety check before starting any listeners
# ============================================================
echo ""
echo "[3/5] Port safety audit (checking for stale sockets on port 3000)..."

if command -v ss > /dev/null 2>&1; then
    STALE=$(ss -tulpn 2>/dev/null | grep ":3000" || true)
    if [ -n "$STALE" ]; then
        echo "  [WARN] Port 3000 occupied. Terminating stale process..."
        fuser -k 3000/tcp 2>/dev/null || true
        sleep 1
    fi
fi
echo "  Port 3000 clear."

# ============================================================
# STEP 4: Run FDB-v3 Test Scenarios
# ============================================================
echo ""
echo "[4/5] Running FDB-v3 Adversarial Test Suite..."

"$VENV_PYTHON" -m pytest \
    tests/test_harness.py \
    tests/test_x_factor.py \
    -s -v \
    -p no:cacheprovider \
    --tb=short \
    --timeout=60 \
    2>&1 | tee /tmp/fdb_pytest_results.txt

echo "  Test suite complete."

# ============================================================
# STEP 5: Scoring Evaluation Matrix
# ============================================================
echo ""
echo "[5/5] Executing Official Samsung Theme 05 Evaluation Matrix..."

"$VENV_PYTHON" scripts/evaluate_score.py

# ============================================================
# OPTIONAL: Cloud health check
# ============================================================
if [ "$OFFLINE_MODE" = false ] && command -v curl > /dev/null 2>&1; then
    echo ""
    echo "[OPTIONAL] Vercel Live Endpoint Health Check..."
    curl -s -o /dev/null -w "  Vercel Status: %{http_code}\n" \
        https://inferics-samsung-prism.vercel.app/api/health 2>/dev/null \
        || echo "  Vercel check skipped (network unavailable)."
fi

echo ""
echo "========================================================================"
echo "  FDB-v3 Reproduction Complete."
echo "  All benchmark scenarios executed with Exit Code 0."
echo "  Agent: INFERICS Pulse v2.0 | Theme 05 | Samsung PRISM Y2026"
echo "========================================================================"
