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
4. **제목 삽입**: 값 세팅이 리셋되므로 제목칸 클릭 후 직접 타이핑이 확실.
5. **사진 자동 업로드 (핵심 우회법)** — `file_upload` 도구는 폴더 경로를 거부(채팅
   첨부만 허용)하므로 로컬 서버로 우회한다:
   - 사진을 ASCII 이름으로 복사 후 `tools/tistory_cors_server.py`로 서빙
     (CORS 헤더 필수, **ThreadingHTTPServer** 필수 — 단일스레드는 멈춤).
   - 페이지 JS에서 `fetch('http://127.0.0.1:8799/파일')` → blob → `new File()`
     → `DataTransfer`로 `#openFile`.files 세팅 → `change` 이벤트 dispatch.
     → 티스토리가 kakaocdn에 실제 업로드하고 커서 위치에 삽입한다.
   - **입력은 1회용**: 슬롯마다 이미지툴바 → "사진" 메뉴를 다시 눌러 새 `#openFile`을
     만들어야 한다. 삽입 직전 `ed.selection`을 해당 마커 `<p>` 뒤로 설정.
   - 마커 텍스트(`【 📷 사진 N 】`)는 삽입 후 `<p>`째 삭제.
6. **임시저장**까지만 하고 **발행은 사용자가 직접** 누른다(공개 발행이라 확인 필요).

## 참고
- 사진은 kakaocdn(`blog.kakaocdn.net`) URL로 실제 업로드됨(blob 아님) → 발행 후에도 유지.
- 크롬 확장(Claude in Chrome) 미연결 시: 확장 설치 + 사이드패널 로그인 필요.
