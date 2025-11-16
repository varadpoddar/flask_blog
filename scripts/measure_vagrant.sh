
#!/usr/bin/env bash
set -euo pipefail

# Backward-compatible wrapper: convert vagrant_setup_time.json to measurements CSV
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
"$SCRIPT_DIR/convert_vagrant_json_to_csv.sh" "$@"
