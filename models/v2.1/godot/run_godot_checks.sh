#!/usr/bin/env bash
set -euo pipefail
GODOT_BIN="${1:-godot}"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$PROJECT_DIR/qa_engine_logs"
"$GODOT_BIN" --headless --editor --path "$PROJECT_DIR" --import >"$PROJECT_DIR/qa_engine_logs/godot_import.log" 2>&1
"$GODOT_BIN" --headless --path "$PROJECT_DIR" --script 'res://validate_import.gd' >"$PROJECT_DIR/qa_engine_logs/godot_validate.log" 2>&1
if ! grep -q 'GODOT ENGINE IMPORT CHECK PASS' "$PROJECT_DIR/qa_engine_logs/godot_validate.log"; then
    cat "$PROJECT_DIR/qa_engine_logs/godot_validate.log"; exit 2
fi
printf '%s\n' 'Godot import and structural audit passed. Visual quality not yet verified.'
