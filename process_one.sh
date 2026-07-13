#!/bin/bash
# 업로더가 호출하는 자동 처리 스크립트
# 사용법: ./process_one.sh "<inbox 폴더 절대경로>"
BASE="$(cd "$(dirname "$0")" && pwd)"
FOLDER="$1"
LOG="$BASE/auto_process.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 처리 시작: $FOLDER" >> "$LOG"

PROMPT="새로 업로드된 블로그 사진 폴더를 처리해줘.

폴더: $FOLDER
- 그 안의 meta.txt 에 지역/가게/정보/요청 이 들어있어. 사진들도 있어.

할 일:
1) 폴더의 사진을 전부 Read로 보고, 잘 나온 것만 골라 (흐릿/중복/손님얼굴 나온 건 제외).
2) 가게 주소·영업시간이 필요하면 WebSearch/WebFetch로 확인.
3) $BASE/STYLE.md 의 말투('~용' '~어요' '>ㅁ<' '짠-' '빠잉~' 이모지)로,
   $BASE/posts/송쉐프_최종.html 과 똑같은 형식(가운데정렬, 빈줄은 <p>&nbsp;</p>, 색·볼드 span, 사진 자리는 【 📷 사진N_설명 】 텍스트)의 스타일 HTML을
   $BASE/posts/<가게이름>_최종.html 로 새로 작성. 맨 위 <title> 근처 주석에 제목도 넣어줘 (형식: [지역] 특징+메뉴 맛집!! \"가게\").
4) 고른 사진들을 sips로 'sips -Z 1080' 리사이즈해서 $BASE/upload_web_<가게이름>/ 에 1_설명.jpg, 2_설명.jpg ... 순서로 저장.
5) 완성되면 Bash로 'open' 명령으로 그 HTML을 크롬에 띄우고, 사진 폴더도 'open' 으로 열어줘.
6) 마지막에 inbox 폴더 이름 앞에 '완료_' 를 붙여 rename.

요청사항(meta의 '요청')을 글에 꼭 반영하고, 손님 얼굴 사진은 절대 쓰지 마."

cd "$BASE" || exit 1
claude -p "$PROMPT" --permission-mode bypassPermissions >> "$LOG" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 처리 완료" >> "$LOG"
