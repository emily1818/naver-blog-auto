#!/usr/bin/env python3
# 폰 → Mac 사진/정보 업로드 웹앱 (여행 버전) — Claude Code가 처리하는 창구
# 맛집 업로더(uploader.py)와 같은 틀 + "여행 / 글 종류(맛집·관광지·여행정보)" 추가
import os, datetime, re
from flask import Flask, request

BASE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(BASE, "inbox")          # 맛집과 동일한 inbox 공유 (meta의 '종류'로 구분)
os.makedirs(INBOX, exist_ok=True)

app = Flask(__name__)

# ===== 로그인 (실제 값은 환경변수 BLOG_USER / BLOG_PASS 로 주입) =====
USERNAME = os.environ.get("BLOG_USER", "admin")
PASSWORD = os.environ.get("BLOG_PASS", "admin")

@app.before_request
def require_login():
    auth = request.authorization
    if not auth or auth.username != USERNAME or auth.password != PASSWORD:
        return ("로그인이 필요해요", 401,
                {"WWW-Authenticate": 'Basic realm="Doong Travel Uploader"'})
# ==============================================

FORM = """
<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>여행 업로더</title>
<style>
  :root{--main:#f0932b;--ink:#2f3542;--sub:#8a93a3;--line:#e1e5ee}
  body{font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;background:#fbf7f0;margin:0;padding:24px;color:var(--ink)}
  .card{max-width:520px;margin:0 auto;background:#fff;border-radius:20px;padding:26px;box-shadow:0 6px 24px rgba(0,0,0,.06)}
  h1{font-size:22px;margin:0 0 4px}
  p.sub{color:var(--sub);font-size:14px;margin:0 0 22px}
  label{display:block;font-weight:700;margin:18px 0 6px;font-size:15px}
  input[type=text],textarea{width:100%;box-sizing:border-box;padding:13px;border:1.5px solid var(--line);border-radius:12px;font-size:16px}
  textarea{height:70px;resize:vertical}
  textarea.big{height:150px}
  input[type=file]{width:100%;box-sizing:border-box;padding:13px;border:1.5px dashed #d8ba8f;border-radius:12px;background:#fdfaf4;font-size:14px}
  .seg{display:flex;gap:8px;margin-top:4px}
  .seg label{flex:1;margin:0;text-align:center;padding:13px 6px;border:1.5px solid var(--line);border-radius:12px;font-weight:700;color:var(--sub);cursor:pointer;transition:.15s}
  .seg input{display:none}
  .seg input:checked+span{color:#fff}
  .seg label:has(input:checked){background:var(--main);border-color:var(--main);color:#fff}
  .seg label span{display:block;font-size:15px}
  .seg label small{display:block;font-weight:500;font-size:11px;opacity:.8;margin-top:2px}
  .hint{font-size:12.5px;color:var(--sub);margin:6px 2px 0;line-height:1.5}
  button{width:100%;margin-top:24px;padding:15px;border:0;border-radius:14px;background:var(--main);color:#fff;font-size:17px;font-weight:800}
</style></head><body><div class=card>
<h1>✈️ 여행 업로더</h1>
<p class=sub>여행·종류·사진만 올리면 Mac에서 글이 만들어져요</p>
<form method=post action=/upload enctype=multipart/form-data>

  <label>🧳 여행 (나라/도시)</label>
  <input type=text name=trip placeholder="예: 모로코, 홍콩, 크루즈" required>

  <label>🗂 글 종류</label>
  <div class=seg>
    <label><input type=radio name=kind value="맛집" checked><span>🍽 맛집<small>식당·카페</small></span></label>
    <label><input type=radio name=kind value="관광지"><span>📸 관광지<small>명소·볼거리</small></span></label>
    <label><input type=radio name=kind value="여행정보"><span>📝 여행정보<small>준비물·일정</small></span></label>
  </div>
  <p class=hint id=kindHint>🍽 구글 지도 + 리뷰로 정보 찾아서 맛집 글로 써드려요.</p>

  <label>📍 지역/도시 <span style="font-weight:400;color:#8a93a3">(선택)</span></label>
  <input type=text name=region placeholder="예: 마라케시, 셰프샤우엔">

  <label id=placeLbl>🏛 장소 이름 <span style="font-weight:400;color:#8a93a3">(선택)</span></label>
  <input type=text name=place placeholder="예: 자마엘프나 광장 / 리야드OO">

  <label>✍️ 이렇게 써줘 (선택)</label>
  <textarea name=request class=big placeholder="하고 싶은 말/요청/아는 정보 다 적어주세요.&#10;예)&#10;· 노을이 진짜 예뻤어&#10;· 입장료·가는 법 넣어줘&#10;· 노션 일정이랑 연동해서 써줘"></textarea>

  <label id=photoLbl>📸 사진 · 🎥 동영상 <span style="font-weight:400;color:#8a93a3">(선택)</span></label>
  <input type=file name=photos accept="image/*,video/*" multiple>

  <button type=submit>올리기</button>
</form>
</div>
<script>
  var hints={
    "맛집":"🍽 구글 지도 + 리뷰로 정보 찾아서 맛집 글로 써드려요.",
    "관광지":"📸 구글 지도 + 리뷰로 명소 정보(입장료·가는 법 등) 찾아서 써드려요.",
    "여행정보":"📝 노션의 준비물·일정을 자동으로 가져와서 정리해드려요. (사진 없어도 OK)"
  };
  document.querySelectorAll('.seg input').forEach(function(r){
    r.addEventListener('change',function(){
      document.getElementById('kindHint').textContent=hints[this.value];
    });
  });
</script>
</body></html>
"""

OK_PAGE = """
<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>완료</title>
<style>body{{font-family:-apple-system,sans-serif;background:#fbf7f0;margin:0;padding:24px}}
.card{{max-width:520px;margin:0 auto;background:#fff;border-radius:20px;padding:26px;box-shadow:0 6px 24px rgba(0,0,0,.06)}}
.ok{{background:#fff3e0;border:1px solid #ffe0b2;color:#b26a00;padding:18px;border-radius:14px;font-size:16px;line-height:1.7}}
a{{display:block;text-align:center;margin-top:20px;color:#f0932b;font-weight:700;text-decoration:none}}</style>
</head><body><div class=card>
<div class=ok>✅ <b>{n}장</b> 업로드 완료!<br><br>🧳 {trip} · 🗂 {kind}{place}<br><br>이제 Mac의 Claude에게<br><b>"여행 글 왔어, 써줘"</b> 라고 하면<br>글이 만들어져요 ✈️</div>
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
    trip   = request.form.get("trip", "").strip()
    kind   = request.form.get("kind", "맛집").strip()
    region = request.form.get("region", "").strip()
    place  = request.form.get("place", "").strip()
    req    = request.form.get("request", "").strip()
    photos = request.files.getlist("photos")
    stamp  = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name_bits = [safe(trip), kind, safe(place or region or "여행")]
    folder = os.path.join(INBOX, f"{stamp}_여행_" + "_".join(name_bits))
    os.makedirs(folder, exist_ok=True)
    n = 0
    for i, f in enumerate(photos, 1):
        if not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        f.save(os.path.join(folder, f"{i:02d}{ext}"))
        n += 1
    with open(os.path.join(folder, "meta.txt"), "w", encoding="utf-8") as m:
        m.write(
            f"분류: 여행\n"
            f"여행: {trip}\n"
            f"종류: {kind}\n"
            f"지역: {region}\n"
            f"장소: {place}\n"
            f"요청: {req}\n"
            f"업로드시각: {stamp}\n"
            f"사진수: {n}\n"
        )
    print(f"[여행 업로드] {folder}  (종류 {kind}, 사진 {n}장)")
    place_txt = f" · 🏛 {place}" if place else ""
    return OK_PAGE.format(n=n, trip=trip, kind=kind, place=place_txt)

if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
    except Exception:
        ip = "<이 Mac의 IP>"
    print("=" * 50)
    print("  ✈️ 여행 업로더 실행 중")
    print(f"  같은 와이파이 폰에서 접속:  http://{ip}:8766")
    print("=" * 50)
    app.run(host="0.0.0.0", port=8766, debug=False)
