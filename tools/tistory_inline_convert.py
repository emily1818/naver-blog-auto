#!/usr/bin/env python3
"""티스토리용 인라인 스타일 변환기.

posts/<가게>_티스토리.html 처럼 CSS 클래스를 쓴 후기 HTML을 받아,
클래스를 인라인 스타일로 바꿔서 TinyMCE(tinymce.setContent)에 바로 넣을 수 있는
본문 HTML로 변환한다. (티스토리엔 우리 <style>이 없어 클래스가 안 먹기 때문)

사용: python3 tools/tistory_inline_convert.py posts/왕초바베큐_티스토리.html > out.html
"""
import re, sys

CLS = {
    'big':  'font-size:16px;font-weight:800;',
    'mid':  'font-size:15px;font-weight:700;',
    'blue': 'color:#2e86de;font-weight:800;',
    'pink': 'color:#eb3b5a;font-weight:700;',
    'orange':'color:#fa8231;font-weight:700;',
    'green':'color:#20bf6b;font-weight:700;',
    'purple':'color:#8854d0;font-weight:700;',
    'gray': 'color:#999999;',
}
BOX = ('background:#f6f7f9;border:1px solid #e3e6ea;border-radius:10px;'
       'padding:14px 18px;margin:10px 0;text-align:left;line-height:1.7;')


def convert(src: str) -> str:
    # 본문만 추출: 첫 <p>안녕하세요 ~ </body> 전
    start = src.index('<p>안녕하세요')
    end = src.index('</body>')
    body = src[start:end].strip()

    body = re.sub(r'<p class="([a-z ]+?)">',
                  lambda m: '<p style="margin:0;' +
                            ''.join(CLS.get(x, '') for x in m.group(1).split()) + '">',
                  body)
    body = re.sub(r'<span class="([a-z]+?)">',
                  lambda m: f'<span style="{CLS.get(m.group(1), "")}">', body)
    body = body.replace('<div class="box">', f'<div style="{BOX}">')
    body = re.sub(r'<p>', '<p style="margin:0;">', body)
    body = body.replace('<p style="text-align:left">', '<p style="margin:0;text-align:left;">')

    return (f'<div style="font-size:13px;line-height:1.9;color:#3a3a3a;'
            f'text-align:center;">{body}</div>')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: tistory_inline_convert.py <가게_티스토리.html>')
    with open(sys.argv[1], encoding='utf-8') as f:
        sys.stdout.write(convert(f.read()))
