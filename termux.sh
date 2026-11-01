#!/data/data/com.termux/files/usr/bin/bash
# 갤럭시 탭(안드로이드) Termux 에서 맥 대신 업로더를 돌리는 스크립트.
#
# 처음 한 번 (Termux 앱에 붙여넣기):
#   curl -fsSL https://raw.githubusercontent.com/emily1818/naver-blog-auto/main/termux.sh | bash -s install
#
# 그 다음부터:
#   ~/naver-blog-auto/termux.sh start   # 업로더 + 접속 주소 켜기
#   ~/naver-blog-auto/termux.sh url     # 지금 주소 다시 보기
#   ~/naver-blog-auto/termux.sh stop    # 끄기

REPO="https://github.com/emily1818/naver-blog-auto.git"
DEST="$HOME/naver-blog-auto"
BRANCH="${BLOG_BRANCH:-main}"

say() { printf '%s\n' "$*"; }

find_url() {
  grep -Eo "https://[a-zA-Z0-9-]+\.trycloudflare\.com" "$1" 2>/dev/null | grep -v '^https://api\.' | tail -1
}

copy_clip() {
  command -v termux-clipboard-set >/dev/null 2>&1 && printf "%s" "$1" | termux-clipboard-set 2>/dev/null
}

do_install() {
  say ""
  say "🐾 갤럭시 탭에 블로그 업로더를 설치할게요"
  say "=================================="
  pkg update -y || { say "❌ pkg update 실패. 인터넷 연결 확인 후 다시 해주세요."; exit 1; }
  pkg install -y git python cloudflared termux-api || { say "❌ 프로그램 설치 실패"; exit 1; }
  python -m pip install --quiet flask || { say "❌ flask 설치 실패"; exit 1; }

  if [ -d "$DEST/.git" ]; then
    say "📥 코드를 최신으로 받아올게요."
    git -C "$DEST" pull --ff-only || say "⚠️  최신으로 못 받았어요. 지금 코드로 계속할게요."
  else
    say "📥 코드를 받아올게요 → $DEST"
    git clone -b "$BRANCH" "$REPO" "$DEST" || git clone "$REPO" "$DEST" || { say "❌ 코드 받기 실패"; exit 1; }
  fi
  chmod +x "$DEST/termux.sh"

  say ""
  say "🎉 설치 끝! 이제 켤게요."
  say "   다음부터는:  ~/naver-blog-auto/termux.sh start"
  exec bash "$DEST/termux.sh" start
}

do_stop() {
  pkill -f "uploader.py" 2>/dev/null
  pkill -f "uploader_travel.py" 2>/dev/null
  pkill -f "cloudflared tunnel" 2>/dev/null
  command -v termux-wake-unlock >/dev/null 2>&1 && termux-wake-unlock
}

do_url() {
  cd "$DEST" || exit 1
  FOOD=$(find_url tunnel.log)
  TRIP=$(find_url tunnel_travel.log)
  say ""
  say "=================================="
  [ -n "$FOOD" ] && { say "🍚 맛집 업로더"; say "   $FOOD"; } || say "🍚 맛집 — 아직 주소가 안 잡혔어요"
  say ""
  [ -n "$TRIP" ] && { say "✈️  여행 업로더"; say "   $TRIP"; } || say "✈️  여행 — 아직 주소가 안 잡혔어요"
  say "=================================="
  if [ -n "$FOOD" ]; then
    copy_clip "$FOOD" && say "✅ 맛집 주소를 클립보드에 복사했어요. 핸드폰으로 보내서 열면 돼요!"
  fi
}

do_start() {
  cd "$DEST" || { say "❌ $DEST 가 없어요. install 부터 해주세요."; exit 1; }

  # 아이디/비번 (auth.local, git 제외)
  [ -f auth.local ] && { set -a; . ./auth.local; set +a; }
  if [ -z "$BLOG_USER" ] || [ -z "$BLOG_PASS" ]; then
    say ""
    say "🔐 업로더에 쓸 아이디/비밀번호를 정해주세요. (핸드폰에서 접속할 때 물어봐요)"
    read -r -p "   아이디: " BLOG_USER < /dev/tty
    read -r -s -p "   비밀번호: " BLOG_PASS < /dev/tty
    say ""
    printf 'BLOG_USER=%s\nBLOG_PASS=%s\n' "$BLOG_USER" "$BLOG_PASS" > auth.local
    chmod 600 auth.local
    say "   ✅ auth.local 에 저장했어요."
  fi
  export BLOG_USER BLOG_PASS

  say ""
  say "🧹 이전에 켜둔 것 정리 중..."
  do_stop
  sleep 2

  # 화면을 꺼도 안드로이드가 Termux 를 재우지 않게
  command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock

  mkdir -p inbox posts
  nohup python uploader.py        > uploader.log 2>&1 &
  nohup python uploader_travel.py > uploader_travel.log 2>&1 &
  sleep 2

  : > tunnel.log; : > tunnel_travel.log
  nohup cloudflared tunnel --url http://localhost:8765 > tunnel.log 2>&1 &
  nohup cloudflared tunnel --url http://localhost:8766 > tunnel_travel.log 2>&1 &

  say "🌐 바깥 접속 주소를 받아오는 중... (20초쯤 걸려요)"
  for _ in $(seq 1 40); do
    [ -n "$(find_url tunnel.log)" ] && [ -n "$(find_url tunnel_travel.log)" ] && break
    sleep 1
  done
  do_url
  say ""
  say "💡 Termux 알림에 'wake lock held' 가 떠 있어야 화면 꺼도 안 끊겨요."
  say "   Termux 앱을 최근 앱에서 밀어서 닫으면 꺼져요."
  say "   사진은 ~/naver-blog-auto/inbox 에 쌓여요."
}

case "${1:-start}" in
  install) do_install ;;
  start)   do_start ;;
  stop)    do_stop; say "✅ 다 껐어요." ;;
  url)     do_url ;;
  *)       say "사용법: termux.sh install | start | url | stop" ;;
esac
