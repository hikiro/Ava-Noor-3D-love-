#!/usr/bin/env python3
"""Runs as dedicated OS user; no access to opposite agent's private state."""
import argparse,json,os,sys,urllib.request,urllib.parse,hashlib,pathlib,datetime,base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes

ROOT=pathlib.Path(__file__).resolve().parents[1]
def dump(p,obj):
 p=pathlib.Path(p);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def iso():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def seal(public_key_path,secret_obj):
 key=serialization.load_pem_public_key(pathlib.Path(public_key_path).read_bytes())
 aes=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12)
 body=json.dumps(secret_obj,sort_keys=True).encode();blob=AESGCM(aes).encrypt(nonce,body,b'VV_EXP01_ROLE_REVIEW')
 wrapped=key.encrypt(aes,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
 return {'cipher':'AES-256-GCM with RSA-OAEP-SHA256 key wrap','nonce':nonce.hex(),'wrapped_key':wrapped.hex(),'ciphertext':blob.hex(),'sha256_cleartext':hashlib.sha256(body).hexdigest()}

def policy(role,evidence):
 # PROTOCOL SMOKE TEST ONLY. This is NOT a language model and must never be counted as AI reasoning.
 stats=evidence['verified_metrics']
 if role=='producer':
  passed=stats['structural_checks']==stats['structural_passed'] and stats['hand_intersection_count']==0
  return {'verdict':'PROPOSE_INTERNAL_RELEASE_CANDIDATE' if passed else 'BLOCK', 'confidence':0.73 if passed else 0.95,
  'public_flags':['TECH_GATE_PASSED','ENGINE_UNVERIFIED'] if passed else ['TECH_GATE_FAILED'],
  'private_assessment':'Rule-based production advocacy: structural and collision gates are green, so propose a limited internal candidate for creative review, not public release. Remaining issues may block subsequent publication.',
  'next_task':'Request Art Director visual signoff and Godot import test before public release.'}
 return {'verdict':'BLOCK_PUBLIC_RELEASE' if (not stats['native_godot_playback_verified'] or evidence['documented_open_visual_issues']) else 'CONDITIONAL_PASS',
   'confidence':0.96,'public_flags':['CONTACT_VISUAL_UNAPPROVED','GODOT_NOT_TESTED','FACIAL_ART_DEFECT'],
   'private_assessment':f"Rule-based adversarial check: 0 mesh intersections does not establish grip fidelity; median 75-100 frame nearest hand points are {stats['nearest_hand_vertices_median_mm']} mm apart. Lip-layer artifact is documented and engine playback is unverified. Block public release pending visual review.",
   'next_task':'Have Art Director and Animator develop true grasp staging; Technical Director must obtain native Godot evidence.'}

def ollama(role,evidence, memory,model,endpoint):
 u=urllib.parse.urlparse(endpoint)
 if u.hostname not in ('localhost','127.0.0.1','::1'):
  raise RuntimeError('Only a locally hosted Ollama endpoint is permitted in this zero-cost experiment.')
 system=(ROOT/'config'/('PRODUCER_SYSTEM.md' if role=='producer' else 'AUDITOR_SYSTEM.md')).read_text()
 prompt={'evidence':evidence,'private_agent_memory':memory,'task':'Review Villa Verse v2.1 readiness independently. Respond in valid JSON matching system contract.'}
 user_message={'role':'user','content':json.dumps(prompt)}
 # The Auditor receives the same evidence JSON plus real image panels for vision-capable local Ollama models.
 # This does not make the model independent unless an actual Ollama runtime responds.
 image_names=['SIX_POSE_V21_INSPECTION.png','CONTACT_V21_DETAIL.png','MOUTH_BEFORE_AFTER_v21.png'] if role=='auditor' else ['SIX_POSE_V21_INSPECTION.png']
 user_message['images']=[base64.b64encode((ROOT/'evidence/visuals'/name).read_bytes()).decode('ascii') for name in image_names]
 body=json.dumps({'model':model,'stream':False,'format':'json','messages':[{'role':'system','content':system},user_message]}).encode()
 req=urllib.request.Request(endpoint,data=body,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:reply=json.load(r)
 parsed=json.loads(reply['message']['content'])
 required=['verdict','confidence','public_flags','private_assessment','next_task']
 if not all(k in parsed for k in required):raise ValueError('Incomplete model response')
 return parsed

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--role',choices=['producer','auditor'],required=True);ap.add_argument('--backend',choices=['policy','ollama'],default='policy');ap.add_argument('--model',default='qwen3.5:4b');ap.add_argument('--private-dir',required=True);ap.add_argument('--public-key',required=True);ap.add_argument('--endpoint',default='http://localhost:11434/api/chat'); args=ap.parse_args()
 private=pathlib.Path(args.private_dir);private.mkdir(parents=True,exist_ok=True);os.chmod(private,0o700)
 evidence=json.loads((ROOT/'evidence/v21_evidence.json').read_text())
 memfile=private/'memory.json';memory=json.loads(memfile.read_text()) if memfile.exists() else {'role':args.role,'experiences':[],'version':1}
 result=policy(args.role,evidence) if args.backend=='policy' else ollama(args.role,evidence,memory,args.model,args.endpoint)
 result['role']=args.role;result['time_utc']=iso();result['backend']=args.backend
 memory['experiences'].append({'task':'VV-v2.1-readiness','verdict':result['verdict'],'public_flags':result['public_flags'],'time_utc':result['time_utc']})
 dump(memfile,memory);os.chmod(memfile,0o600)
 sealed=seal(args.public_key,{'result':result,'memory':memory,'role_system_prompt':(ROOT/'config'/('PRODUCER_SYSTEM.md' if args.role=='producer' else 'AUDITOR_SYSTEM.md')).read_text()})
 out=ROOT/'outputs'/args.role
 dump(out/'sealed_review.json',sealed)
 public={'role':args.role,'verdict':result['verdict'],'confidence':result['confidence'],'public_flags':result['public_flags'],'backend':args.backend,'is_real_language_model':args.backend=='ollama','private_review':'encrypted/not_opened','time_utc':result['time_utc'],'sealed_sha256':hashlib.sha256((out/'sealed_review.json').read_bytes()).hexdigest()}
 dump(out/'public_status.json',public)
 # Leave no private details in stdout; only public result.
 print(json.dumps({'role':args.role,'verdict':public['verdict'],'backend':args.backend}))
if __name__=='__main__':main()
