#!/usr/bin/env bash
# run_scraper.sh – convenience launcher
# Usage:
#   ./run_scraper.sh save   # scrape -> JSON/CSV only (default)
#   ./run_scraper.sh load   # scrape -> DB + JSON/CSV
# The script auto-activates .venv if it exists.

# 1. Always operate from project root (folder containing this script)
cd "$(dirname "$0")" || exit 1

# 2. Activate virtual environment if present
if [[ -d ".venv" ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

# 3. Decide which Python module to run
ACTION=${1:-save}
case "$ACTION" in
  load)
    PY_SCRIPT="scraping/scrape_and_load.py"
    ;;
  save)
    PY_SCRIPT="scraping/scrape_and_save.py"
    ;;
  *)
    echo "Unknown option: $ACTION (use 'save' or 'load')"
    exit 1
    ;;
esac

# 4. Execute
exec python3 "$PY_SCRIPT"
