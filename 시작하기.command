#!/bin/bash
# 더블클릭하면 업로더 2개 + 바깥 접속 주소(터널)를 한 번에 켜줍니다.
# 새 맥/새 계정에서도 이 파일만 더블클릭하면 돼요.

cd "$(dirname "$0")" || exit 1
BASE="$(pwd)"

echo ""
echo "🐾 블로그 업로더를 켤게요"
echo "=================================="

# ---------- 1. 필요한 것 확인 ----------
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 이 없어요."
  echo "   터미널에 이걸 붙여넣어 설치해주세요:"
  echo "   xcode-select --install"
  echo ""
  read -r -p "엔터를 누르면 닫혀요..." _
  exit 1
fi

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "❌ cloudflared 가 없어요. (폰에서 접속하려면 필요해요)"
  echo "   터미널에 이걸 붙여넣어 설치해주세요:"
  echo "   brew install cloudflared"
  echo ""
  read -r -p "엔터를 누르면 닫혀요..." _
  exit 1
fi

# ---------- 2. 비밀번호 ----------
# auth.local 파일에 아이디/비번을 적어두면 매번 안 물어봐요. (git에 안 올라감)
#   BLOG_USER=내아이디
#   BLOG_PASS=내비밀번호
if [ -f "$BASE/auth.local" ]; then
  # shellcheck disable=SC1090
  set -a; . "$BASE/auth.local"; set +a
fi

if [ -z "$BLOG_USER" ] || [ -z "$BLOG_PASS" ]; then
  echo ""
  echo "🔐 업로더에 쓸 아이디/비밀번호를 정해주세요."
  echo "   (폰에서 접속할 때 물어보는 그거예요)"
  echo ""
  read -r -p "   아이디: " BLOG_USER
  read -r -s -p "   비밀번호: " BLOG_PASS
  echo ""
  printf 'BLOG_USER=%s\nBLOG_PASS=%s\n' "$BLOG_USER" "$BLOG_PASS" > "$BASE/auth.local"
  chmod 600 "$BASE/auth.local"
  echo "   ✅ auth.local 에 저장했어요. 다음부터는 안 물어봐요."
fi
export BLOG_USER BLOG_PASS

# ---------- 3. 파이썬 패키지 ----------
if ! python3 -c "import flask" >/dev/null 2>&1; then
  echo ""
  echo "📦 flask 설치 중..."
  python3 -m pip install --quiet --user -r "$BASE/requirements.txt" || {
    echo "❌ 설치 실패. 터미널에 이걸 붙여넣어 주세요:"
    echo "   python3 -m pip install --user flask"
    read -r -p "엔터를 누르면 닫혀요..." _
    exit 1
  }
fi

# ---------- 4. 기존 것 정리 ----------
echo ""
echo "🧹 이전에 켜둔 것 정리 중..."
pkill -f "uploader.py" 2>/dev/null
pkill -f "uploader_travel.py" 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 3

# ---------- 5. 업로더 켜기 ----------
mkdir -p "$BASE/inbox" "$BASE/posts"
: > "$BASE/uploader.log"
: > "$BASE/uploader_travel.log"
nohup python3 "$BASE/uploader.py"        > "$BASE/uploader.log" 2>&1 &
nohup python3 "$BASE/uploader_travel.py" > "$BASE/uploader_travel.log" 2>&1 &
sleep 2

# ---------- 6. 터널 켜기 ----------
: > "$BASE/tunnel.log"
: > "$BASE/tunnel_travel.log"
nohup cloudflared tunnel --url http://localhost:8765 > "$BASE/tunnel.log" 2>&1 &
nohup cloudflared tunnel --url http://localhost:8766 > "$BASE/tunnel_travel.log" 2>&1 &

echo "🌐 바깥 접속 주소를 받아오는 중... (20초쯤 걸려요)"

get_url() {
  for _ in $(seq 1 40); do
    u=$(grep -Eo "https://[a-zA-Z0-9.-]+trycloudflare\.com" "$1" 2>/dev/null | head -1)
    [ -n "$u" ] && { echo "$u"; return; }
    sleep 1
  done
}
FOOD=$(get_url "$BASE/tunnel.log")
TRIP=$(get_url "$BASE/tunnel_travel.log")

# ---------- 7. 결과 ----------
echo ""
echo "=================================="
if [ -n "$FOOD" ]; then
  echo "🍚 맛집 업로더"
  echo "   $FOOD"
else
  echo "⚠️  맛집 주소를 못 받았어요. 잠시 후 '현재주소_확인.command' 를 눌러보세요."
fi
echo ""
if [ -n "$TRIP" ]; then
  echo "✈️  여행 업로더"
  echo "   $TRIP"
else
  echo "⚠️  여행 주소를 못 받았어요. 잠시 후 다시 확인해주세요."
fi
echo "=================================="
echo ""

if [ -n "$FOOD" ]; then
  printf "%s" "$FOOD" | pbcopy
  echo "✅ 맛집 주소를 클립보드에 복사했어요. 폰으로 보내서 열면 돼요!"
fi

echo ""
echo "💡 주소는 켤 때마다 바뀌어요. 다시 확인하려면 이 파일을 또 눌러주세요."
echo "   끌 때는 '끄기.command' 를 누르면 돼요."
echo ""
read -r -p "엔터를 누르면 이 창이 닫혀요 (업로더는 계속 켜져 있어요)..." _
