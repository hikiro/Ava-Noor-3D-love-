#!/usr/bin/env python3
"""Villa Verse producer gate. This tracks review evidence; it cannot certify reviewers were independent."""
import argparse, json, sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
BOARD=BASE/'plans/V22_TASK_BOARD.json'
REV=BASE/'reviews/v22_review_status.json'

def load(p): return json.loads(p.read_text())

def status():
 b=load(BOARD); r=load(REV); print('Release',r['release']);
 for t in b['work_orders']:
  print(f"{t['id']:7} {t['owner']:26} {t['status']:22} | {t['task'][:55]}")
 print('\nRELEASE GATES:')
 for k in r['required_gates']:
  v=r['gates'][k]; print(f"  {k:24} {v['verdict']:9} {v['execution_mode']}")


def evaluate():
 r=load(REV); blocked=[]
 for k in r['required_gates']:
  g=r['gates'][k]
  if g['verdict']!='PASS': blocked.append(f'{k}: {g["verdict"]}'); continue
  if not g.get('evidence'): blocked.append(f'{k}: missing evidence'); continue
  if g.get('execution_mode') not in ('actual_subagent','human','actual_native_tool'): blocked.append(f'{k}: review is not independently executed')
  for item in g['evidence']:
   p=BASE/item
   if not p.exists(): blocked.append(f'{k}: evidence file missing: {item}')
 if blocked:
  print('HOLD — not approved for final distribution')
  for x in blocked: print(' -',x)
  return 2
 print('ALL GATES DOCUMENTED PASS (verify reviewer provenance manually before release)')
 return 0

p=argparse.ArgumentParser();p.add_argument('action',choices=['status','evaluate']);a=p.parse_args()
if a.action=='status': status()
else: sys.exit(evaluate())
