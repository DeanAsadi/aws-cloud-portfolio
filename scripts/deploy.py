"""Publish immutable releases and roll back by promoting a verified saved entry page.
No delete permissions, infrastructure mutation, or credential storage is required.
"""
import argparse, datetime, hashlib, json, os, re, subprocess, tempfile, time, urllib.request
from pathlib import Path
from release import SHA, digest, safe_path, validate_release

class AWS:
    def __init__(self, bucket, distribution):
        self.bucket=bucket; self.distribution=distribution
    def call(self, service, operation, *args):
        p=subprocess.run(['aws',service,operation,*args,'--region','us-east-1','--output','json','--no-cli-pager'],capture_output=True,text=True)
        if p.returncode: raise RuntimeError(p.stderr.strip())
        return json.loads(p.stdout) if p.stdout.strip() else {}
    def get(self, key, target):
        target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
        return self.call('s3api','get-object','--bucket',self.bucket,'--key',key,str(target))
    def put(self, key, file, content_type, immutable=False):
        args=['--bucket',self.bucket,'--key',key,'--body',str(file),'--content-type',content_type,
              '--cache-control','public,max-age=31536000,immutable' if immutable else 'no-cache',
              '--server-side-encryption','AES256']
        if immutable: args+=['--if-none-match','*']
        try: return self.call('s3api','put-object',*args)
        except RuntimeError as e:
            if not immutable or ('PreconditionFailed' not in str(e) and '412' not in str(e)): raise
            with tempfile.TemporaryDirectory() as tmp:
                old=Path(tmp)/'existing';self.get(key,old)
                if old.read_bytes()!=Path(file).read_bytes(): raise ValueError('Immutable release cannot be overwritten')
    def invalidate(self):
        r=self.call('cloudfront','create-invalidation','--distribution-id',self.distribution,'--paths','/','/index.html')
        id=r['Invalidation']['Id']
        self.call('cloudfront','wait','invalidation-completed','--distribution-id',self.distribution,'--id',id)
        return id

def fetch_release(aws, sha, target):
    if not SHA.fullmatch(sha): raise ValueError('Invalid rollback SHA')
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    aws.get('releases/'+sha+'/release.json',target/'release.json')
    m=json.loads((target/'release.json').read_text())
    if m.get('release')!=sha: raise ValueError('Wrong saved release')
    for item in m['files']:
        key=safe_path(item['path']);aws.get('releases/'+sha+'/'+key,target/key)
    return validate_release(target,sha)

def publish(aws, folder, sha, upload=True):
    folder=Path(folder);m=validate_release(folder,sha)
    if upload:
        for item in m['files']:
            aws.put('releases/'+sha+'/'+item['path'],folder/item['path'],item['content_type'],immutable=True)
        aws.put('releases/'+sha+'/release.json',folder/'release.json','application/json',immutable=True)
    # Promote only after every referenced object is present. Previous releases remain intact.
    aws.put('index.html',folder/'index.html','text/html',immutable=False)
    invalidation=aws.invalidate()
    return {'release':sha,'invalidation':invalidation,'published_files':len(m['files'])}

def verify(url, folder, sha):
    folder=Path(folder);m=validate_release(folder,sha); checks=[]
    for item in m['files']:
        path='' if item['path']=='index.html' else 'releases/'+sha+'/'+item['path']
        with urllib.request.urlopen(url.rstrip('/')+'/'+path,timeout=30) as response:
            data=response.read();assert response.status==200
        if digest(data)!=item['sha256']: raise ValueError('Public checksum mismatch: '+path)
        checks.append({'path':path or '/', 'status':200,'sha256':digest(data)})
    return checks

def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['deploy','rollback'])
    parser.add_argument('--sha',required=True);parser.add_argument('--folder',default='artifacts/site')
    args=parser.parse_args()
    if not SHA.fullmatch(args.sha): raise ValueError('Expected a full lowercase commit SHA')
    aws=AWS(os.environ['SITE_BUCKET'],os.environ['DISTRIBUTION_ID']);url=os.environ['SITE_URL']
    folder=Path(args.folder)
    if args.mode=='rollback':fetch_release(aws,args.sha,folder)
    r=publish(aws,folder,args.sha,upload=args.mode=='deploy')
    # Invalidation must finish before verifying the promoted root entry page.
    r.update({'mode':args.mode,'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'public_checks':verify(url,folder,args.sha),'url':url,'run_id':os.environ.get('GITHUB_RUN_ID')})
    Path('artifacts').mkdir(exist_ok=True);Path('artifacts/deployment.json').write_text(json.dumps(r,indent=2)+'\n')
    with open(os.environ.get('GITHUB_STEP_SUMMARY',os.devnull),'a') as f:
        f.write(f"## {args.mode.title()} verified\n\nRelease `{args.sha}`\n\n{len(r['public_checks'])} public files matched their SHA-256 checksums.\n\n[Live portfolio]({url})\n")
    print(json.dumps({k:v for k,v in r.items() if k!='public_checks'},indent=2))

if __name__=='__main__':main()
