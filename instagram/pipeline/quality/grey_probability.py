#!/usr/bin/env python3
"""GV-003: semantic probability animation, entirely offline; never posts."""
import argparse, hashlib, json, math, shutil, subprocess, wave, sys
from pathlib import Path
from array import array
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from typography import load_font

W,H,FPS,DURATION=1080,1920,30,22
BG='#252729'; FG='#F4F0E7'; ACC='#D6DF98'; MUTED='#ADB5AF'; DARK='#49504D'
class LayoutError(ValueError): pass

def probability(n,p=.01):
    if not 0 <= p <= 1 or n < 0: raise ValueError('Invalid probability model')
    return 1-(1-p)**n

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(doc):
    if doc.get('id')!='GV-003' or doc.get('public_post_approved') is not False:
        raise ValueError('Wrong id or approval gate')
    if doc.get('account')!='greyvisual2026': raise ValueError('Wrong account')
    model=doc['probability']
    if model['p']!=.01 or model['trials']!=100: raise ValueError('This module explains exactly p=.01, n=100')
    if abs(model['exact_value']-probability(100))>1e-12: raise ValueError('Claim differs from arithmetic')
    return doc

class Drawing:
    def __init__(self,regular,bold):
        self.regular,self.bold=regular,bold
        self.fonts={};self.checked={}
        self.safe=(72,155,1008,1665)
        self.current=[]
    def face(self,size,bold=False):
        key=(size,bold)
        if key not in self.fonts: self.fonts[key]=load_font(self.bold if bold else self.regular,size,bold=bold)
        return self.fonts[key]
    def text(self,d,text,box,size=48,bold=False,color=FG,center=False,min_size=None):
        min_size=min_size or size
        x0,y0,x1,y1=box
        for pts in range(size,min_size-1,-1):
            f=self.face(pts,bold)
            lines=text.split('\n');step=round(pts*1.22)
            boxes=[];origins=[]
            for i,line in enumerate(lines):
                b=d.textbbox((0,0),line,font=f,anchor='lt');width=b[2]-b[0]
                left=x0+(x1-x0-width)/2 if center else x0
                x=left-b[0];y=y0+i*step-b[1]
                origins.append((x,y))
                boxes.append(d.textbbox((x,y),line,font=f,anchor='lt'))
            if all(b[0]>=x0 and b[1]>=y0 and b[2]<=x1 and b[3]<=y1 for b in boxes): break
        else: raise LayoutError('Text does not fit: '+text)
        for i,(line,b) in enumerate(zip(lines,boxes)):
            for prev,previous_text in self.current:
                if b[0]<prev[2] and prev[0]<b[2] and b[1]<prev[3] and prev[1]<b[3]:
                    raise LayoutError('Text overlap: '+text+' / '+previous_text)
            self.current.append((b,text))
            if b[0]<self.safe[0] or b[1]<self.safe[1] or b[2]>self.safe[2] or b[3]>self.safe[3]:
                raise LayoutError('Unsafe text margin: '+text)
            d.text(origins[i],line,font=f,anchor='lt',fill=color)
        self.checked[(text,tuple(box))]={'text':text,'panel':list(box),'ink_boxes':[list(b) for b in boxes],'font_size':pts}
    def base(self):
        self.current=[]
        im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
        d.line((84,190,148,190),fill=ACC,width=8)
        self.text(d,'GREY VISUAL / A SENSE OF CHANCE',(170,170,990,215),28,color=MUTED)
        self.text(d,'@greyvisual2026',(84,1620,850,1660),29,color=MUTED)
        return im,d
    def area(self,d,n,y=800,h=370):
        p=probability(n);x,w=120,840
        d.rectangle((x,y,x+w,y+h),fill=DARK)
        boundary=x+w*p
        if p>0:d.rectangle((x,y,boundary,y+h),fill=ACC)
        d.rectangle((boundary-1,y,boundary+1,y+h),fill=FG)
        # Exact 50% reference. At69 the crossing is subpixel at this scale;
        # the explicit50.016% readout establishes the strict crossing honestly.
        for yy in range(y-12,y+h+12,24):d.line((540,yy,540,min(yy+11,y+h+12)),fill=FG,width=2)
        self.text(d,'0%',(120,y+h+25,270,y+h+82),36,color=MUTED)
        self.text(d,'50%',(485,y+h+25,635,y+h+82),36,color=MUTED)
        self.text(d,'100%',(850,y+h+25,992,y+h+82),36,color=MUTED)
        return p
    def footer(self,d):
        self.text(d,'Area = chance, not a win count.',(84,1460,996,1520),43,color=FG,min_size=40)
        self.text(d,'Independent tries. Same 1% each time.',(84,1550,996,1604),36,color=MUTED,min_size=33)
    def grow(self,d,n):
        self.text(d,'At least one success?',(84,300,996,402),76,True,min_size=70)
        self.text(d,f'{n} tries',(84,455,996,570),100,True)
        self.text(d,f'{100*probability(n):.2f}%',(84,610,996,748),132,True,color=ACC)
        self.area(d,n,835,365)
        self.text(d,'1 - 0.99^n',(120,1320,970,1400),62,True,color=ACC)
        self.footer(d)
    def graph(self,d,t):
        x0,x1,y0,y1=205,950,705,1205
        d.line((x0,y0,x0,y1,x1,y1),fill=MUTED,width=3)
        for val in [0,.5,1]:
            yy=y1-(y1-y0)*val
            for xx in range(x0,x1,26):d.line((xx,yy,min(xx+10,x1),yy),fill=MUTED if val==.5 else DARK,width=2)
            self.text(d,f'{int(val*100)}%',(75,yy-15,195,yy+40),32,color=MUTED)
        count=min(100,max(0,int((t-16.5)/2.5*100)))
        pts=[(x0+(x1-x0)*n/100,y1-(y1-y0)*probability(n)) for n in range(count+1)]
        if len(pts)>1:d.line(pts,fill=ACC,width=9)
        if pts:
            x,y=pts[-1];d.ellipse((x-9,y-9,x+9,y+9),fill=ACC)
        if count>=69:
            x=x0+(x1-x0)*.69;y=y1-(y1-y0)*probability(69)
            d.ellipse((x-13,y-13,x+13,y+13),fill=BG,outline=FG,width=4)
            self.text(d,'69: first above 50%',(425,1040,975,1100),38,True,color=FG)
        for n in [0,50,100]:
            xx=x0+(x1-x0)*n/100
            self.text(d,str(n),(xx-25,1230,min(xx+90,1006),1283),36,color=MUTED)
        if count==100:self.text(d,'63.4%',(695,810,995,895),67,True,color=ACC)
    def frame(self,t):
        im,d=self.base()
        if t<2.5:
            self.text(d,'1% each try.',(84,300,996,438),112,True)
            self.text(d,'100 independent tries.',(84,490,996,600),72,True,min_size=66)
            self.text(d,'At least one success?',(84,660,996,770),75,True,min_size=69)
            for k in range(100):
                r,c=divmod(k,10);x=155+c*78;y=875+r*40
                d.ellipse((x,y,x+20,y+20),outline=MUTED,width=3)
            self.text(d,'What is the chance?',(84,1390,996,1460),54,color=FG)
            self.text(d,'Markers = tries, not outcomes.',(84,1490,996,1544),43,color=FG,min_size=40)
            self.text(d,'Independent tries. Same 1% each time.',(84,1560,996,1610),36,color=MUTED,min_size=33)
        elif t<6:
            self.grow(d,min(68,int((t-2.5)/3.5*69)))
        elif t<9.5:
            self.text(d,'69 tries.',(84,300,996,445),120,True)
            self.text(d,'First above 50%.',(84,485,996,575),66,True)
            self.text(d,'50.016%',(84,625,996,770),137,True,color=ACC)
            self.text(d,'68 tries: 49.51%',(84,835,996,905),49,color=MUTED)
            self.area(d,69,980,250)
            self.footer(d)
        elif t<12.5:
            self.grow(d,min(100,69+int((t-9.5)/3*31)))
        elif t<16.5:
            self.text(d,'100 tries.',(84,285,996,400),94,True)
            self.text(d,'63.4%',(84,450,996,620),174,True,color=ACC)
            self.text(d,'at least one success',(84,670,996,750),59,True,min_size=54)
            self.area(d,100,865,255)
            self.text(d,'36.6% get no successes.',(84,1250,996,1320),53,True,min_size=48)
            self.text(d,'100% - 36.6% = 63.4%',(84,1360,996,1440),58,True,color=ACC,min_size=52)
            self.footer(d)
        else:
            self.text(d,'Why 63.4%?',(84,285,996,390),85,True)
            self.text(d,'No successes: 0.99^100',(84,435,996,505),51,min_size=47)
            self.text(d,'At least one: 1 - 0.99^100',(84,535,996,602),49,min_size=45)
            self.graph(d,t)
            self.text(d,'1 - 0.99^100 = 63.4%',(84,1360,996,1445),65,True,color=ACC,min_size=58)
            self.footer(d)
        return im
    def cover(self):
        im,d=self.base()
        self.text(d,'1% each try.',(84,485,996,625),110,True)
        self.text(d,'69 tries.',(84,680,996,820),110,True)
        self.text(d,'First above 50%.',(84,890,996,1005),83,True,min_size=75)
        self.area(d,69,1130,155)
        self.text(d,'50.016%',(84,1395,996,1500),101,True,color=ACC)
        return im

def cue_events():
    return [dict(time=6.0,duration=.14,frequency=660,amplitude=.065,meaning='69trials first crossing of50%'),
            dict(time=12.5,duration=.19,frequency=440,amplitude=.065,meaning='100trials63.4% reveal'),
            dict(time=16.5,duration=.10,frequency=523.25,amplitude=.04,meaning='Complement proof begins')]

def tones(dest):
    rate=48000;events=cue_events();pcm=array('h')
    for i in range(DURATION*rate):
        t=i/rate;value=0.
        for e in events:
            u=t-e['time']
            if 0<=u<e['duration']:
                envelope=math.sin(math.pi*u/e['duration'])**2
                value+=e['amplitude']*envelope*math.sin(2*math.pi*e['frequency']*u)
        sample=round(max(-.3,min(.3,value))*32767);pcm.extend((sample,sample))
    with wave.open(str(dest),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(rate);out.writeframes(pcm.tobytes())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('content',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--font-regular',type=Path,required=True);p.add_argument('--font-bold',type=Path,required=True);p.add_argument('--preview-only',action='store_true')
    args=p.parse_args();doc=validate(json.loads(args.content.read_text()));args.out.mkdir(parents=True,exist_ok=True)
    if doc['duration']!=DURATION:raise ValueError('Spec and renderer duration mismatch')
    art=Drawing(args.font_regular,args.font_bold)
    art.cover().save(args.out/'GV-003-cover.png')
    for sec in [1,5.9,7,11.5,14,20]:art.frame(sec).save(args.out/f'preview-{sec:g}s.png')
    command=None
    if not args.preview_only:
        executable=shutil.which('ffmpeg')
        if not executable:raise RuntimeError('ffmpeg not found')
        wav=args.out/'original-cues.wav';tones(wav);video=args.out/'GV-003.mp4'
        command=[executable,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-ar','48000','-movflags','+faststart','-t',str(DURATION),str(video)]
        with (args.out/'ffmpeg-render.log').open('w') as log:
            proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
            try:
                for frame in range(FPS*DURATION):proc.stdin.write(art.frame(frame/FPS).tobytes())
            except BrokenPipeError:raise RuntimeError('Encoder exited early; see ffmpeg-render.log')
            finally:proc.stdin.close()
            if proc.wait()!=0:raise RuntimeError('Encoder failed; see ffmpeg-render.log')
    report={'id':doc['id'],'revision':'r2','state':'AWAITING_OWNER_APPROVAL','public_post_approved':False,'dimensions':[W,H],'duration':DURATION,'fps':FPS,'source_sha256':sha(args.content),'renderer_sha256':sha(__file__),'font_sha256':{str(x.name):sha(x) for x in [args.font_regular,args.font_bold]},'probability_checks':{str(n):probability(n) for n in [0,1,10,50,68,69,100]},'first_above_half':next(n for n in range(101) if probability(n)>.5),'text_safe_bounds':list(art.safe),'text_blocks_checked':list(art.checked.values()),'ffmpeg_command':command,'preview_only':args.preview_only,'media_qc':'PENDING_EXTERNAL_PROBE_AND_DECODE','audio_events':cue_events(),'direct_listening_status':'BLOCKED: agent has no audio input/listening tool; technical audio QC is not a listening claim.','issues':[]}
    (args.out/'layout-qc.json').write_text(json.dumps(report,indent=2)+'\n')
    (args.out/'caption.txt').write_text(doc['caption']+'\n');print(json.dumps({k:v for k,v in report.items() if k!='text_blocks_checked'},indent=2))
if __name__=='__main__':main()
