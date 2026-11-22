#!/usr/bin/env python3
"""Concurrent producer/auditor launch. For real model use --backend ollama after installing Ollama and pulling a local model."""
import argparse,os,subprocess,pathlib,json,sys, shutil
root=pathlib.Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--backend',choices=['policy','ollama'],default='ollama');ap.add_argument('--model',default='qwen3.5:4b');ap.add_argument('--endpoint',default='http://localhost:11434/api/chat');ap.add_argument('--allow-same-uid',action='store_true');args=ap.parse_args()
users={'producer':'vvexp01p','auditor':'vvexp01a'}
if os.geteuid()!=0 and not args.allow_same_uid:
 sys.exit('Two-user isolation requires root privileges and prepared vvexp01p/vvexp01a accounts. Without them, use --allow-same-uid with weaker isolation.')
processes=[]
for role,username in users.items():
 cmd=[sys.executable,str(root/'src/worker.py'),'--role',role,'--backend',args.backend,'--model',args.model,'--endpoint',args.endpoint,'--private-dir',str(root/'run'/('private_'+role)),'--public-key',str(root/'keys/exp01_public.pem')]
 if os.geteuid()==0:cmd=['runuser','-u',username,'--']+cmd
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 processes.append((role,p))
results=[]
for role,p in processes:
 stdout,stderr=p.communicate(timeout=240)
 results.append({'role':role,'exit_code':p.returncode,'public_stdout':stdout.strip()[:1000],'stderr_first_line':stderr.splitlines()[0][:250] if stderr else ''})
if all(x['exit_code']==0 for x in results):
 check=subprocess.run([sys.executable,str(root/'src/feedback_router.py')],capture_output=True,text=True)
 if check.returncode!=0:results.append({'error':'feedback router failed','stderr':check.stderr[:1000]})
print(json.dumps({'backend':args.backend,'mode':'separate_subprocesses','roles':results,'real_ai':args.backend=='ollama' and all(x['exit_code']==0 for x in results)},indent=2))
if any(x.get('exit_code',0)!=0 or 'error' in x for x in results):sys.exit(2)
