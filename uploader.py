#!/usr/bin/env python3
# 폰 → Mac 사진 업로드 웹앱 (Claude Code가 처리하는 창구)
import os, datetime, re
from flask import Flask, request

BASE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(BASE, "inbox")
os.makedirs(INBOX, exist_ok=True)

app = Flask(__name__)

# ===== 로그인 (실제 값은 환경변수 BLOG_USER / BLOG_PASS 로 주입) =====
# git 에 비번이 올라가지 않도록 코드엔 기본값(placeholder)만 둡니다.
USERNAME = os.environ.get("BLOG_USER", "admin")
PASSWORD = os.environ.get("BLOG_PASS", "admin")

@app.before_request
def require_login():
    auth = request.authorization
    if not auth or auth.username != USERNAME or auth.password != PASSWORD:
        return ("로그인이 필요해요", 401,
                {"WWW-Authenticate": 'Basic realm="Doong Blog Uploader"'})
# ==============================================

FORM = """
<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>사진 업로더</title>
<style>
  body{font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;background:#f4f6fa;margin:0;padding:24px;color:#2f3542}
  .card{max-width:520px;margin:0 auto;background:#fff;border-radius:20px;padding:26px;box-shadow:0 6px 24px rgba(0,0,0,.06)}
  h1{font-size:22px;margin:0 0 4px}
  p.sub{color:#8a93a3;font-size:14px;margin:0 0 22px}
  label{display:block;font-weight:700;margin:16px 0 6px;font-size:15px}
  input[type=text],textarea{width:100%;box-sizing:border-box;padding:13px;border:1.5px solid #e1e5ee;border-radius:12px;font-size:16px}
  textarea{height:70px;resize:vertical}
  input[type=file]{width:100%;box-sizing:border-box;padding:13px;border:1.5px dashed #b7c0d0;border-radius:12px;background:#fafbfd;font-size:14px}
  button{width:100%;margin-top:22px;padding:15px;border:0;border-radius:14px;background:#2e86de;color:#fff;font-size:17px;font-weight:800}
  .ok{background:#eafaf1;border:1px solid #cdefda;color:#1e824c;padding:16px;border-radius:14px;font-size:15px;line-height:1.6}
</style></head><body><div class=card>
<h1>🐾 사진 업로더</h1>
<p class=sub>사진이랑 정보만 올리면 Mac에서 글이 만들어져요</p>
<form method=post action=/upload enctype=multipart/form-data>
  <label>📍 지역</label>
  <input type=text name=region placeholder="예: 어린이대공원" required>
  <label>🏠 가게 이름</label>
  <input type=text name=store placeholder="예: 서북면옥" required>
  <label>📝 아는 정보 (선택)</label>
  <textarea name=note placeholder="가게 사실 정보. 예: 노키즈존, 주차 불가, 영업 11시~"></textarea>
  <label>✍️ 이렇게 써줘 (선택)</label>
  <textarea name=request placeholder="하고 싶은 말/요청. 예: 친구랑 간 얘기 넣어줘, 물냉면 강조해줘"></textarea>
  <label>📸 사진 · 🎥 동영상 (여러 개 선택 가능)</label>
  <input type=file name=photos accept="image/*,video/*" multiple required>
  <button type=submit>올리기</button>
</form>
</div></body></html>
"""

OK_PAGE = """
<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>완료</title>
<style>body{{font-family:-apple-system,sans-serif;background:#f4f6fa;margin:0;padding:24px}}
.card{{max-width:520px;margin:0 auto;background:#fff;border-radius:20px;padding:26px;box-shadow:0 6px 24px rgba(0,0,0,.06)}}
.ok{{background:#eafaf1;border:1px solid #cdefda;color:#1e824c;padding:18px;border-radius:14px;font-size:16px;line-height:1.7}}
a{{display:block;text-align:center;margin-top:20px;color:#2e86de;font-weight:700;text-decoration:none}}</style>
</head><body><div class=card>
<div class=ok>✅ <b>{n}장</b> 업로드 완료!<br><br>📍 {region} · 🏠 {store}<br><br>이제 Mac의 Claude에게<br><b>"새 글 왔어, 써줘"</b> 라고 하면<br>글이 만들어져요 🎨</div>
<a href="/">← 또 올리기</a>
</div></body></html>
"""

def safe(s):
    return re.sub(r"[^\w가-힣]+", "_", s).strip("_")[:40] or "untitled"

@app.route("/")
def index():
    return FORM

@app.route("/upload", methods=["POST"])
def upload():
    region = request.form.get("region", "").strip()
    store = request.form.get("store", "").strip()
    note = request.form.get("note", "").strip()
    req = request.form.get("request", "").strip()
    photos = request.files.getlist("photos")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = os.path.join(INBOX, f"{stamp}_{safe(region)}_{safe(store)}")
    os.makedirs(folder, exist_ok=True)
    n = 0
    for i, f in enumerate(photos, 1):
        if not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        f.save(os.path.join(folder, f"{i:02d}{ext}"))
        n += 1
    with open(os.path.join(folder, "meta.txt"), "w", encoding="utf-8") as m:
        m.write(f"지역: {region}\n가게: {store}\n정보: {note}\n요청: {req}\n업로드시각: {stamp}\n사진수: {n}\n")
    print(f"[업로드됨] {folder}  (사진 {n}장)")
    return OK_PAGE.format(n=n, region=region, store=store)

if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "<이 Mac의 IP>"
    print("=" * 50)
    print("  사진 업로더 실행 중")
    print(f"  같은 와이파이 폰에서 접속:  http://{ip}:8765")
    print("=" * 50)
    app.run(host="0.0.0.0", port=8765, debug=False)
