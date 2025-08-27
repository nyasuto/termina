#!/bin/bash
# Termina起動スクリプト - ダブルクリックで実行可能

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

echo "🎤 Termina起動中..."
echo "終了するには Ctrl+C を押してください"
echo ""

# uvでTerminaを実行
uv run python termina.py