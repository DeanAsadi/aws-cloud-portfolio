"""Deterministic static release packaging and checksum validation. No cloud access."""
import argparse, hashlib, json, mimetypes, re, shutil
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

SHA = re.compile(r'^[0-9a-f]{40}$')
PUBLIC_URL = 'https://d25v5xu84onas.cloudfront.net/'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_path(key):
    p = PurePosixPath(key)
    if not key or key.startswith('/') or '\\' in key or '..' in p.parts or str(p) != key:
        raise ValueError('Unsafe release path')
    return key

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.references = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            if attrs['id'] in self.ids: raise ValueError('Duplicate HTML ID')
            self.ids.add(attrs['id'])
        self.references.extend(attrs[k] for k in ('href', 'src') if attrs.get(k))

def validate_source(source):
    source = Path(source); parser = Links(); parser.feed((source/'index.html').read_text())
    refs = parser.references + re.findall(r'(?:src|href)="(assets/[^"]+)"', (source/'app.js').read_text())
    for ref in refs:
        if ref.startswith('#'):
            if ref[1:] not in parser.ids: raise ValueError('Missing anchor: '+ref)
        elif not re.match(r'[a-z]+:', ref):
            key = safe_path(ref.split('?')[0])
            if not (source/key).is_file(): raise ValueError('Missing local asset: '+key)
    for f in source.rglob('*'):
        if f.is_symlink(): raise ValueError('Symlinks are not release assets')
        if f.is_file():
            data = f.read_bytes()
            if b'PRIVATE KEY-----' in data or b'AKIA' in data or f.suffix in ('.tfstate','.tfvars'):
                raise ValueError('Unexpected sensitive asset: '+f.name)

def build(source, target, sha):
    if not SHA.fullmatch(sha): raise ValueError('Release must be a full lowercase commit SHA')
    validate_source(source); target = Path(target)
    if target.exists(): shutil.rmtree(target)
    shutil.copytree(source, target)
    prefix = '/releases/'+sha+'/'
    for name in ('index.html', 'app.js'):
        p = target/name; text = p.read_text().replace('assets/', prefix+'assets/')
        if name == 'index.html':
            text = text.replace('href="style.css"', 'href="'+prefix+'style.css"')
            text = text.replace('src="app.js', 'src="'+prefix+'app.js')
            text = text.replace('<head>', '<head><meta name="portfolio-release" content="'+sha+'">')
        p.write_text(text)
    files = []
    for f in sorted(target.rglob('*')):
        if f.is_file():
            key = safe_path(f.relative_to(target).as_posix())
            files.append({'path':key,'sha256':digest(f.read_bytes()),'size':f.stat().st_size,
                          'content_type':mimetypes.guess_type(key)[0] or 'application/octet-stream'})
    manifest = {'schema':1,'release':sha,'files':files}
    (target/'release.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    validate_release(target, sha)
    return manifest

def validate_release(folder, expected):
    folder = Path(folder); m = json.loads((folder/'release.json').read_text())
    if m.get('schema') != 1 or m.get('release') != expected or not SHA.fullmatch(expected):
        raise ValueError('Release identity mismatch')
    paths = set()
    for item in m['files']:
        key = safe_path(item['path'])
        if key in paths: raise ValueError('Duplicate manifest path')
        paths.add(key); data = (folder/key).read_bytes()
        if digest(data) != item['sha256'] or len(data) != item['size']:
            raise ValueError('Release checksum mismatch: '+key)
    if not {'index.html','style.css','app.js'} <= paths: raise ValueError('Incomplete release')
    return m

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--sha',required=True)
    parser.add_argument('--source',default='site'); parser.add_argument('--output',default='artifacts/site')
    args=parser.parse_args(); m=build(args.source,args.output,args.sha)
    print('Validated release',m['release'],'with',len(m['files']),'files')
