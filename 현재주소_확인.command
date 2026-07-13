#!/bin/bash
# 더블클릭하면 현재 바깥 접속 주소를 보여주고 클립보드에 복사해요
LOG="$(cd "$(dirname "$0")" && pwd)/tunnel.log"
URL=$(grep -Eo "https://[a-zA-Z0-9.-]+trycloudflare.com" "$LOG" | tail -1)
echo ""
if [ -n "$URL" ]; then
  echo "📱 지금 바깥에서 접속할 주소:"
  echo ""
  echo "   $URL"
  echo ""
  printf "%s" "$URL" | pbcopy
  echo "✅ 클립보드에 복사됐어요! (폰으로 전송해서 열면 돼요)"
else
  echo "⚠️ 아직 주소가 안 잡혔어요. 잠시 후 다시 눌러보세요."
  echo "   (터널 서비스가 켜지는 중일 수 있어요)"
fi
echo ""
echo "이 창은 닫아도 돼요."
