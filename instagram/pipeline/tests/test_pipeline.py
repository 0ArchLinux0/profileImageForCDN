import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render import validate, render, file_hash
from PIL import Image

class TestPipeline(unittest.TestCase):
    def test_reject_unapproved_or_missing_rights(self):
        spec = Path(__file__).resolve().parents[1]/'specs/GV-003.json'
        doc = json.loads(spec.read_text())
        validate(doc)
        doc['rights'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'Rights'):
            validate(doc)

    def test_carousel_dimensions_and_manifest(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            report = render(root/'specs/SS-LEARN-002.json', d)
            self.assertFalse(report['public_post_approved'])
            self.assertEqual(len(report['asset_sha256']), 5)
            for name, digest in report['asset_sha256'].items():
                path = Path(d)/name
                with Image.open(path) as im:
                    self.assertEqual(im.size, (1080, 1350))
                self.assertEqual(file_hash(path), digest)

if __name__ == '__main__':
    unittest.main()
