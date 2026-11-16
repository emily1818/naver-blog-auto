"""네이버판 분량 검사 (2026-11-16 사용자 확정).
기준(공백 포함 글자수, 사진 슬롯 수에 따라):
  - 사진 많음(슬롯 12개 이상): 약 4,500자 → 4,000~5,200자
  - 쓸 내용이 적음(슬롯 12개 미만): 2,000~3,500자
사용: python3 tools/check_length.py posts/<가게>_최종.html ..."""
import sys, re
bad = 0
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read().split('<div class="title">', 1)[-1]
    ps = re.findall(r"<p[^>]*>(.*?)</p>", s)
    slots = sum("【" in p for p in ps)
    lines = [re.sub(r"<[^>]+>", "", p).replace("&amp;", "&") for p in ps if p.strip() != "&nbsp;" and "【" not in p]
    n = len("\n".join(lines))
    lo, hi = (4000, 5200) if slots >= 12 else (2000, 3500)
    ok = lo <= n <= hi
    bad += not ok
    print(("✅" if ok else "❌"), f, f"공백포함 {n}자 (사진 슬롯 {slots}개 → 목표 {lo}~{hi}자)")
sys.exit(1 if bad else 0)
