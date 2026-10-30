import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from release import build,validate_release,safe_path,digest
from deploy import publish,fetch_release
ROOT=Path(__file__).resolve().parents[1]
A='a'*40;B='b'*40

class FakeAWS:
    def __init__(self):self.objects={};self.events=[];self.fail_key=None
    def put(self,key,file,content_type,immutable=False):
        if key==self.fail_key:raise RuntimeError('Simulated upload failure')
        data=Path(file).read_bytes()
        if immutable and key in self.objects and self.objects[key]!=data:raise ValueError('Immutable release conflict')
        self.objects[key]=data;self.events.append(key)
    def get(self,key,target):
        target=Path(target);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(self.objects[key])
    def invalidate(self):self.events.append('invalidate');return 'TEST'

class ReleaseTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
    def make(self,sha=A):
        folder=self.p/sha;build(ROOT/'site',folder,sha);return folder
    def test_published_assets_use_release_paths(self):
        f=self.make();html=(f/'index.html').read_text();js=(f/'app.js').read_text()
        self.assertIn('/releases/'+A+'/app.js',html)
        self.assertIn('/releases/'+A+'/assets/',js)
        self.assertIn('name="portfolio-release" content="'+A+'"',html)
    def test_build_is_deterministic(self):
        f=self.make();manifest=(f/'release.json').read_bytes();build(ROOT/'site',f,A)
        self.assertEqual(manifest,(f/'release.json').read_bytes())
    def test_tampered_asset_rejected(self):
        f=self.make();(f/'style.css').write_text('tampered')
        with self.assertRaises(ValueError):validate_release(f,A)
    def test_traversal_and_bad_sha_rejected(self):
        for path in ['../state','/private','a/../b','a\\b','a//b']:
            with self.assertRaises(ValueError):safe_path(path)
        with self.assertRaises(ValueError):build(ROOT/'site',self.p/'bad','main')
    def test_upload_failure_does_not_promote_index(self):
        aws=FakeAWS();aws.objects['index.html']=b'known good';aws.fail_key='releases/'+A+'/app.js'
        with self.assertRaises(RuntimeError):publish(aws,self.make(),A)
        self.assertEqual(aws.objects['index.html'],b'known good');self.assertNotIn('invalidate',aws.events)
    def test_rollback_restores_saved_bytes_without_new_uploads(self):
        aws=FakeAWS();publish(aws,self.make(A),A);old=aws.objects['index.html'];publish(aws,self.make(B),B)
        self.assertNotEqual(old,aws.objects['index.html']);folder=self.p/'rollback'
        fetch_release(aws,A,folder);aws.events=[];publish(aws,folder,A,upload=False)
        self.assertEqual(aws.objects['index.html'],old);self.assertEqual(aws.events,['index.html','invalidate'])
    def test_repeat_release_is_safe_but_modified_release_is_rejected(self):
        aws=FakeAWS();folder=self.make();publish(aws,folder,A);publish(aws,folder,A)
        with self.assertRaises(ValueError):aws.put('releases/'+A+'/app.js',folder/'index.html','text/javascript',immutable=True)
    def test_entry_page_is_last_before_invalidation(self):
        aws=FakeAWS();publish(aws,self.make(),A);self.assertEqual(aws.events[-2:],['index.html','invalidate'])

if __name__=='__main__':unittest.main()
