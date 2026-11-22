#!/usr/bin/env python3
"""Tests isolated processes and public release gate without opening private agent reports."""
from pathlib import Path
import subprocess,json,os,sys,socket,hashlib
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization,hashes
R=Path(__file__).resolve().parents[1]
results=[]
def chk(name,condition):results.append({'name':name,'pass':bool(condition)})
def as_user(username,command):
 return subprocess.run(['runuser','-u',username,'--',*command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
producer=R/'run/private_producer/memory.json';auditor=R/'run/private_auditor/memory.json'
chk('producer cannot read auditor private memory',as_user('vvexp01p',['test','-r',str(auditor)]).returncode!=0)
chk('auditor cannot read producer private memory',as_user('vvexp01a',['test','-r',str(producer)]).returncode!=0)
chk('producer can read own private memory',as_user('vvexp01p',['test','-r',str(producer)]).returncode==0)
chk('auditor can read own private memory',as_user('vvexp01a',['test','-r',str(auditor)]).returncode==0)
chk('producer cannot modify evidence',as_user('vvexp01p',['test','-w',str(R/'evidence/v21_evidence.json')]).returncode!=0)
chk('auditor cannot modify evidence',as_user('vvexp01a',['test','-w',str(R/'evidence/v21_evidence.json')]).returncode!=0)
chk('producer cannot list auditor outputs',as_user('vvexp01p',['test','-r',str(R/'outputs/auditor/sealed_review.json')]).returncode!=0)
chk('auditor cannot list producer outputs',as_user('vvexp01a',['test','-r',str(R/'outputs/producer/sealed_review.json')]).returncode!=0)
chk('producer cannot read auditor role instructions',as_user('vvexp01p',['test','-r',str(R/'config/AUDITOR_SYSTEM.md')]).returncode!=0)
chk('auditor cannot read producer role instructions',as_user('vvexp01a',['test','-r',str(R/'config/PRODUCER_SYSTEM.md')]).returncode!=0)
p=json.loads((R/'outputs/producer/public_status.json').read_text());a=json.loads((R/'outputs/auditor/public_status.json').read_text());f=json.loads((R/'outputs/feedback/public_result.json').read_text())
chk('separate role public status files',p['role']=='producer' and a['role']=='auditor')
chk('opposed role recommendations detected',f['disagreement_detected'])
chk('auditor veto blocks public release',f['public_release_status']=='BLOCKED')
chk('feedback does not claim private reads',f['private_reasoning_accessed_by_router'] is False)
chk('no false AI instance claim',f['real_llm_instances_executed']==0 and f['simulated_policy_execution'])
chk('repair work routed',len(f['routed_tasks'])>=2)
chk('sealed report contains ciphertext not raw fields',all('private_assessment' not in (R/f'outputs/{x}/sealed_review.json').read_text() for x in ('producer','auditor')))
chk('private unlock key outside distribution directory',not (R/'keys/exp01_private.pem').exists())
# Test crypto using a disposable synthetic message. Real private reports remain sealed/unopened.
key=rsa.generate_private_key(public_exponent=65537,key_size=2048);aes=AESGCM.generate_key(bit_length=256);iv=os.urandom(12);plaintext=b'TEST_ONLY_NOT_ANY_AGENT_REPORT';cipher=AESGCM(aes).encrypt(iv,plaintext,b'test');wrap=key.public_key().encrypt(aes,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None));rec=key.decrypt(wrap,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None));chk('cryptographic roundtrip with synthetic sample',AESGCM(rec).decrypt(iv,cipher,b'test')==plaintext)
s=socket.socket();s.settimeout(.25)
try:s.connect(('127.0.0.1',11434));available=True
except OSError:available=False
finally:s.close()
chk('model runtime availability honestly detected', not available)
report={'test_count':len(results),'passed':sum(x['pass'] for x in results),'failed':sum(not x['pass'] for x in results),'tests':results,'runtime':{'ollama_local_online':available,'genuine_llm_sessions_executed':0},'private_reports_opened':False}
(R/'outputs/feedback/infrastructure_tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(int(report['failed']>0))
