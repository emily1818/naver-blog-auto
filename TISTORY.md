# 티스토리 자동 발행 가이드 (emily-meow.tistory.com)

네이버 블로그 후기를 **티스토리에도 자동 발행**하기 위한 절차. 티스토리 Open API는
2024.02 완전 종료되어 공식 API 발행은 불가능하므로, 로그인된 크롬(Claude in Chrome)
브라우저 자동화 + 로컬 서버로 사진까지 자동 업로드한다.

## 네이버판과 다른 점 (구글/다음 SEO)
티스토리는 네이버 자체검색이 아니라 **구글·다음** 검색에 노출된다. 그래서:
- **제목**: 실제 검색어 나열형. 예) `종각 야장 술집 추천｜왕초바베큐 종각점 숯불 바베큐 후기 (메뉴·가격·영업시간·주차)`
- **본문**: 네이버판과 문장을 다르게 새로 쓴다(중복 콘텐츠 감점 방지).
- **구조화**: 📌 한눈에 요약 박스 + ❓ 자주 묻는 질문(FAQ) 넣기 → 구글 스니펫 대응.
- 파일: `posts/<가게>_티스토리.html` 로 별도 저장(네이버판 `_최종.html`과 구분).

## 사진 방향·순서·스타일 규칙
[STYLE.md](STYLE.md)를 그대로 따른다 (사진 회전 확인, 반찬·국 먼저·메인 마지막,
가게 내부컷 포함, 일상문장 볼드 금지 등).

## 자동 발행 절차
1. **글쓰기 열기**: `https://emily-meow.tistory.com/manage/newpost/?type=post`
   - 에디터 = TinyMCE, id `editor-tistory` / 제목 = `textarea#post-title-inp`
2. **인라인 스타일 변환**: 티스토리엔 우리 `<style>`이 없으므로 `.big/.mid/.pink/...`
   클래스를 인라인 스타일로 바꿔야 한다. → `tools/tistory_inline_convert.py` 사용.
3. **본문 삽입**: `tinymce.get('editor-tistory').setContent(inlineHTML)`
   - ⚠️ **변환기는 `<p>안녕하세요` 앞을 다 잘라내므로 사진 1(썸네일) 마커가 사라진다.**
     setContent 직후 본문 맨 앞에 마커를 직접 다시 넣어야 한다:
     ```js
     const wrap = ed.getBody().querySelector('div');
     (wrap || ed.getBody()).insertAdjacentHTML('afterbegin',
       '<p style="margin:0;color:#999999;">【 📷 사진 1_XXX 】</p><p style="margin:0;">&nbsp;</p>');
     ```
4. **제목 삽입**: ⚠️ **반드시 `computer` 도구로 "실제 타이핑"** 할 것.
   `textarea#post-title-inp`.value 를 JS로 세팅하고 `input`/`change`/`keyup` 을 dispatch 하면
   화면에는 보이지만 **임시저장에 반영되지 않아 "제목 없음"으로 저장된다** (2026-08-06 확인).
   에디터 본문은 `setContent`로 넣어도 저장되는데, 제목만 이 함정이 있다.
   → JS로 `t.focus()` 한 뒤 `computer.type` 으로 치고, 넣은 뒤 `.value` 를 꼭 확인한다.
5. **사진 자동 업로드 (핵심 우회법)** — `file_upload` 도구는 폴더 경로를 거부(채팅
   첨부만 허용)하므로 로컬 서버로 우회한다:
   - 사진을 ASCII 이름(`p1.jpg`, `p2.jpg` …)으로 복사 후 `tools/tistory_cors_server.py`로
     서빙 (CORS 헤더 필수, **ThreadingHTTPServer** 필수 — 단일스레드는 멈춤).
     변환된 본문 HTML도 같은 폴더에 `body.html`로 두면 페이지에서 fetch로 바로 읽을 수 있다.
   - 페이지 JS에서 `fetch('http://127.0.0.1:8799/파일')` → blob → `new File()`
     → `DataTransfer`로 `#openFile`.files 세팅 → `change` 이벤트 dispatch.
     → 티스토리가 kakaocdn에 실제 업로드하고 커서 위치에 삽입한다.
   - **입력은 1회용**: 슬롯마다 `#openFile`을 새로 만들어야 한다. 만드는 방법이 핵심:
     - **첨부 메뉴 열기는 "실제 마우스 클릭"** — `#attach-layer-btn`(툴바 맨 왼쪽 사진
       아이콘, 좌표 약 `(343, 37)`)을 `computer` 도구로 클릭한다. JS 합성 클릭은 안 열린다.
     - **'사진' 메뉴 항목 클릭은 "JS 합성 클릭"** — `.mce-menu-item` 중 텍스트가 '사진'인
       것에 mousedown/mouseup/click을 dispatch. ⭐ 합성 이벤트는 user activation이 없어서
       **네이티브 파일 선택창이 뜨지 않고** `#openFile`만 생성된다. 실제 클릭하면 OS
       파일 대화상자가 떠서 브라우저가 막힌다.
     - 즉 슬롯당 2단계: `computer.left_click(343,37)` → `javascript_tool`로 사진항목 클릭 +
       파일 주입. 이 순서를 슬롯 수만큼 반복.
   - 삽입 직전 `ed.selection`을 해당 마커 `<p>` 뒤로 설정 (`select(p)` → `collapse(false)`).
   - 마커 텍스트(`【 📷 사진 N 】`)는 **모든 슬롯을 다 넣은 뒤 마지막에 일괄 삭제**해도 된다.
     (마커가 선택 기준점이므로 중간에 지우면 다음 슬롯을 못 찾는다)
6. **임시저장**까지만 하고 **발행은 사용자가 직접** 누른다(공개 발행이라 확인 필요).
   임시저장 버튼은 우하단 약 `(1333, 735)`. 옆 숫자가 1 올라가면 저장된 것.
   카테고리는 안 골라도 임시저장되니 발행할 때 사용자가 같이 선택하면 된다.

## 자동화할 때 걸리는 함정 (2026-07-31 실전 기록)
- **카카오 로그인 세션 만료**: `/manage/newpost/`가 `tistory.com/auth/login`으로 리다이렉트되면
  세션이 끊긴 것. **로그인은 내가 못 하니 사용자에게 요청**하고, 로그인 후 다시 열면 된다.
- **백그라운드 탭 타이머 스로틀링** ⭐ 제일 크게 걸렸던 문제. 탭이 비활성이면 크롬이
  `setTimeout`을 심하게 늦춘다. 그래서 `for` 루프 안에서 `await sleep(500)`을 수십 번 도는
  긴 async 함수를 페이지에 던지면 **몇 분씩 멈춘 것처럼 보인다.**
  → 페이지 안에서 긴 폴링 루프를 돌리지 말고, **슬롯 하나당 tool 호출 하나**로 쪼갠다.
  트리거는 `setTimeout(…, 400)` 한 번만 쓰고 즉시 리턴시킨 뒤, 다음 호출에서
  `img` 개수를 읽어 진행 여부를 확인하는 방식이 안정적이다.
- **CDP 45초 제한**: `javascript_tool` 한 번에 오래 `await` 하면
  `Runtime.evaluate timed out after 45000ms`가 난다. 업로드 완료를 한 호출에서 기다리지 말 것.
  `Promise was collected` 에러도 같은 계열인데, **이건 무해하다** — 주입은 이미 실행됐으니
  다음 호출에서 `img` 개수만 확인하면 된다.
- **"이어서 작성하시겠습니까?" 네이티브 confirm**: 이게 뜨면 스크립트 주입 자체가 막혀서
  `screenshot`·`javascript_tool` 전부 `Script injection timed out`으로 실패한다.
  `computer.key Return`이면 닫히지만(= 이어서 작성, 이전 내용 복구) **Escape는 안 통한다.**
  이전 글 내용이 섞이면 곤란하니, **새 글을 쓸 때는 `tabs_create_mcp`로 새 탭을 만드는 게
  가장 깔끔하다** (새 탭에는 대화상자가 안 뜬다). 막힌 탭은 나중에 `tabs_close_mcp`로 닫기.
- **검증은 꼭 하기**: 다 넣은 뒤 `img` 개수와 `src`에 `kakaocdn` 포함 여부를 확인하고,
  본문을 순서대로 훑어 `IMG`와 소제목 순서가 의도대로인지 점검한다.

## 참고
- 사진은 kakaocdn(`blog.kakaocdn.net`) URL로 실제 업로드됨(blob 아님) → 발행 후에도 유지.
- 크롬 확장(Claude in Chrome) 미연결 시: 확장 설치 + 사이드패널 로그인 필요.
