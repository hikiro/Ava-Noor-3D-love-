#!/usr/bin/env python3
"""Looks only at public summaries; cannot access workers' private directories."""
import json,pathlib,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
p=json.loads((root/'outputs/producer/public_status.json').read_text())
a=json.loads((root/'outputs/auditor/public_status.json').read_text())
blocked=a['verdict']=='BLOCK_PUBLIC_RELEASE' or p['verdict']=='BLOCK'
report={'experiment':'VV_EXP01','roles':['producer','auditor'],'backends':{'producer':p['backend'],'auditor':a['backend']},'real_llm_instances_executed':int(p['is_real_language_model'])+int(a['is_real_language_model']), 'producer_public_verdict':p['verdict'], 'auditor_public_verdict':a['verdict'], 'disagreement_detected':p['verdict']=='PROPOSE_INTERNAL_RELEASE_CANDIDATE' and a['verdict']=='BLOCK_PUBLIC_RELEASE','public_release_status':'BLOCKED' if blocked else 'PENDING_HUMAN_REVIEW', 'public_flags':sorted(set(p['public_flags']+a['public_flags'])), 'routed_tasks':[{'to':'Art Director + Animator','task':'Design independently inspected believable interlocking grasp, resolve hand-gap and finger anatomy','priority':'P0'},{'to':'Technical Director','task':'Obtain native Godot import and animation-playback test evidence','priority':'P0'},{'to':'Character Artist','task':'Correct detached-looking lip layers and improve facial topology','priority':'P1'}] if blocked else [], 'private_reasoning_accessed_by_router':False, 'simulated_policy_execution':p['backend']=='policy' or a['backend']=='policy'}
(root/'outputs/feedback/public_result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
