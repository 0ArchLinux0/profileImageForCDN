#!/usr/bin/env python3
"""Content truth regression, independent of rasterizer/encoder."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from math_reference import birthday_probability,birthday_pair_count,fixed_perimeter_area,rectangle_perimeter
class NextTwoTruthTests(unittest.TestCase):
    def test_first_group_strictly_above_fifty_is_23(self):
        self.assertTrue(all(birthday_probability(n)<=.5 for n in range(23)))
        self.assertGreater(birthday_probability(23),.5)
    def test_birthday_probability_points(self):
        self.assertAlmostEqual(birthday_probability(10),.11694817771107767,places=12)
        self.assertAlmostEqual(birthday_probability(22),.4756953076625502,places=12)
        self.assertAlmostEqual(birthday_probability(23),.5072972343239857,places=12)
        self.assertEqual(birthday_pair_count(23),253)
    def test_empty_single_and_impossible_days(self):
        self.assertEqual(birthday_probability(0),0)
        self.assertEqual(birthday_probability(1),0)
        self.assertEqual(birthday_probability(366),1)
    def test_geometric_examples(self):
        self.assertEqual(rectangle_perimeter(10,40),100)
        self.assertEqual(rectangle_perimeter(25,25),100)
        self.assertEqual(fixed_perimeter_area(10),400)
        self.assertEqual(fixed_perimeter_area(25),625)
        self.assertEqual(fixed_perimeter_area(25)-fixed_perimeter_area(10),225)
    def test_fixed_perimeter_morph(self):
        for i in range(61):
            w=10+15*i/60
            h=50-w
            self.assertAlmostEqual(rectangle_perimeter(w,h),100)
            self.assertAlmostEqual(fixed_perimeter_area(w),w*h)
            self.assertLessEqual(w*h,625)
    def test_bad_inputs(self):
        for n in [-1,1.5]:
            with self.assertRaises(ValueError):birthday_probability(n)
        with self.assertRaises(ValueError):fixed_perimeter_area(50)
if __name__=="__main__":unittest.main()
