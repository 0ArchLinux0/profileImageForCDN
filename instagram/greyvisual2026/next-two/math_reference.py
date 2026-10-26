#!/usr/bin/env python3
"""Pure-math ground truth for new Grey Reel concepts; no network or publishing."""
from __future__ import annotations
from math import prod

def birthday_probability(n: int, days: int = 365) -> float:
    if not isinstance(n,int) or not isinstance(days,int) or n<0 or days<1:
        raise ValueError("invalid inputs")
    if n>days:
        return 1.0
    return 1.0-prod((days-k)/days for k in range(n))

def birthday_pair_count(n:int)->int:
    if not isinstance(n,int) or n<0:
        raise ValueError("invalid people count")
    return n*(n-1)//2

def rectangle_perimeter(w:float,h:float)->float:
    if w<=0 or h<=0:raise ValueError("positive dimensions required")
    return 2*(w+h)

def fixed_perimeter_area(w:float,perimeter:float=100)->float:
    if perimeter<=0 or not 0<w<perimeter/2:raise ValueError("invalid shape")
    return w*(perimeter/2-w)

if __name__=="__main__":
    import json
    print(json.dumps({"birthday":{"n10_pct":100*birthday_probability(10),"n20_pct":100*birthday_probability(20),"n22_pct":100*birthday_probability(22),"n23_pct":100*birthday_probability(23),"pairs23":birthday_pair_count(23)},"geometry":{"rect10x40_area":fixed_perimeter_area(10),"square25x25_area":fixed_perimeter_area(25)}},indent=2))
