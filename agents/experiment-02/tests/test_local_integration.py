"""Tests the real transport protocol with MOCK RESPONSES. Not a language-model benchmark."""
import base64, copy, json, os, shutil, subprocess, sys, tempfile, threading, unittest
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

TEMPLATE=Path(__file__).resolve().parents[1]

class MockHandler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.0'
    requests_log=[]
    malformed=False
    def log_message(self,*args): pass
    def do_GET(self):
        if self.path != '/api/tags':
            self.send_error(404);return
        self.send_json({'models':[{'name':'qwen3.5:4b'},{'name':'qwen3-vl:4b'}]})
    def send_json(self, data):
        b=json.dumps(data).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_POST(self):
        raw=self.rfile.read(int(self.headers['Content-Length']))
        data=json.loads(raw)
        sys_text=data['messages'][0]['content']
        role='producer' if 'PRODUCER-01' in sys_text else 'auditor'
        task=json.loads(data['messages'][1]['content'])
        memory=task['role_private_memory']
        type(self).requests_log.append({'role':role,'model':data['model'],'memory_count':len(memory),'vision_images':len(data['messages'][1]['images']),'own_role':task['experiment'],'private_memory':memory})
        if type(self).malformed:
            answer={'verdict':'INVALID','private_assessment':'secret SHOULD NEVER LEAK','confidence':7,'next_task':'foo','public_flags':[]}
        else:
            answer={
              'verdict': 'PROPOSE_INTERNAL_RELEASE_CANDIDATE' if role=='producer' else 'BLOCK_PUBLIC_RELEASE',
              'confidence':0.72 if role=='producer' else 0.93,
              'public_flags':(['TECH_GATE_PASSED'] if role=='producer' else ['CONTACT_UNAPPROVED','GODOT_UNVERIFIED'])+(['PRIOR_CASE_REMEMBERED'] if memory else []),
              'private_assessment':f'PRIVATE {role} simulated assessment, not language-model reasoning',
              'next_task':'Validate evidence and redesign unresolved interaction.',
              'learning_proposals':[{'rule':'Never infer believable handholding only from zero triangle intersections.','supporting_evidence':'v21_evidence.json documented open visual issues','status':'PENDING_VALIDATION'}]
            }
        self.send_json({'model':data['model'],'message':{'role':'assistant','content':json.dumps(answer)},'done':True,'eval_count':41,'prompt_eval_count':85,'total_duration':750000})

class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),MockHandler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.endpoint=f'http://127.0.0.1:{cls.server.server_port}/api/chat'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)/'experiment'
        self.base.mkdir()
        for folder in ('src','config','evidence'):
            shutil.copytree(TEMPLATE/folder,self.base/folder)
        (self.base/'keys').mkdir()
        sys.path.insert(0,str(self.base/'src'))
        import importlib
        import protocol
        importlib.reload(protocol)
        protocol.make_owner_keys(self.base/'keys/owner_public.pem',Path(self.tmp.name)/'OWNER_KEY_DO_NOT_SHIP.pem')
        self.private_key=Path(self.tmp.name)/'OWNER_KEY_DO_NOT_SHIP.pem'
        MockHandler.requests_log=[];MockHandler.malformed=False
    def launch(self,backend='mock',run_id='TEST001'):
        cmd=[sys.executable,str(self.base/'src/orchestrator.py'),'--backend',backend,'--endpoint',self.endpoint,'--run-id',run_id]
        return subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    def test_01_two_processes_have_different_system_prompts_and_images(self):
        r=self.launch()
        self.assertEqual(r.returncode,0,r.stderr+r.stdout)
        self.assertEqual([x['role'] for x in MockHandler.requests_log],['producer','auditor'])
        self.assertEqual([x['model'] for x in MockHandler.requests_log],['qwen3.5:4b','qwen3-vl:4b'])
        self.assertEqual([x['vision_images'] for x in MockHandler.requests_log],[1,3])
    def test_02_private_memory_is_role_scoped_and_persists(self):
        self.assertEqual(self.launch(run_id='T1').returncode,0)
        self.assertEqual(self.launch(run_id='T2').returncode,0)
        self.assertEqual([x['memory_count'] for x in MockHandler.requests_log],[0,0,1,1])
        producer=json.loads((self.base/'private_state/producer/memory.json').read_text())
        auditor=json.loads((self.base/'private_state/auditor/memory.json').read_text())
        self.assertEqual(producer['role'],'producer')
        self.assertEqual(auditor['role'],'auditor')
        self.assertEqual(producer['version'],3)
        self.assertEqual(auditor['version'],3)
        self.assertNotEqual(producer['events'][0]['review_verdict'],auditor['events'][0]['review_verdict'])
        self.assertEqual(len(producer['events']),2)
    def test_03_public_router_never_reads_or_returns_private_assessment(self):
        self.assertEqual(self.launch().returncode,0)
        public=(self.base/'run/TEST001/public_result.json').read_text()
        for who in ['producer','auditor']:
            self.assertNotIn('private_assessment',(self.base/f'run/TEST001/{who}/public_status.json').read_text())
        self.assertNotIn('PRIVATE',public)
        self.assertEqual(json.loads(public)['public_release'],'BLOCKED')
        self.assertTrue(json.loads(public)['disagreement'])
        self.assertEqual(json.loads(public)['actual_model_api_calls'],0)
    def test_04_seal_can_only_open_with_owner_private_key(self):
        self.assertEqual(self.launch().returncode,0)
        import protocol
        sealed=json.loads((self.base/'run/TEST001/auditor/sealed_review.json').read_text())
        private=protocol.open_report(self.private_key,sealed)
        self.assertEqual(private['role'],'auditor')
        self.assertIn('PRIVATE auditor',private['review']['private_assessment'])
        self.assertNotIn('PRIVATE auditor',json.dumps(sealed))
        self.assertTrue(sealed['ciphertext'])
    def test_05_modified_evidence_refuses_execution(self):
        p=self.base/'evidence/v21_evidence.json'
        p.write_text(p.read_text()+' ')
        r=self.launch()
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(MockHandler.requests_log)
    def test_06_malformed_response_fails_closed_without_leak(self):
        MockHandler.malformed=True
        r=self.launch()
        self.assertNotEqual(r.returncode,0)
        public=json.loads((self.base/'run/TEST001/producer/public_status.json').read_text())
        self.assertEqual(public['status'],'ERROR')
        self.assertNotIn('SHOULD NEVER LEAK',r.stdout+r.stderr+json.dumps(public))
        self.assertFalse((self.base/'run/TEST001/public_result.json').exists())
    def test_07_do_not_overwrite_run_or_autoapprove(self):
        self.assertEqual(self.launch().returncode,0)
        r=self.launch()
        self.assertNotEqual(r.returncode,0)
        report=json.loads((self.base/'run/TEST001/public_result.json').read_text())
        self.assertFalse(report['native_godot_verified'])
        self.assertEqual(report['public_release'],'BLOCKED')
    def test_08_model_endpoint_is_local_only(self):
        from urllib.parse import urlparse
        p=self.base/'src/agent_worker.py'
        self.assertIn('127.0.0.1',p.read_text())
        self.assertIn('localhost',p.read_text())
    def test_09_sealed_reports_have_unique_iv_and_ciphertext(self):
        self.assertEqual(self.launch().returncode,0)
        a=json.loads((self.base/'run/TEST001/auditor/sealed_review.json').read_text())
        b=json.loads((self.base/'run/TEST001/producer/sealed_review.json').read_text())
        self.assertNotEqual(a['nonce'],b['nonce'])
        self.assertNotEqual(a['wrapped_key'],b['wrapped_key'])
    def test_10_learning_proposals_remain_pending(self):
        self.assertEqual(self.launch().returncode,0)
        auditor=json.loads((self.base/'private_state/auditor/memory.json').read_text())
        rules=auditor['events'][0]['proposed_rules']
        self.assertTrue(rules)
        self.assertTrue(all(x['status']=='PENDING_VALIDATION' for x in rules))
    def test_11_no_worker_can_claim_verified_real_inference_in_mock_mode(self):
        self.assertEqual(self.launch().returncode,0)
        for who in ('producer','auditor'):
            status=json.loads((self.base/f'run/TEST001/{who}/public_status.json').read_text())
            self.assertFalse(status['model_inference_verified'])
    def test_12_no_owner_private_key_in_project(self):
        self.assertFalse(list(self.base.rglob('*PRIVATE_KEY*.pem')))
        self.assertTrue(self.private_key.is_file())
    def test_13_local_key_bootstrap_is_owner_held_and_idempotent(self):
        env=os.environ.copy()
        env['HOME']=str(Path(self.tmp.name)/'owner_home')
        Path(env['HOME']).mkdir(exist_ok=True)
        source=self.base/'src/setup_owner_keys.py'
        old_public=(self.base/'keys/owner_public.pem').read_bytes()
        for i in range(2):
            p=subprocess.run([sys.executable,str(source)],capture_output=True,text=True,env=env,timeout=15)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        new_public=(self.base/'keys/owner_public.pem').read_bytes()
        self.assertNotEqual(old_public,new_public)
        self.assertTrue((Path(env['HOME'])/'VillaVerse_OwnerKeys/exp02_private.pem').is_file())
        self.assertFalse((self.base/'keys/exp02_private.pem').exists())
        self.assertTrue((self.base/'keys/LOCAL_OWNER_KEY_INITIALIZED.json').exists())

if __name__=='__main__':
    unittest.main(verbosity=2)
