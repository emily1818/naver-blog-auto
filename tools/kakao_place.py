"""카카오맵에서 가게 정보(주소·전화·영업시간·메뉴 가격) 가져오기.
사용: python3 tools/kakao_place.py "가게이름 지역" """
import sys, json, re, urllib.request, urllib.parse
H = {"Referer": "https://map.kakao.com/", "User-Agent": "Mozilla/5.0"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=15).read().decode()
t = get("https://search.map.kakao.com/mapsearch/map.daum?" + urllib.parse.urlencode({"q": sys.argv[1], "msFlag": "A", "sort": "0"}))
pl = json.loads(t if t.lstrip().startswith("{") else re.sub(r'^[^(]*\(|\);?\s*$', '', t)).get("place", [])
if not pl: sys.exit("못 찾음")
p = pl[0]; pid = p["confirmid"]
print(f"이름: {p.get('name')}\n주소: {p.get('new_address') or p.get('address')}\n전화: {p.get('tel')}\n링크: https://place.map.kakao.com/{pid}")
d = json.loads(get(f"https://place-api.map.kakao.com/places/panel3/{pid}"))
print("영업시간:")
for w in (d.get("open_hours") or {}).get("week_from_today", {}).get("week_periods", [])[:1]:
    for day in w.get("days", []):
        o = day.get("on_days") or {}
        print(" ", day.get("day_of_the_week_desc"), o.get("start_end_time_desc") or "휴무", " ".join(o.get("break_times_desc") or []))
items = ((d.get("menu") or {}).get("menus") or {}).get("items") or []
print(f"메뉴({len(items)}):")
for m in items: print(f"  {m.get('name')} — {m.get('price') or '가격없음'}")
tags = re.findall(r'"(?:name|title|text)[^"]*": "([^"]{1,20})"', json.dumps(d.get("place_add_info", {}), ensure_ascii=False))
print("편의:", ", ".join(t for t in dict.fromkeys(tags) if re.search(r"주차|반려|예약|포장|와이파이|단체|룸", t)))
