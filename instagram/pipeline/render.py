#!/usr/bin/env python3
"""Deterministic offline Instagram media renderer. NEVER posts to a platform."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BRANDS = {
    'greyvisual2026': dict(bg='#242729', fg='#F6F2E8', accent='#D8E19C', muted='#B3B8B5'),
    'squirrelsnow2026': dict(bg='#C9DFE8', fg='#26363A', accent='#AF623D', muted='#556B71'),
}
SIZES = {'reel': (1080, 1920), 'carousel': (1080, 1350)}
from typography import brand_font

def font(size):
    return brand_font(size)

def validate(doc):
    required = ('id', 'account', 'format', 'title', 'rights', 'evidence', 'items')
    missing = [k for k in required if not doc.get(k)]
    if missing:
        raise ValueError('Missing required fields: ' + ', '.join(missing))
    if not re.fullmatch(r'[A-Z0-9_-]{4,64}', doc['id']):
        raise ValueError('Invalid content id')
    if doc['account'] not in BRANDS or doc['format'] not in SIZES:
        raise ValueError('Unknown account/format')
    if doc['rights'] != 'original_or_licensed_verified':
        raise ValueError('Rights provenance must be explicitly verified')
    if not isinstance(doc['evidence'], list) or not isinstance(doc['items'], list):
        raise ValueError('evidence and items must be lists')
    if not (2 <= len(doc['items']) <= 10):
        raise ValueError('Exactly 2-10 content items required')
    for item in doc['items']:
        if not item.get('heading') or not item.get('detail'):
            raise ValueError('Each item needs heading and detail')
        if doc['format'] == 'reel' and not (2 <= float(item.get('duration', 0)) <= 12):
            raise ValueError('Reel item duration must be 2-12s')
    if doc.get('public_post_approved', False) is not False:
        raise ValueError('Publishing approval is tracked outside source spec')
    return doc

def lines_fit(draw, message, face, max_width):
    out, line = [], ''
    for word in message.split():
        if draw.textbbox((0, 0), word, font=face)[2] > max_width:
            raise ValueError('Unbreakable text exceeds available width')
        candidate = (line + ' ' + word).strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] > max_width and line:
            out.append(line)
            line = word
        else:
            line = candidate
    if line:
        out.append(line)
    return out

def draw_block(draw, text, xy, width, face, fill, spacing=22):
    x, y = xy
    for line in lines_fit(draw, text, face, width):
        offset = draw.textbbox((0, 0), line, font=face)
        origin = (x-offset[0], y)
        ink = draw.textbbox(origin, line, font=face)
        if ink[0] < x or ink[2] > x+width:
            raise ValueError('Text ink exceeds panel width')
        draw.text(origin, line, font=face, fill=fill)
        y += face.size + spacing
    return y

def draw_item(doc, item, index, dest):
    account, kind = doc['account'], doc['format']
    palette = BRANDS[account]
    w, h = SIZES[kind]
    im = Image.new('RGB', (w, h), palette['bg'])
    draw = ImageDraw.Draw(im)
    margin = 102
    draw.rounded_rectangle((72, 85, w-72, h-75), radius=50,
                           outline=palette['muted'], width=3)
    draw.ellipse((w-206, 130, w-128, 208), fill=palette['accent'])
    draw.text((margin, 148), account.upper(), font=font(31), fill=palette['muted'])
    y = 280 if kind == 'reel' else 230
    y = draw_block(draw, item['heading'], (margin, y), w-2*margin,
                   font(88 if kind == 'reel' else 76), palette['fg'], 25)
    y += 76
    value = item.get('emphasis', '')
    if value:
        f = font(112 if kind == 'reel' else 96)
        draw.rounded_rectangle((margin-20, y-22, w-margin+20, y+f.size+65),
                               radius=24, fill=palette['accent'])
        draw_block(draw, value, (margin, y), w-2*margin, f,
                   palette['bg'] if account == 'greyvisual2026' else '#FFFFFF', 10)
        y += f.size + 132
    y = draw_block(draw, item['detail'], (margin, y), w-2*margin,
                   font(48 if kind == 'reel' else 44), palette['fg'], 17)
    if y > h-310:
        raise ValueError(f'Text overflow on card {index}; shorten the content')
    if item.get('figure') == 'probability_grid':
        on = int(item.get('highlight_cells', 0))
        if not (0 <= on <= 100):
            raise ValueError('highlight_cells must be 0..100')
        size, gap = 34, 8
        start_x, start_y = (w-10*size-9*gap)//2, max(y+25, h-690)
        if start_y+10*(size+gap) > h-240:
            raise ValueError('Grid does not fit')
        for n in range(100):
            col, row = n%10, n//10
            x, yy = start_x + col*(size+gap), start_y + row*(size+gap)
            draw.rounded_rectangle((x, yy, x+size, yy+size), radius=9,
                                   fill=palette['accent'] if n < on else palette['muted'])
    label = item.get('footer', 'Learning in progress.' if account == 'squirrelsnow2026'
                     else 'See the reasoning.')
    footer_y = h-250 if kind == 'reel' else h-200
    draw.text((margin, footer_y), label[:52], font=font(28), fill=palette['muted'])
    seg_w = (w-2*margin-16)//len(doc['items'])
    for j in range(len(doc['items'])):
        x = margin + j*(seg_w+16)
        draw.rounded_rectangle((x, h-148, x+seg_w, h-138), radius=5,
                               fill=palette['accent'] if j <= index else palette['muted'])
    im.save(dest, optimize=True)

def ffprobe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt',
                        '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)

def make_reel(items, outputs, out):
    if shutil.which('ffmpeg') is None:
        raise RuntimeError('ffmpeg is needed for Reel, or use --images-only')
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    total = 0
    for item, still in zip(items, outputs):
        duration = float(item['duration'])
        total += duration
        cmd += ['-loop', '1', '-framerate', '30', '-t', str(duration), '-i', str(still)]
    cmd += ['-f', 'lavfi', '-t', str(total), '-i', 'anullsrc=r=48000:cl=stereo']
    filters = ';'.join(f'[{i}:v]format=yuv420p,setsar=1[v{i}]'
                       for i in range(len(items)))
    filters += ';' + ''.join(f'[v{i}]' for i in range(len(items)))
    filters += f'concat=n={len(items)}:v=1:a=0[outv]'
    cmd += ['-filter_complex', filters, '-map', '[outv]', '-map', f'{len(items)}:a',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
            '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '128k',
            '-ar', '48000', '-movflags', '+faststart', '-shortest', str(out)]
    subprocess.run(cmd, check=True)
    p = ffprobe(out)
    video = next((x for x in p['streams'] if x['codec_type'] == 'video'), {})
    audio = next((x for x in p['streams'] if x['codec_type'] == 'audio'), {})
    assert (video.get('width'), video.get('height'), video.get('codec_name')) == (1080, 1920, 'h264')
    assert audio.get('codec_name') == 'aac'
    if abs(float(p['format']['duration'])-total) > 0.25:
        raise ValueError('Rendered Reel duration mismatch')
    return p

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def render(spec, dest, images_only=False):
    doc = validate(json.loads(Path(spec).read_text(encoding='utf-8')))
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, item in enumerate(doc['items']):
        still = dest/f'{doc["id"]}_{i+1:02d}.png'
        draw_item(doc, item, i, still)
        outputs.append(still)
    media = None
    if doc['format'] == 'reel' and not images_only:
        media = dest/f'{doc["id"]}.mp4'
        make_reel(doc['items'], outputs, media)
    if doc['format'] == 'carousel':
        for p in outputs:
            with Image.open(p) as image:
                if image.size != (1080, 1350):
                    raise ValueError('Carousel export wrong size')
    payload = {
        'id': doc['id'], 'account': doc['account'], 'format': doc['format'],
        'state': 'RENDERED_PENDING_OWNER_QA', 'public_post_approved': False,
        'source_sha256': file_hash(spec), 'evidence': doc['evidence'],
        'rights': doc['rights'],
        'asset_sha256': {p.name: file_hash(p) for p in outputs+([media] if media else [])},
        'video_probe': ffprobe(media) if media else None,
        'publish_gate': 'NO_PUBLIC_ACTION_FROM_THIS_PIPELINE',
    }
    (dest/'build-manifest.json').write_text(json.dumps(payload, indent=2,
                                          ensure_ascii=False)+'\n', encoding='utf-8')
    (dest/'caption.txt').write_text(doc.get('caption', '')+'\n', encoding='utf-8')
    return payload

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('spec', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--images-only', action='store_true')
    args = p.parse_args()
    print(json.dumps(render(args.spec, args.out, args.images_only), indent=2)[:3000])

if __name__ == '__main__':
    main()
