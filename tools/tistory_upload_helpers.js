// 티스토리 글쓰기 페이지(/manage/newpost/)에서 javascript_tool로 실행하는 업로드 헬퍼.
// 사진·본문은 tools/tistory_cors_server.py 로 http://127.0.0.1:8799/<key>/ 에서 서빙한다
// (tools/tistory_build_bundles.py 가 <key>/body.html, p1.jpg… , manifest.json 을 만든다).
//
// 순서 (글 1개):
//   1) find "category dropdown combobox" → 그 ref 클릭 (카테고리 목록을 펼쳐둬야 __cat 이 고를 수 있음)
//   2) 이 파일 전체를 실행한 뒤  await __prep('t014')  → 제목 반환 → 제목칸에 computer.type
//   3) 슬롯마다:  computer.left_click(330,34)  (툴바 사진 아이콘, 실제 클릭이어야 메뉴가 열림)
//                 → javascript  await __s('t014', i)  → wait 3초
//   4) __clean() 으로 마커 삭제 → await __sched(2026,11,6) 반환값(날짜·10·00·공개) 확인
//      → document.querySelector('#publish-btn').click() → 글 관리 목록에서 [예약] 확인
// 사진 아이콘 좌표는 창 크기마다 다르니 스크린샷으로 먼저 확인할 것.
// 같은 탭에서 연달아 쓰면 "이어서 작성" 확인창에 막힐 수 있다 → 새 탭(tabs_create)으로 옮기면 된다.
// 새 탭에서는 첫 사진 아이콘 클릭이 자주 안 먹는다(제목칸 포커스 등). 본문을 한 번 클릭하고 다시 눌러볼 것.
//   안 되면 JS로 메뉴를 직접 여는 방법(미검증):
//   tinymce.get('editor-tistory').theme.panel.find('menubutton').filter(c=>c.settings.text==='첨부')[0].showMenu()
// 사진이 blob: 상태로 남으면(업로드 실패) 그 img 를 마커 <p>로 바꾸고 __slot 으로 다시 올린다.

(() => {
  // 에디터는 사진 메뉴 클릭 시 <input type=file>을 만들고 .click() 한다.
  // 합성 클릭엔 user activation 이 없어 파일창이 안 뜨므로, .click() 을 가로채 그 input 을 잡아둔다.
  if (!window.__patched) {
    const oc = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function () {
      if (this.type === 'file') { window.__fi = this; return; }
      return oc.call(this);
    };
    window.__patched = 1;
  }
  const ed = () => tinymce.get('editor-tistory');
  const markers = () => [...ed().getBody().querySelectorAll('p')].filter(p => p.textContent.includes('【 📷'));

  window.__cat = (name) => {
    const o = [...document.querySelectorAll('#category-list [role=option], #category-list li')].find(o => o.textContent.trim() === name);
    if (!o) return 'no ' + name;
    o.click();
    return document.querySelector('#category-btn').textContent.trim();
  };

  window.__load = async (key, first) => {
    const html = await fetch(`http://127.0.0.1:8799/${key}/body.html`).then(r => r.text());
    ed().setContent(html);
    // 변환기가 <p>안녕하세요 앞을 잘라내므로 1번(썸네일) 마커를 다시 넣는다
    const w = ed().getBody().querySelector('div');
    (w || ed().getBody()).insertAdjacentHTML('afterbegin',
      `<p style="margin:0;color:#999999;">【 📷 01번 · ${first} 】</p><p style="margin:0;">&nbsp;</p>`);
    return markers().length;
  };

  window.__slot = async (key, i, nums) => {
    const p = markers()[i];
    ed().selection.select(p); ed().selection.collapse(false);
    window.__fi = null;
    const it = [...document.querySelectorAll('.mce-tistory-attach-item')].find(m => m.textContent.trim() === '사진');
    ['mousedown', 'mouseup', 'click'].forEach(t => it.dispatchEvent(new MouseEvent(t, { bubbles: true })));
    let inp = null;
    for (let k = 0; k < 40 && !inp; k++) { await new Promise(r => setTimeout(r, 100)); inp = window.__fi; }
    if (!inp) return 'no input';
    const fs = await Promise.all(nums.map(n => fetch(`http://127.0.0.1:8799/${key}/p${n}.jpg`)
      .then(r => r.blob()).then(b => new File([b], `p${n}.jpg`, { type: 'image/jpeg' }))));
    const dt = new DataTransfer(); fs.forEach(f => dt.items.add(f));
    inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
    return 'ok ' + nums;
  };

  window.__s = async (key, i) => {
    const m = window.__M.find(x => x.key === key);
    if (i >= m.groups.length) return 'none';
    if (!m.groups[i].length) return 'skip ' + i;
    return window.__slot(key, i, m.groups[i]);
  };

  window.__imgs = () => {
    const b = ed().getBody();
    return [b.querySelectorAll('img').length, [...b.querySelectorAll('img')].filter(i => /kakaocdn/.test(i.src)).length];
  };

  // 마커와 이미지 순서 확인용: "01 I 02 I 03,04 I I …"
  window.__seq = () => {
    const s = [];
    ed().getBody().querySelectorAll('p, img').forEach(n => {
      if (n.tagName === 'IMG') s.push('I');
      else if (n.textContent.includes('【 📷')) s.push(n.textContent.match(/\d[\d,]*/)[0]);
    });
    return s.join(' ');
  };

  window.__clean = () => {
    const b = ed().getBody();
    markers().forEach(p => {
      if (!p.querySelector('img')) {
        const nx = p.nextElementSibling;
        if (nx && nx.tagName === 'P' && nx.textContent.trim() === '' && !nx.querySelector('img')) nx.remove();
        p.remove();
      } else p.childNodes.forEach(c => { if (c.nodeType === 3) c.textContent = c.textContent.replace(/【[^】]*】/, ''); });
    });
    ed().fire('change');
    return [b.textContent.includes('【 📷'), b.querySelectorAll('img').length];
  };

  // 발행 패널을 열고 공개 + 예약(y-m-d 10:00)까지 세팅. 좌표를 안 써서 창 크기와 무관하다.
  // 반환값으로 날짜·시간을 확인한 뒤  document.querySelector('#publish-btn').click()  으로 발행.
  window.__sched = async (y, m, d) => {
    const W = ms => new Promise(r => setTimeout(r, ms));
    if (!document.querySelector('#open20')) {
      [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '완료').click();
      await W(1500);
    }
    document.querySelector('#open20').click(); await W(400);
    if (!document.querySelector('.btn_reserve')) {
      [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '예약').click();
      await W(600);
    }
    if (!document.querySelector('.box_calendar')) { document.querySelector('.btn_reserve').click(); await W(600); }
    for (let k = 0; k < 6; k++) {
      if (document.querySelector('.txt_calendar').textContent.trim() === `${y}년 ${m}월`) break;
      document.querySelector('.box_calendar .btn_next').click(); await W(300);
    }
    const day = [...document.querySelectorAll('.box_calendar .btn_day')].find(b => b.textContent.trim() === String(d) && !b.disabled);
    if (!day) return 'no day';
    day.click(); await W(400);
    const set = (el, v) => {
      const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      el.focus(); s.call(el, v);
      ['input', 'change', 'blur'].forEach(e => el.dispatchEvent(new Event(e, { bubbles: true })));
    };
    const [h, mi] = document.querySelectorAll('input[type=number]');
    set(h, '10'); set(mi, '00'); await W(300);
    return [document.querySelector('.btn_reserve').textContent.trim(), h.value, mi.value,
      document.querySelector('#open20').checked, document.querySelector('#publish-btn').textContent.trim()];
  };

  window.__prep = async (key) => {
    window.__M = await fetch('http://127.0.0.1:8799/manifest.json').then(r => r.json());
    const m = window.__M.find(x => x.key === key);
    const c = window.__cat(m.cat);
    const n = await window.__load(key, m.first);
    document.querySelector('#post-title-inp').focus();
    return [c, m.title, m.groups.length, n];
  };
})();
