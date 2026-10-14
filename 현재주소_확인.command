#!/bin/bash
# 더블클릭하면 지금 바깥에서 접속할 주소를 보여주고 클립보드에 복사해요
BASE="$(cd "$(dirname "$0")" && pwd)"

find_url() {
  grep -Eo "https://[a-zA-Z0-9.-]+trycloudflare\.com" "$1" 2>/dev/null | tail -1
}

FOOD=$(find_url "$BASE/tunnel.log")
TRIP=$(find_url "$BASE/tunnel_travel.log")

echo ""
echo "=================================="
if [ -n "$FOOD" ]; then
  echo "🍚 맛집 업로더"
  echo "   $FOOD"
else
  echo "🍚 맛집 — 아직 주소가 안 잡혔어요"
fi
echo ""
if [ -n "$TRIP" ]; then
  echo "✈️  여행 업로더"
  echo "   $TRIP"
else
  echo "✈️  여행 — 아직 주소가 안 잡혔어요"
fi
echo "=================================="
echo ""

if [ -n "$FOOD" ]; then
  printf "%s" "$FOOD" | pbcopy
  echo "✅ 맛집 주소를 클립보드에 복사했어요! (폰으로 보내서 열면 돼요)"
elif [ -n "$TRIP" ]; then
  printf "%s" "$TRIP" | pbcopy
  echo "✅ 여행 주소를 클립보드에 복사했어요!"
else
  echo "⚠️ 주소가 하나도 없어요."
  echo "   '시작하기.command' 를 먼저 눌러주세요."
fi

echo ""
echo "이 창은 닫아도 돼요."
