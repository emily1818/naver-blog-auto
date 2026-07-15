#!/usr/bin/env python3
"""티스토리 사진 자동 업로드용 임시 로컬 서버 (CORS 허용).

브라우저 file_upload 도구가 폴더 경로를 거부하므로, 사진 폴더를 이 서버로 서빙하고
페이지 JS에서 fetch → File → #openFile 주입하는 방식으로 우회한다.

- CORS 헤더(Access-Control-Allow-Origin: *) 필수 — 티스토리(https)에서 fetch 가능하게.
- ThreadingHTTPServer 필수 — 단일스레드는 브라우저 커넥션에 걸려 멈춘다.
- 127.0.0.1 은 크롬 mixed-content 예외라 https 페이지에서도 fetch 됨.

사용: python3 tools/tistory_cors_server.py <사진폴더> [포트=8799]
"""
import http.server, os, sys

root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else '.'
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8799
os.chdir(root)


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass

    def address_string(self):
        return '-'


httpd = http.server.ThreadingHTTPServer(('127.0.0.1', port), H)
print(f'serving {root} at http://127.0.0.1:{port}')
httpd.serve_forever()
