"""CPU guard tests only; no Docker image/container/HF acceptance claim."""
from contextlib import redirect_stdout
import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]/'scripts'))
import validate_space_container_runtime as runtime


class ContainerRuntimeGuardTests(unittest.TestCase):
    def test_Docker_image_omitted_entrypoint_preserves_default_CMD(self):
        value={'Id':'sha256:'+'a'*64,'Config':{'User':'appuser','Cmd':['python','launch.py'],
               'Env':['PYTHONUNBUFFERED=1']}}
        parsed=runtime.image_state(json.dumps([value]))
        self.assertIsNone(parsed['entrypoint'])
        self.assertEqual(parsed['cmd'],['python','launch.py'])
        value['Config']['Entrypoint']=['unexpected-command']
        self.assertEqual(runtime.image_state(json.dumps([value]))['entrypoint'],['unexpected-command'])
        for raw in [json.dumps(value),json.dumps([]),json.dumps([value,value]),json.dumps([{'Id':'x','Config':None}])]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):runtime.image_state(raw)

    def test_raw_container_inspection_keeps_identity_and_terminal_guards(self):
        value={'Id':'a'*64,'Image':'sha256:'+'b'*64,
               'Config':{'User':'1000:1000','Labels':{runtime.SCOPE:'owned'}},
               'HostConfig':{'NetworkMode':'none','RestartPolicy':{'Name':'no'},'PortBindings':None},
               'State':{'Running':False,'ExitCode':0}}
        parsed=runtime.container_state(json.dumps([value]))
        runtime.checked_owner(parsed,'a'*64,'sha256:'+'b'*64,'owned')
        self.assertFalse(parsed['running'])
        value['State']['Running']='false'
        with self.assertRaises(ValueError):runtime.container_state(json.dumps([value]))

    def test_image_tag_cannot_substitute_for_independent_ID(self):
        self.assertEqual(runtime.checked_image('sha256:'+'a'*64),'sha256:'+'a'*64)
        for value in ('koevd:latest','a'*64,'sha256:'+'A'*64,'sha256:'+'a'*63):
            with self.subTest(value=value),self.assertRaises(ValueError):
                runtime.checked_image(value)

    def test_remote_daemon_refused_before_private_bind_mounts(self):
        for value in ('ssh://node','tcp://127.0.0.1:2375','tcp://remote:2376',None,'unix:///tmp/sock\nother'):
            with self.subTest(value=value),self.assertRaises(ValueError):
                runtime.checked_local_endpoint(value)
        runtime.checked_local_endpoint('unix:///var/run/docker.sock')
        runtime.checked_local_endpoint('npipe:////./pipe/docker_engine')

    def test_cleanup_requires_exact_ID_image_label_and_isolation(self):
        state={'id':'a'*64,'image':'sha256:'+'b'*64,'label':'owned-token','user':'1000:1000',
               'network':'none','restart':'no','ports':{},'running':True,'exit_code':0}
        runtime.checked_owner(state,'a'*64,'sha256:'+'b'*64,'owned-token')
        for field,value in [('id','c'*64),('image','sha256:'+'d'*64),('label','unrelated'),
            ('user','0'),('network','host'),('restart','always'),('ports',{'7860/tcp':[]})]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                runtime.checked_owner(dict(state,**{field:value}),'a'*64,'sha256:'+'b'*64,'owned-token')

    def test_default_launcher_argv_does_not_publish_ports_or_run_shell(self):
        with tempfile.TemporaryDirectory() as temp:
            args=runtime.create_argv('docker','sha256:'+'a'*64,'c'*32,*[Path(temp)/n for n in ('context','tools','results','output')])
        self.assertEqual(args[-1],'sha256:'+'a'*64)
        self.assertNotIn('--entrypoint',args)
        self.assertNotIn('-p',args)
        self.assertIn('--pull=never',args)
        self.assertIn('none',args)
        self.assertEqual(sum(',readonly' in arg for arg in args),3)
        for arg in args:
            self.assertNotIn('docker.sock',arg)
            self.assertNotIn('KOEVD_BACKUP_TOKEN',arg)

    def test_prepare_only_does_not_call_Docker_copy_responses_or_claim_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);candidate=root/'candidate';candidate.mkdir()
            payload=b'public source'
            (candidate/'source.txt').write_bytes(payload)
            manifest={'format':'koevd-private-development-space-v1','storage':'ephemeral_development',
                'credentials_included':False,'actual_target_outputs_included':False,'official_rank_eligible':False,
                'files':{'source.txt':{'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}}}
            (candidate/'deployment-manifest.json').write_text(json.dumps(manifest))
            result=root/'actual-original.json';result.write_bytes(b'private input example')
            out=root/'output'
            argv=['check','--candidate',str(candidate),'--image-id','sha256:'+'a'*64,
                '--result',str(result),'--result-sha256',runtime.digest(result),'--output',str(out),'--prepare-only']
            with patch('sys.argv',argv),patch.object(runtime.subprocess,'run') as run,redirect_stdout(io.StringIO()):
                runtime.main()
            run.assert_not_called()
            receipt=json.loads((out/'receipt.json').read_text())
            self.assertEqual(receipt['status'],'prepared_only')
            self.assertFalse(receipt['container_verified'])
            self.assertFalse(receipt['raw_result_copies_created'])
            self.assertFalse((out/'disposable').exists())
            out2=root/'wrong-hash-output'
            argv[argv.index(str(out))]=str(out2)
            argv[argv.index(runtime.digest(result))]='f'*64
            with patch('sys.argv',argv),self.assertRaises(ValueError):
                runtime.main()
            self.assertFalse(out2.exists())


if __name__=='__main__':
    unittest.main()
