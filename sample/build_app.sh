#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${ROOT}/venv/bin/activate"
SAMPLE="${ROOT}/sample"

if [[ ! -f "$VENV" ]]; then
  echo "venv not found: ${ROOT}/venv"
  echo "Create it and run: pip install -r requirements.txt"
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV"

pip install -q pyinstaller

cd "$SAMPLE"
pyinstaller --noconfirm --clean pyqt_stock_scanner.spec

echo ""
echo "Build complete."
echo "  macOS app: ${SAMPLE}/dist/StockScanner.app"
echo "  Run:       open \"${SAMPLE}/dist/StockScanner.app\""
echo ""
echo "Telegram 사용 시 프로젝트 .env 를 dist/.env 로 복사하세요:"
echo "  cp \"${ROOT}/.env\" \"${SAMPLE}/dist/.env\""
