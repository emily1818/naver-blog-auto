"""네이버판 분량 검사. 기준 미달이면 종료코드 1.
사용: python3 tools/check_length.py posts/<가게>_최종.html ...
기준(2026-11-16 사용자 "길게길게"): 본문 텍스트 줄 130줄 이상, 공백 뺀 글자 3,300자 이상(삼정카페 재작성본의 약 1.4배)."""
import sys, re
bad = 0
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read()
    s = s.split('<div class="title">', 1)[-1]
    lines = [l for l in re.findall(r"<p[^>]*>(.*?)</p>", s) if l.strip() not in ("&nbsp;", "") and "【" not in l]
    chars = len(re.sub(r"\s", "", re.sub(r"<[^>]+>", "", "".join(lines))))
    ok = len(lines) >= 130 and chars >= 3300
    bad += not ok
    print(("✅" if ok else "❌"), f, f"{len(lines)}줄 {chars}자")
sys.exit(1 if bad else 0)
