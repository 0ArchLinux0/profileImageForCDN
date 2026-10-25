import copy,json,sys,unittest,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from render import validate as validate_baseline,lines_fit,font
from quality.grey_probability import probability,Drawing,validate as validate_grey
from quality.squirrel_cards import Card,LayoutError

class TestQuality(unittest.TestCase):
    def setUp(self):
        self.regular=ROOT/'fonts/Lato-Regular.ttf'
        self.bold=ROOT/'fonts/Lato-Bold.ttf'
    def test_exact_probability_and_monotonic_diminishing_returns(self):
        self.assertAlmostEqual(probability(1),.01,14)
        self.assertAlmostEqual(probability(100),.6339676587267709,14)
        self.assertAlmostEqual((1-probability(100)),.3660323412732291,14)
        vals=[probability(n) for n in range(101)]
        self.assertTrue(all(a<b for a,b in zip(vals,vals[1:])))
        diffs=[b-a for a,b in zip(vals,vals[1:])]
        self.assertTrue(all(a>b for a,b in zip(diffs,diffs[1:])))
    def test_publish_gate_rejects_true_and_string(self):
        doc=json.loads((ROOT/'specs/GV-003.json').read_text())
        for value in [True,'true',1]:
            doc['public_post_approved']=value
            with self.assertRaises(ValueError):validate_baseline(doc)
    def test_long_unbroken_text_rejected(self):
        d=ImageDraw.Draw(Image.new('RGB',(1080,1350)))
        with self.assertRaises(ValueError):lines_fit(d,'X'*100,font(48),800)
    def test_grey_keyframe_layout_and_nonstatic_visual(self):
        art=Drawing(self.regular,self.bold)
        frames=[art.frame(t) for t in [0,1,3,5,6,7,9.5,10,12,13,16,17,19,21.9]]
        art.cover()
        self.assertTrue(all(im.size==(1080,1920) for im in frames))
        hashes=[hashlib.sha256(im.tobytes()).hexdigest() for im in frames]
        self.assertGreaterEqual(len(set(hashes)),9)
        self.assertTrue(all(row['font_size']>=24 for row in art.checked.values()))
    def test_area_boundary_matches_model_not_simulation(self):
        art=Drawing(self.regular,self.bold)
        for t in [3,5,10,12]:
            n=min(68,int((t-2.5)/3.5*69)) if t<6 else min(100,69+int((t-9.5)/3*31))
            im=art.frame(t)
            expected=120+840*probability(n)
            px=im.load()
            # Moving white divider follows the complement-derived area boundary;
            # ignore the separately drawn fixed50% reference guide.
            white_x=[x for x in range(120,961) if px[x,1000]==(244,240,231) and abs(x-540)>2]
            self.assertTrue(white_x)
            self.assertLessEqual(abs(sum(white_x)/len(white_x)-expected),2)
    def test_grey_spec_arithmetic_and_approval_rejected(self):
        doc=json.loads((ROOT/'quality/GV-003.json').read_text())
        validate_grey(doc);doc['probability']['exact_value']=1
        with self.assertRaises(ValueError):validate_grey(doc)
    def test_all_squirrel_cards_fit_without_overlapping_text(self):
        doc=json.loads((ROOT/'quality/SS-LEARN-002.json').read_text())
        for card in doc['cards']:
            art=Card(doc,card,self.regular,self.bold)
            im=art.render()
            self.assertEqual(im.size,(1080,1350))
            self.assertEqual(art.qc['status'],'pass')
            self.assertFalse(art.qc['errors'])
    def test_squirrel_rejects_unrenderable_text(self):
        doc=json.loads((ROOT/'quality/SS-LEARN-002.json').read_text());bad=copy.deepcopy(doc['cards'][0]);bad['title']='X'*500
        next(t for t in bad['texts'] if t['id']=='title')['text']=bad['title']
        with self.assertRaises(LayoutError):Card(doc,bad,self.regular,self.bold).render()

if __name__=='__main__':unittest.main()
