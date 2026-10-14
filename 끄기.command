#!/bin/bash
# 더블클릭하면 업로더랑 터널을 전부 꺼요.
cd "$(dirname "$0")" || exit 1

echo ""
echo "🛑 업로더를 끌게요..."
pkill -f "uploader.py" 2>/dev/null
pkill -f "uploader_travel.py" 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 2
echo "✅ 다 껐어요."
echo ""
echo "이 창은 닫아도 돼요."
sleep 2
