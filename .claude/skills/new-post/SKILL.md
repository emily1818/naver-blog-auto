---
name: new-post
description: "새글 왔어/새글 올라왔어/사진 올라왔어" — 업로더에 올라온 사진으로 네이버+티스토리 글을 쓴다. 토큰 아끼는 고정 절차.
---

# 새글 작성 (토큰 절약판)

이전 대화·이전 글은 보지 않는다. 이 파일 + STYLE.md만 기준으로 한다. 서브에이전트 쓰지 않는다(토큰 많이 듦). 묻지 않고 끝까지 한다.

1. `ArtifactData` query `uploads` where `status == "new"` (url https://claude.ai/artifact/H41SwXhd3kidaW6GBaQzM3).
2. 업로드마다:
   - 사진: `Artifact` read `path`=asset id, 한 번에 하나씩 병렬. 저장된 파일을 `inbox/<stamp>_<region>_<store>/NN.jpg`로 복사, `meta.txt` 작성.
   - 보기: `python3 tools/fetch_sheet.py inbox/<폴더> <scratchpad>/sheets_<가게>` → 나온 모아보기만 Read. 원본은 메뉴판·간판 확대가 꼭 필요할 때만 잘라서 1~2장.
   - 정보: **먼저 `python3 tools/kakao_place.py "가게이름 지역"`** → 주소·전화·요일별 영업시간·**메뉴판(메뉴명+가격)**이 한 번에 나온다. 메뉴/가격 섹션은 여기 메뉴로 채운다(먹은 메뉴 + 대표 메뉴 몇 개).
     사진(간판·메뉴판)과 다르면 사진 우선. 카카오에 없을 때만 WebSearch 1~2번(standard). 그래도 없으면 .guide에 "확인 필요".
   - 글: `posts/<가게>_최종.html`, `posts/<가게>_티스토리.html`. 형식은 `형식_템플릿.html`, 말투·순서는 STYLE.md(메인 먼저 → 서브). 협찬 문구 넣지 않음. .guide에 슬롯 → 폰 파일 이름 매핑.
   - `올릴순서_<가게>/`에 슬롯 순서대로 복사 + `_순서표.txt`.
3. HTML 파일을 SendUserFile로 바로 보내고, 업로드 문서를 `update` `{status:"done"}` (if_version 넣기).
4. 답변은 짧게: 제목 + 확인 필요한 것만.
