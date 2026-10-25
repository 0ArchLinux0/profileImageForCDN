#!/usr/bin/env python3
"""Build two review candidates and optional technical baselines. No publishing/network."""
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from PIL import Image
import PIL
ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,log=None):
    r=subprocess.run([str(x) for x in cmd],capture_output=True,text=True)
    if log:Path(log).write_text('$ '+' '.join(map(str,cmd))+'\n'+r.stdout+r.stderr)
    if r.returncode:raise RuntimeError('Command failed (%s): %s\n%s'%(r.returncode,cmd,r.stderr[-2500:]))
    return r

def environment():
    commit=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True)
    meta={'python':sys.version,'pillow':PIL.__version__,'platform':platform.platform(),'machine':platform.machine(),'source_commit':commit.stdout.strip() if commit.returncode==0 else 'UNKNOWN (archive without .git)'}
    for tool in ['ffmpeg','ffprobe','node']:
        exe=shutil.which(tool)
        meta[tool]={'path':exe,'version':run([exe,'--version' if tool=='node' else '-version']).stdout.splitlines()[0] if exe else None}
    meta['probe_implementation']='Real FFmpeg FFprobe; this build may use documented offline WASM launcher, not a native Mach-O executable.'
    return meta

def qc(folder,content_id,kind,expected_duration=None,variant='candidate'):
    checks=[];pngs=sorted(folder.glob('*.png'))
    required=(1080,1920) if kind=='reel' else (1080,1350)
    for p in pngs:
        with Image.open(p) as im:
            im.load()
            if im.size!=required:raise ValueError('PNG size mismatch: '+str(p))
            if im.mode not in ['RGB','RGBA']:raise ValueError('Unexpected PNG color mode')
            if len(im.getexif()):raise ValueError('Unexpected EXIF metadata')
    checks.append({'name':'PNG full decode, dimensions, color mode, no EXIF','pass':True,'count':len(pngs)})
    video=folder/(content_id+'.mp4');probe=None;audio=None
    if kind=='reel':
        probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_format','-show_streams','-of','json',video],folder/'ffprobe.log').stdout)
        streams=probe['streams'];v=next(s for s in streams if s['codec_type']=='video');a=next(s for s in streams if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'])==(1080,1920,'h264','yuv420p')
        assert Fraction(v['r_frame_rate'])==30 and Fraction(v['avg_frame_rate'])==30
        assert int(v['nb_read_frames'])==int(expected_duration*30)
        assert a['codec_name']=='aac' and int(a['sample_rate'])==48000 and a['channels']==2
        assert abs(float(probe['format']['duration'])-expected_duration)<.08
        checks.append({'name':'Real ffprobe streams, CFR30, decoded frame count, AAC48k stereo and duration','pass':True,'decoded_frames':int(v['nb_read_frames'])})
        run(['ffmpeg','-v','error','-i',video,'-f','null','-'],folder/'decode.log')
        checks.append({'name':'Full native FFmpeg video and audio decode','pass':True})
        vol=run(['ffmpeg','-hide_banner','-i',video,'-vn','-af','volumedetect','-f','null','-'],folder/'audio-qc.log').stderr
        found=re.search(r'max_volume: ([-+\w.]+) dB',vol)
        audio={'max_volume_db':float(found.group(1)) if found and found.group(1) not in ['-inf','inf'] else None,'declared':'original synthesized cues' if variant=='candidate' else 'AAC silence'}
        if audio['max_volume_db'] is not None and audio['max_volume_db']>=-.1:raise ValueError('Audio clipping risk')
        checks.append({'name':'Audio peak headroom','pass':True,'measurement':audio})
    if kind=='carousel':
        slides=[p for p in pngs if re.search(r'[-_]0[1-5]\.png$',p.name)]
        if len(slides)!=5:raise ValueError('Expected exactly five card PNGs, got '+str(len(slides)))
        checks.append({'name':'Exactly five ordered 4:5 carousel cards','pass':True})
    layout=folder/'layout-qc.json'
    if layout.exists():
        q=json.loads(layout.read_text())
        assert not q.get('issues') and not q.get('errors')
        if kind=='carousel':assert q['status']=='pass' and all(c['status']=='pass' for c in q['cards'])
        checks.append({'name':'Renderer-measured text bounds and same-frame text non-overlap','pass':True,'source':'layout-qc.json'})
    else:checks.append({'name':'Baseline text-fit assertions in renderer','pass':True,'limitation':'Technical template only; no claim of production editorial quality.'})
    result={'id':content_id,'variant':variant,'technical_qc':'PASS','checked_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'video_probe':probe,'audio':audio,'human_editorial_status':'REVISE_PENDING_OWNER_REVIEW','unresolved':(['[blocked] Direct human listening for volume, timbre and cue comfort is not performed.'] if kind=='reel' else [])+['Owner disposition remains REVISE. Separate explicit publication approval required.']}
    (folder/'qc-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def make_manifest(folder,spec,content_id,kind,variant,env,commands,qc_result):
    source_paths=[ROOT/'render.py',ROOT/'requirements.txt',ROOT/'quality/grey_probability.py',ROOT/'quality/squirrel_cards.py',ROOT/'quality/build.py',ROOT/'quality/GV-003.json',ROOT/'quality/SS-LEARN-002.json',ROOT/'typography.py',ROOT/'fonts/Lato-Regular.ttf',ROOT/'fonts/Lato-Bold.ttf',ROOT/'fonts/Lato-OFL.txt',ROOT/'tests/test_quality.py',ROOT/'tests/test_revision_r2.py']
    data={'id':content_id,'variant':variant,'account':'greyvisual2026' if kind=='reel' else 'squirrelsnow2026','candidate_revision':'r2','state':'REVISE' if variant=='candidate' else 'TECHNICAL_TEST_ONLY_NOT_FOR_PUBLICATION','public_post_approved':False,'base_git_commit':'a74308e0927961e1ed39e58ccc038efde30684f0','environment':env,'commands':commands,'spec_sha256':digest(spec),'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in source_paths},'asset_sha256':{str(p.relative_to(folder)):digest(p) for p in sorted(folder.rglob('*')) if p.is_file() and p.name not in ['build-manifest.json','SHA256SUMS.txt']},'qc_result_sha256':digest(folder/'qc-result.json'),'technical_qc':qc_result['technical_qc'],'source_rights_note':'Sources/rights are reviewed human assertions; output hashes are integrity evidence, not copyright clearance.','publish_gate':'NO_PUBLIC_ACTION_FROM_THIS_PIPELINE','metrics':{'views':None,'reach':None,'reason':'Unpublished review candidate or technical fixture, no platform data.'}}
    (folder/'build-manifest.json').write_text(json.dumps(data,indent=2)+'\n')
    (folder/'SHA256SUMS.txt').write_text(''.join(digest(p)+'  '+str(p.relative_to(folder))+'\n' for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--baseline-only',action='store_true');parser.add_argument('--candidate-only',action='store_true');args=parser.parse_args()
    if args.baseline_only and args.candidate_only:raise ValueError('Choose only one build filter')
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
    env=environment();(args.out/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
    tests=run([sys.executable,'-m','unittest','discover','-s',ROOT/'tests','-v'],args.out/'tests.log')
    normal=ROOT/'fonts/Lato-Regular.ttf';bold=ROOT/'fonts/Lato-Bold.ttf'
    jobs=[]
    if not args.candidate_only:
        for cid,kind,duration in [('GV-003','reel',18),('SS-LEARN-002','carousel',None)]:
            spec=ROOT/'specs'/(cid+'.json');out=args.out/'baseline'/cid;out.mkdir(parents=True,exist_ok=True)
            cmd=[sys.executable,ROOT/'render.py',spec,'--out',out];run(cmd,out/'build-command.log');result=qc(out,cid,kind,duration,'baseline');make_manifest(out,spec,cid,kind,'baseline',env,[list(map(str,cmd))],result);jobs.append({'id':cid,'variant':'baseline','qc':'PASS'})
    if not args.baseline_only:
        for cid,kind,module,duration in [('GV-003','reel','grey_probability.py',22),('SS-LEARN-002','carousel','squirrel_cards.py',None)]:
            spec=ROOT/'quality'/(cid+'.json');out=args.out/'candidates'/cid;out.mkdir(parents=True,exist_ok=True)
            cmd=[sys.executable,ROOT/'quality'/module,spec,'--out',out,'--font-regular',normal,'--font-bold',bold];run(cmd,out/'build-command.log')
            doc=json.loads(spec.read_text());shutil.copyfile(spec,out/'content.json');(out/'caption.txt').write_text(doc['caption']+'\n')
            if kind=='carousel':shutil.copyfile(out/(cid+'-01.png'),out/'cover.png')
            result=qc(out,cid,kind,duration,'candidate');make_manifest(out,spec,cid,kind,'candidate',env,[list(map(str,cmd))],result);jobs.append({'id':cid,'variant':'candidate','qc':'PASS'})
    (args.out/'build-summary.json').write_text(json.dumps({'state':'REVISE','candidate_revision':'r2','public_post_approved':False,'jobs':jobs,'environment':env},indent=2)+'\n');print(json.dumps(jobs,indent=2))
if __name__=='__main__':main()
