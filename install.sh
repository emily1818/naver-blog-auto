#!/bin/bash
# 새 맥/새 계정에서 한 줄로 설치하기.
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/emily1818/naver-blog-auto/main/install.sh)"
# 이미 깔린 건 건너뛰고, 없는 것만 설치한 뒤 업로더까지 켜요.
# 다시 실행해도 괜찮아요 (코드는 최신으로 받아와요).

REPO="https://github.com/emily1818/naver-blog-auto.git"
DEST="$HOME/claude/naver-blog-auto"

echo ""
echo "🐾 블로그 자동 글쓰기 설치를 시작할게요"
echo "=================================="

# ---------- 1. 맥 기본 개발도구 (git, python3) ----------
if ! xcode-select -p >/dev/null 2>&1; then
  echo ""
  echo "🛠  맥 기본 개발도구를 설치할게요."
  echo "   화면에 설치 창이 뜨면 [설치]를 눌러주세요. (몇 분 걸려요)"
  xcode-select --install >/dev/null 2>&1
  until xcode-select -p >/dev/null 2>&1; do sleep 5; done
  echo "   ✅ 개발도구 설치 완료"
else
  echo "✅ 개발도구는 이미 있어요"
fi

# ---------- 2. Homebrew ----------
load_brew() {
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    [ -x "$b" ] && { eval "$("$b" shellenv)"; return 0; }
  done
  return 1
}

if ! command -v brew >/dev/null 2>&1 && ! load_brew; then
  echo ""
  echo "🍺 Homebrew를 설치할게요. (맥 로그인 비밀번호를 물어볼 수 있어요)"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
    echo "❌ Homebrew 설치에 실패했어요. 인터넷 연결을 확인하고 다시 실행해주세요."
    exit 1
  }
  load_brew
  # 다음에 터미널을 열어도 brew를 찾을 수 있게
  BREW_BIN="$(command -v brew)"
  if [ -n "$BREW_BIN" ] && ! grep -q "brew shellenv" "$HOME/.zprofile" 2>/dev/null; then
    echo "eval \"\$($BREW_BIN shellenv)\"" >> "$HOME/.zprofile"
  fi
else
  echo "✅ Homebrew는 이미 있어요"
fi

# ---------- 3. cloudflared (폰 접속용 터널) ----------
if ! command -v cloudflared >/dev/null 2>&1; then
  echo ""
  echo "🌐 cloudflared를 설치할게요."
  brew install cloudflared || { echo "❌ cloudflared 설치 실패"; exit 1; }
else
  echo "✅ cloudflared는 이미 있어요"
fi

# ---------- 4. 코드 받기 ----------
echo ""
if [ -d "$DEST/.git" ]; then
  echo "📥 코드를 최신으로 받아올게요."
  git -C "$DEST" pull --ff-only || echo "⚠️  최신으로 못 받았어요. 지금 있는 코드로 계속할게요."
else
  echo "📥 코드를 받아올게요 → $DEST"
  mkdir -p "$(dirname "$DEST")"
  git clone "$REPO" "$DEST" || { echo "❌ 코드 받기 실패"; exit 1; }
fi

# ---------- 5. 실행 권한 ----------
chmod +x "$DEST"/*.command "$DEST"/install.sh 2>/dev/null

# ---------- 6. 업로더 켜기 ----------
echo ""
echo "=================================="
echo "🎉 설치 끝! 이제 업로더를 켤게요."
echo "   다음부터는 Finder에서 '시작하기.command'만 더블클릭하면 돼요."
echo "   글 쓸 때는:  cd $DEST && claude"
echo "=================================="
exec "$DEST/시작하기.command"
