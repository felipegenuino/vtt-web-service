#!/usr/bin/env bash
# run.sh — script para rodar a aplicação em WSL / Linux / macOS
# Uso: ./run.sh [porta]

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-5000}"
VENV_DIR="$ROOT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Criando virtualenv..."
  python -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$ROOT_DIR/requirements.txt"
fi

echo "Ativando virtualenv..."
source "$VENV_DIR/bin/activate"

: "${OLLAMA_HOST:=http://127.0.0.1:11434}"
export OLLAMA_HOST
export FLASK_APP=app.py

echo "Iniciando Flask (porta $PORT)..."
python -m flask run --host=0.0.0.0 --port="$PORT"
