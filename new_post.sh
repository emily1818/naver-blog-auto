#!/bin/bash
# 네이버 블로그 자동 글쓰기 - 사진 목록 확인용 헬퍼
# 사용법: ./new_post.sh

DIR="$(cd "$(dirname "$0")" && pwd)"
PHOTOS="$DIR/photos"

echo "📸 photos/ 폴더의 사진 목록:"
echo "--------------------------------"
count=0
for f in "$PHOTOS"/*; do
  [ -e "$f" ] || continue
  case "$f" in
    *.jpg|*.jpeg|*.png|*.heic|*.JPG|*.JPEG|*.PNG|*.HEIC|*.webp)
      echo "  • $(basename "$f")"
      count=$((count+1))
      ;;
  esac
done
echo "--------------------------------"

if [ "$count" -eq 0 ]; then
  echo "⚠️  사진이 없습니다. photos/ 폴더에 사진을 먼저 넣어주세요."
else
  echo "✅ 사진 $count장 준비됨."
  echo ""
  echo "이제 Claude Code에서 이렇게 말하세요:"
  echo "   \"네이버 블로그 글 만들어줘\""
fi
