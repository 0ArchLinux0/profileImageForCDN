#!/usr/bin/env python3
"""SS-LEARN-002. Requires Pillow; no bundled fonts or external artwork."""
import argparse
import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Deployment location: instagram/pipeline/quality/squirrel_cards.py.
# Parent supplies pipeline/typography.py and OFL Lato Regular/Bold font.
PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
from typography import load_font

W, H = 1080, 1350

class LayoutError(RuntimeError):
    pass

def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

class Card:
    def __init__(self, content, card, regular, bold):
        self.data, self.card = content, card
        for field in ('title', 'subtitle'):
            rendered = next((t['text'] for t in card['texts'] if t['id'] == field), None)
            if rendered != card.get(field):
                raise LayoutError('Metadata/rendered text mismatch: '+field)
        self.colors = content['design']['palette']
        self.regular, self.bold = regular, bold
        self.image = Image.new('RGB', (W, H), self.colors['cream'])
        self.draw = ImageDraw.Draw(self.image)
        self.qc = {'card': card['number'], 'size': [W, H], 'panels': [], 'text': [], 'errors': []}
        self.names = set()

    def panel(self, name, box, fill=None, outline=None):
        if name in self.names:
            raise LayoutError('Duplicate panel: ' + name)
        self.names.add(name)
        if not (0 <= box[0] < box[2] <= W and 0 <= box[1] < box[3] <= H):
            raise LayoutError('Panel outside canvas: ' + name)
        self.qc['panels'].append({'id': name, 'bbox': list(box)})
        if fill or outline:
            self.draw.rounded_rectangle(box, radius=22, fill=self.colors.get(fill, fill), outline=self.colors.get(outline, outline), width=2)
        return box

    def text(self, name, text, box, size=34, minimum=26, bold=False, color='blue', align='left'):
        self.panel(name, box)
        x0, y0, x1, y1 = box
        width, height = x1-x0, y1-y0
        fontpath = self.bold if bold else self.regular
        chosen = None
        for pts in range(size, minimum-1, -1):
            font = load_font(fontpath, pts, bold=bold)
            lines = []
            valid = True
            for paragraph in text.split('\n'):
                line = ''
                for word in paragraph.split():
                    wb = self.draw.textbbox((0,0), word, font=font, anchor='lt')
                    if wb[2]-wb[0] > width:
                        valid = False
                        break
                    attempt = (line + ' ' + word).strip()
                    bounds = self.draw.textbbox((0,0), attempt, font=font, anchor='lt')
                    if bounds[2]-bounds[0] <= width:
                        line = attempt
                    else:
                        lines.append(line)
                        line = word
                if not valid:
                    break
                lines.append(line)
            step = math.ceil(pts * 1.27)
            maxink = max((self.draw.textbbox((0,0), s, font=font, anchor='lt')[3] for s in lines), default=0)
            used = max(0, len(lines)-1)*step + maxink
            if valid and used <= height:
                chosen = font, lines, step, pts
                break
        if chosen is None:
            raise LayoutError('Text cannot fit panel ' + name)
        font, lines, step, pts = chosen
        record = {'panel': name, 'text': text, 'font_size': pts, 'requested_size': size, 'line_bboxes': []}
        for idx, line in enumerate(lines):
            ink = self.draw.textbbox((0,0), line, font=font, anchor='lt')
            line_width = ink[2]-ink[0]
            x = x0 + ((width-line_width)/2 if align == 'center' else 0) - ink[0]
            y = y0 + idx*step - ink[1]
            actual = list(self.draw.textbbox((x,y), line, font=font, anchor='lt'))
            if actual[0] < x0 or actual[1] < y0 or actual[2] > x1 or actual[3] > y1:
                raise LayoutError('Text ink outside panel ' + name)
            self.draw.text((x,y), line, font=font, fill=self.colors[color], anchor='lt')
            if line:
                record['line_bboxes'].append(actual)
        boxes = record['line_bboxes']
        record['bbox'] = [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)] if boxes else [x0,y0,x0,y0]
        self.qc['text'].append(record)

    def arrow(self, start, end, color='auburn'):
        c = self.colors[color]
        self.draw.line([start,end], fill=c, width=4)
        angle = math.atan2(end[1]-start[1], end[0]-start[0])
        for offset in (-0.55, 0.55):
            point = (end[0]-17*math.cos(angle+offset), end[1]-17*math.sin(angle+offset))
            self.draw.line([point,end], fill=c, width=4)

    def common(self):
        self.draw.rectangle((0,0,18,H), fill=self.colors['auburn'])
        self.draw.line((70,1215,1010,1215), fill=self.colors['blue'], width=2)

    def render(self):
        self.common()
        c = self.card
        self.qc['graphics'] = []
        for g in c['graphics']:
            box = g['box']
            if not (0 <= box[0] <= box[2] <= W and 0 <= box[1] <= box[3] <= H):
                raise LayoutError('Graphic outside canvas: ' + g['id'])
            fill = self.colors.get(g['fill'], g['fill'])
            if g['type'] == 'line':
                self.draw.line(box, fill=fill, width=3)
            elif g['type'] == 'rect':
                self.draw.rectangle(box, fill=fill)
            elif g['type'] == 'rounded':
                self.draw.rounded_rectangle(box, radius=22, fill=fill)
            else:
                raise LayoutError('Unknown graphic type: ' + g['type'])
            self.qc['graphics'].append({'id': g['id'], 'bbox': box, 'type': g['type']})
        for t in c['texts']:
            self.text(t['id'], t['text'], t['box'], t['size'], t['minimum'],
                      t['bold'], t['color'], t['align'])
        boxes = [(r['panel'], i, b) for r in self.qc['text'] for i, b in enumerate(r['line_bboxes'])]
        for idx, (name, ln, box) in enumerate(boxes):
            for other, oln, ob in boxes[idx+1:]:
                if intersects(box, ob):
                    self.qc['errors'].append('Text overlap: %s[%d] / %s[%d]' % (name,ln,other,oln))
        if self.qc['errors']:
            raise LayoutError('; '.join(self.qc['errors']))
        self.qc['text_bounds_kind'] = 'measured glyph ink via Pillow textbbox'
        self.qc['no_text_overlap'] = True
        self.qc['status'] = 'pass'
        return self.image

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('content',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--font-regular',type=Path,required=True)
    parser.add_argument('--font-bold',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    report={'candidate_id':'SS-LEARN-002','status':'pending','cards':[], 'errors':[], 'fonts':{'regular':str(args.font_regular),'bold':str(args.font_bold),'license':'Lato Regular/Bold font, SIL Open Font License 1.1; binaries and OFL supplied by parent.'}}
    try:
        data=json.loads(args.content.read_text(encoding='utf-8'))
        if data['candidate_id'] != 'SS-LEARN-002' or len(data['cards']) != 5:
            raise ValueError('Expected exactly five cards for SS-LEARN-002')
        if data['dimensions'] != {'width':1080,'height':1350}:
            raise ValueError('Expected 1080x1350 dimensions')
        if [c['number'] for c in data['cards']] != [1,2,3,4,5]:
            raise ValueError('Card numbers must be 1..5')
        for font in (args.font_regular,args.font_bold):
            if not font.is_file():
                raise ValueError('Font file missing: '+str(font))
        for content_card in data['cards']:
            card=Card(data,content_card,args.font_regular,args.font_bold)
            report['cards'].append(card.qc)
            image=card.render()
            filename='SS-LEARN-002-%02d.png' % content_card['number']
            image.save(args.out/filename)
            card.qc['file']=filename
        report['status']='pass'
    except Exception as exc:
        report['status']='fail'
        report['errors'].append(type(exc).__name__+': '+str(exc))
        if report['cards']:
            report['cards'][-1]['status']='fail'
        raise
    finally:
        (args.out/'layout-qc.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

if __name__ == '__main__':
    main()
