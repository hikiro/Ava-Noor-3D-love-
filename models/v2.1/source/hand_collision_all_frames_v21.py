#!/usr/bin/env python3
"""Test all encoded frames for opposite-hand triangle intersections only.
Does not test self-contact, interlocking fingers, pressure, or full-body collisions.
"""
import json, pathlib
from build_v21 import Actor
from contact_sweep_v20 import measures
from build_v19 import QA

def main():
    A,N=Actor('ava'),Actor('noor')
    rec=[]
    for i in range(125):
        d=measures(A,N,i/24,z=.039)
        rec.append({'frame':i,'hits':d['triangle_intersections'],
                    'nearest_vertices_m':d['nearest_vertices_m']})
    result={'frames_expected':125,'frames_checked':len(rec),
            'zero_opposing_triangle_intersections':all(r['hits']==0 for r in rec),
            'collision_records':rec,
            'note':'Opposing hand surfaces only; does not cover self-intersections, limbs or garments; proximity does not establish natural grasp.'}
    out=QA/'ALL_125_HAND_COLLISION_v21.json'
    out.write_text(json.dumps(result,indent=2))
    print(f"opposing-hand collision: {len(rec)} frames, no intersections={result['zero_opposing_triangle_intersections']}")
    if not result['zero_opposing_triangle_intersections']:raise SystemExit(1)
if __name__=='__main__':main()
