import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from typography import brand_font,zero_diagnostic
from quality.grey_probability import probability,cue_events,DURATION,Drawing
from quality.squirrel_cards import Card,LayoutError

class RevisionR2(unittest.TestCase):
    def test_ordinary_zero_in_both_shared_weights(self):
        for bold in [False,True]:
            report=zero_diagnostic(brand_font(120,bold))
            self.assertTrue(report['ordinary_zero_center_clear'])
            self.assertEqual(report['center_ink_fraction'],0)
    def test_required_arrow_and_math_glyphs_exist(self):
        for bold in [False,True]:
            f=brand_font(100,bold);missing=f.getmask(chr(0x10FFFF))
            for ch in '0123456789→−÷×¼%':
                m=f.getmask(ch)
                self.assertFalse(m.size==missing.size and bytes(m)==bytes(missing),ch)
    def test_first_strict_crossing_of_half_is_69(self):
        self.assertTrue(all(probability(n)<=.5 for n in range(69)))
        self.assertGreater(probability(69),.5)
        self.assertAlmostEqual(probability(68),.49511411121293036,14)
        self.assertAlmostEqual(probability(69),.500162970100801,14)
    def test_milestone_is_held_and_duration_in_requested_range(self):
        self.assertTrue(20<=DURATION<=24)
        art=Drawing(ROOT/'fonts/Lato-Regular.ttf',ROOT/'fonts/Lato-Bold.ttf')
        self.assertEqual(art.frame(6.2).tobytes(),art.frame(9.2).tobytes())
        records=list(art.checked.values())
        self.assertTrue(any('50.016%' in r['text'] for r in records))
        self.assertTrue(any('not a win count' in r['text'] for r in records))
        self.assertTrue(any('Independent' in r['text'] for r in records))
    def test_cue_times_match_visual_beats_and_have_headroom(self):
        events=cue_events()
        self.assertEqual([e['time'] for e in events],[6.,12.5,16.5])
        self.assertTrue(all(0<e['amplitude']<.1 for e in events))
        self.assertTrue(all(0<e['duration']<.25 for e in events))
        self.assertTrue(all(e['time']+e['duration']<DURATION for e in events))
    def test_percentage_change_example_and_reverse_checks(self):
        self.assertEqual(100-80,20)
        self.assertAlmostEqual(20/100,.2)
        self.assertAlmostEqual((100-80)/80,.25)
        self.assertEqual(80*1.25,100)
        self.assertEqual(80*1.2,96)
        self.assertAlmostEqual((60-50)/50,.2)
        self.assertAlmostEqual((80-100)/100,-.2)
    def test_caption_citations_and_copy_reduction(self):
        doc=json.loads((ROOT/'quality/SS-LEARN-002.json').read_text())
        actual=sum(len(t['text'].strip().split()) for card in doc['cards'] for t in card['texts'])
        metrics=doc['visible_copy_metrics']
        self.assertEqual(actual,metrics['after_total'])
        self.assertTrue(.7<=actual/metrics['before_total']<=.8)
        self.assertLessEqual(len(doc['caption']),2200)
        self.assertIn('10.1111/j.1467-9280.2006.01693.x',doc['caption'])
        self.assertIn('10.1037/0278-7393.34.4.918',doc['caption'])
        self.assertIn('ILLUSTRATIVE',doc['caption'])
        self.assertTrue(all(any('ILLUSTRATIVE' in t['text'] for t in card['texts']) for card in doc['cards']))
    def test_caption_and_card_do_not_claim_user_experience(self):
        doc=json.loads((ROOT/'quality/SS-LEARN-002.json').read_text())
        self.assertIn('not',doc['caption'])
        self.assertIn("owner's life",doc['caption'])
        self.assertFalse(doc['public_post_approved'])
        self.assertEqual(len(doc['cards']),5)

if __name__=='__main__':unittest.main()
