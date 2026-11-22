import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
script=ROOT/'scripts/producer.py'
p=subprocess.run([sys.executable,str(script),'status'],capture_output=True,text=True)
assert p.returncode==0 and 'executive-producer' in p.stdout and 'independent-auditor' in p.stdout
p=subprocess.run([sys.executable,str(script),'evaluate'],capture_output=True,text=True)
assert p.returncode==2 and 'HOLD' in p.stdout and 'not approved' in p.stdout
files=list((ROOT/'.claude'/'agents').glob('*.md'))
assert len(files)==10, len(files)
for f in files:
 s=f.read_text(); assert s.startswith('---\nname:') and 'description:' in s and 'Required report contract' in s, str(f)
tasks=json.loads((ROOT/'plans'/'V22_TASK_BOARD.json').read_text())['work_orders']
assert len(tasks)==11
ids={t['id'] for t in tasks}
assert all(set(t['dependencies'])<=ids for t in tasks)
roles={f.stem for f in files}
assert all(t['owner'] in roles for t in tasks)
print('TESTS PASS: 10 agent configurations, 11 task cards, dependency integrity, review gate HOLD behavior')
