#!/usr/bin/env python3
"""티스토리 예약 업로드용 묶음 만들기.

posts/_티스토리_업로드현황.txt 의 "## 남은 것" 목록을 순서대로 읽어
upload/tistory_bundles/<key>/ 에 body.html(인라인 변환) + p1.jpg… 를 만들고
manifest.json(key·제목·카테고리·사진 그룹)을 쓴다. upload/ 는 git 제외 폴더.

사용: python3 tools/tistory_build_bundles.py
     python3 tools/tistory_cors_server.py upload/tistory_bundles
그 다음 tools/tistory_upload_helpers.js 순서대로 올린다.
"""
import re, os, json, shutil, sys
sys.path.insert(0,'tools')
from tistory_inline_convert import convert
OUT='upload/tistory_bundles'
todo=open('posts/_티스토리_업로드현황.txt',encoding='utf-8').read().split('## 남은 것')[1].splitlines()[1:]
items=[(None,x.strip()) for x in todo if x.strip() and not x.startswith('#')]
os.makedirs(OUT,exist_ok=True)
travel_kw=('여행','가볼만한곳','숙소','휴게소','전망대','관광')
mukho={1:'올릴순서_무코드/02_바다뷰1.jpg',2:'올릴순서_초당쫄면순두부/01_순두부찌개_썸네일.jpg',3:'올릴순서_등대그집/01_외관_썸네일.jpg',4:'올릴순서_거동탕수육/01_문어탕수육_썸네일.jpg',5:'올릴순서_무코드/01_바다뷰_음료_썸네일.jpg',6:'올릴순서_부흥횟집/23_물회1.jpg',7:'올릴순서_도깨비아이스크림/01_도깨비아이스크림_썸네일.jpg',8:'올릴순서_동해조개빵/01_조개빵_진열_썸네일.jpg',9:'올릴순서_묵호회센터/01_막회_썸네일.jpg',10:'올릴순서_묵호항닭/01_문새닭_썸네일.jpg'}
override={'한국횟집':[[1],[2],[3,4],[5],[6],[7],[],[8],[9,10],[11],[12,13],[14],[15],[16,17],[18,19],[20,21]]}
nocat={'시글루','어깅네일'}
man=[]; problems=[]
for i,(d,s) in enumerate(items,1):
    key=f't{i:03d}'; dd=os.path.join(OUT,key); shutil.rmtree(dd,ignore_errors=True); os.makedirs(dd)
    src=open(f'posts/{s}_티스토리.html',encoding='utf-8').read()
    if '</body>' not in src: src=src+'</body>'
    mc=re.search(r'<!--\s*제목:\s*(.*?)\s*-->',src)
    m=re.search(r'class="title">.*?<br>\s*(.*?)</div>',src,re.S)
    title=mc.group(1).strip() if mc else re.sub('<[^>]+>','',m.group(1)).strip() if m else re.sub('<[^>]+>','',re.search(r'<title>(.*?)</title>',src,re.S).group(1)).strip()
    try: body=convert(src)
    except Exception as e: problems.append((s,'convert',str(e))); continue
    start=src.index('<p>안녕하세요')
    pre=src[:start]; post=src[start:]
    allm=re.findall(r'【\s*📷([^】]*)】',post)
    prem=re.findall(r'【\s*📷([^】]*)】',pre)
    first=prem[-1] if prem else None
    marks=([first] if first else [])+allm
    def nums(t):
        mm=re.match(r'\s*(?:사진\s*)?([\d,\s~\-]+)',t)
        if not mm: return None
        r=[]
        for part in mm.group(1).replace(' ','').strip(',').split(','):
            if not part: continue
            if '~' in part or '-' in part:
                a,b=re.split('[~-]',part); r+=list(range(int(a),int(b)+1))
            else: r.append(int(part))
        return r
    groups=[nums(t) for t in marks]
    if any(g is None for g in groups): problems.append((s,'marker',marks[:3])); continue
    if s in override: groups=override[s]
    firstdesc=re.sub(r'^\s*(?:사진\s*)?[\d,]+번?\s*[·_]?\s*','',marks[0]).strip() if first else ''
    body=re.sub(r'<p[^>]*>【\s*🎥[^】]*】</p>(<p[^>]*>&nbsp;</p>)?','',body)
    body=re.sub(r'<p[^>]*>\(자세한 후기 → 링크\)</p>(<p[^>]*>&nbsp;</p>)?','',body)
    open(os.path.join(dd,'body.html'),'w',encoding='utf-8').write(body)
    need=sorted({n for g in groups for n in g}); missing=[]
    if s=='묵호여행코스':
        for n in need: shutil.copy(mukho[n],f'{dd}/p{n}.jpg')
    else:
        cands=[f'올릴순서_{s}',f'upload_web_{s}']
        fd=next((c for c in cands if os.path.isdir(c)),None)
        files={}
        if fd:
            for f in os.listdir(fd):
                mm=re.match(r'(\d+)[_.]',f)
                if mm and f.lower().endswith(('.jpg','.jpeg','.png','.heic','.webp')): files[int(mm.group(1))]=f
        for n in need:
            if n in files: shutil.copy(os.path.join(fd,files[n]),f'{dd}/p{n}.jpg')
            else: missing.append(n)
    if missing: groups=[[n for n in g if n not in missing] for g in groups]
    cat='여행' if s=='묵호여행코스' else '카테고리 없음' if s in nocat else ('여행' if any(k in title for k in travel_kw) and '맛집' not in title else '맛집')
    bm=len(re.findall('【 📷',body))
    ok = bm+ (1 if first else 0) == len(groups)
    man.append(dict(key=key,store=s,title=title,cat=cat,groups=groups,first=firstdesc,hasfirst=bool(first),missing=missing,))
    print(key,s,cat,'slots',len(groups),'ok' if ok else f'MISMATCH body={bm}','first' if first else 'NOFIRST','miss',missing[:5],'|',title[:30])
json.dump(man,open(os.path.join(OUT,'manifest.json'),'w',encoding='utf-8'),ensure_ascii=False)
print('problems',problems); print('count',len(man))
