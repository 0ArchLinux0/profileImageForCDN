"""Shared brand typography: Lato with ordinary, unslashed default zero.
Used by both channel adapters and the baseline renderer. No platform calls.
"""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageFont
ROOT=Path(__file__).resolve().parent
FONT=ROOT/'fonts/Lato-Regular.ttf'
FONT_BOLD=ROOT/'fonts/Lato-Bold.ttf'
LICENSE=ROOT/'fonts/Lato-OFL.txt'

def zero_diagnostic(font):
    mask=font.getmask('0',mode='L');w,h=mask.size
    im=Image.frombytes('L',(w,h),bytes(mask))
    box=(int(w*.43),int(h*.4),max(int(w*.57),int(w*.43)+1),max(int(h*.6),int(h*.4)+1))
    patch=im.crop(box)
    pixels=list(getattr(patch,'get_flattened_data',patch.getdata)());ink=sum(v>32 for v in pixels)/max(1,len(pixels))
    return {'zero_glyph_size':[w,h],'center_box':list(box),'center_ink_fraction':ink,'ordinary_zero_center_clear':ink<.05}

@lru_cache(maxsize=512)
def load_font(path=None,size=48,bold=False):
    font=ImageFont.truetype(str(path or FONT),int(size))
    try:
        axes=font.get_variation_axes();values=[]
        for axis in axes:
            name=axis['name'].decode() if isinstance(axis['name'],bytes) else str(axis['name'])
            value=700 if bold and name.lower()=='weight' else 400 if name.lower()=='weight' else 100 if name.lower()=='width' else axis['default']
            values.append(max(axis['minimum'],min(axis['maximum'],value)))
        font.set_variation_by_axes(values)
    except OSError:
        pass
    return font

def brand_font(size,bold=False):
    return load_font(FONT_BOLD if bold else FONT,size,bold)
