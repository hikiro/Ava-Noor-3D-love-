#!/usr/bin/env python3
"""A producer/auditor orchestrator that never reads private report or memory text.
Sequential execution is deliberate: 6 GB GPUs should not host both 4B models at once.
"""
import argparse, json, subprocess, sys, uuid
from pathlib import Path
from urllib.request import urlopen
from protocol import ROOT, load_json, dump_json, check_evidence, utc_now

def get_models(endpoint):
    with urlopen(endpoint.replace('/api/chat', '/api/tags'), timeout=12) as f:
        return {m['name'] for m in json.load(f)['models']}

def make_feedback(run_dir, statuses, backend):
    p, a = statuses['producer'], statuses['auditor']
    if any(x.get('status') == 'ERROR' for x in (p, a)):
        raise RuntimeError('A worker failed; no verdict can be released')
    evidence = load_json(ROOT / 'evidence/v21_evidence.json')
    godot = evidence['verified_metrics']['native_godot_playback_verified']
    blocking = a['verdict'] == 'BLOCK_PUBLIC_RELEASE' or p['verdict'] == 'BLOCK' or not godot
    tasks = []
    if blocking:
        tasks = [
            {'owner':'3D Animator + 3D Art Director','task':'Demonstrate credible finger wrapping with rendered close-up contact evidence','priority':'P0'},
            {'owner':'Technical Director','task':'Verify glTF import, skeleton and animation playback in native Godot','priority':'P0'},
            {'owner':'Character Artist','task':'Correct detached-looking lip layers and facial topology','priority':'P1'},
        ]
    result = {
        'experiment':'VV-EXP02', 'run_id':p['run_id'], 'timestamp':utc_now(),
        'producer_public_verdict':p['verdict'],'auditor_public_verdict':a['verdict'],
        'disagreement':p['verdict']=='PROPOSE_INTERNAL_RELEASE_CANDIDATE' and a['verdict']=='BLOCK_PUBLIC_RELEASE',
        'public_release':'BLOCKED' if blocking else 'REQUIRES_HUMAN_CREATIVE_APPROVAL',
        'native_godot_verified':godot,
        'actual_model_api_calls':int(backend == 'ollama')*2,
        'independent_model_weights':False,
        'agent_contexts_independent':True,
        'private_reports_opened':False,
        'roles_memory_versions':{role:x['memory_version'] for role,x in statuses.items()},
        'backend':backend,
        'routed_tasks':tasks,
        'security_note':'Separate processes and contexts; on a shared Windows user account this is not OS-enforced black-box isolation.'
    }
    dump_json(run_dir/'public_result.json',result)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--backend',choices=['ollama','mock'],default='ollama')
    ap.add_argument('--model-producer',default='qwen3.5:4b')
    ap.add_argument('--model-auditor',default='qwen3-vl:4b')
    ap.add_argument('--endpoint',default='http://127.0.0.1:11434/api/chat')
    ap.add_argument('--run-id',default='VV'+uuid.uuid4().hex[:12])
    ap.add_argument('--timeout',type=int,default=360)
    args=ap.parse_args()
    if check_evidence():
        print('ERROR: Evidence integrity mismatch',file=sys.stderr)
        return 2
    if args.backend=='ollama':
        try:
            available=get_models(args.endpoint)
        except Exception:
            print('ERROR: Ollama is not reachable at localhost:11434; no model calls were run.',file=sys.stderr)
            return 3
        missing={args.model_producer,args.model_auditor}-available
        if missing:
            print('ERROR: Required Ollama models not installed: '+', '.join(sorted(missing)),file=sys.stderr)
            return 4
    run_dir=ROOT/'run'/args.run_id
    if run_dir.exists():
        print('ERROR: Run already exists; refusing overwrite',file=sys.stderr)
        return 5
    run_dir.mkdir(parents=True)
    workers={}
    for role,model in [('producer',args.model_producer),('auditor',args.model_auditor)]:
        child_out=run_dir/role
        cmd=[sys.executable,str(ROOT/'src/agent_worker.py'), '--role',role,'--run-id',args.run_id,'--model',model,'--backend',args.backend,'--endpoint',args.endpoint,'--state-dir',str(ROOT/'private_state'/role),'--run-dir',str(child_out),'--public-key',str(ROOT/'keys/owner_public.pem'),'--timeout',str(args.timeout)]
        # This orchestrator never reads the child's private directory or sealed contents.
        proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=args.timeout+30)
        if proc.returncode!=0:
            print(json.dumps({'role':role,'status':'WORKER_FAILED','exit_code':proc.returncode,'public_stdout':proc.stdout.strip()[:300]}))
            return 6
        workers[role]=load_json(child_out/'public_status.json')
    result=make_feedback(run_dir,workers,args.backend)
    print(json.dumps({'run_id':args.run_id,'roles':{k:v['verdict'] for k,v in workers.items()},'public_release':result['public_release'],'backend':args.backend,'real_model_calls':result['actual_model_api_calls'],'result_path':str(run_dir/'public_result.json')},indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
