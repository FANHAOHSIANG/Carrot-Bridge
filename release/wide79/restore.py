"""Reconstruct the exact signed APK from bounded per-ZIP-entry binary deltas."""
import hashlib,json,sys
from pathlib import Path
import bsdiff4

def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def restore(base,root,out):
 root=Path(root);meta=json.loads((root/'delta.json').read_text())
 assert digest(base)==meta['base_sha256']
 patches=b''.join(p.read_bytes() for p in sorted((root/'chunks').glob('*.bin')))
 with open(base,'rb') as source,open(out,'xb') as target:
  for kind,start,size,pstart,psize in meta['ops']:
   source.seek(start)
   if kind=='copy':
    while size:
     data=source.read(min(size,1048576));assert data;target.write(data);size-=len(data)
   else:
    target.write(bsdiff4.patch(source.read(size),patches[pstart:pstart+psize]))
 assert digest(out)==meta['sha256']

if __name__=='__main__':restore(*sys.argv[1:])
