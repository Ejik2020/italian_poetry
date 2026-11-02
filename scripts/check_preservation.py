"""One-time redesign audit against the annotated pre-redesign tag.

Optional --baseline-html checks rendered text and explicit break counts too.
Do not use this against future intentional content edits without choosing a new
appropriate baseline.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess

class Content(HTMLParser):
    void = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    chrome = {'edition-masthead','readingbar','poem-panel','mobile-shade','home-reading-action'}
    def __init__(self, html):
        super().__init__(); self.stack=[]; self.text=[]; self.breaks=0; self.feed(html)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); parent=self.stack[-1] if self.stack else ('',False,False)
        inside=parent[1] or tag=='main'
        excluded=parent[2] or tag in {'script','style'} or bool(self.chrome & set(attrs.get('class','').split()))
        if inside and not excluded and tag=='br': self.breaks+=1
        if tag not in self.void: self.stack.append((tag,inside,excluded))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]; break
    def handle_data(self, data):
        if self.stack and self.stack[-1][1] and not self.stack[-1][2]: self.text.append(data)
    def normalized(self): return re.sub(r'\s+',' ',' '.join(self.text)).strip()

parser=argparse.ArgumentParser()
parser.add_argument('--baseline',default='v1.0-pre-redesign')
parser.add_argument('--baseline-html',type=Path)
args=parser.parse_args()
paths=[*Path('.').glob('*.qmd'),*[p for p in Path('images').rglob('*') if p.is_file()]]
for p in paths:
    original=subprocess.check_output(['git','show',args.baseline+':'+p.as_posix()])
    assert original==p.read_bytes(), f'Content changed: {p}'
print(f'{len(paths)} source and image files match {args.baseline} byte for byte.')
if args.baseline_html:
    pages=list(Path('_book').glob('*.html'))
    for p in pages:
        before=Content((args.baseline_html/p.name).read_text())
        after=Content(p.read_text())
        assert before.normalized()==after.normalized(), f'Rendered text changed: {p.name}'
        assert before.breaks==after.breaks, f'Explicit line breaks changed: {p.name}'
    print(f'All {len(pages)} rendered pages retain their complete text and explicit break counts.')
