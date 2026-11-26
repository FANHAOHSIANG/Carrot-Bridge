"""Reconstruct exact already-signed wide83 APK using public signature bytes only."""
from pathlib import Path
import argparse, base64, hashlib, io, struct, zipfile, zlib
BASE_SHA = '6ac9fcc6b34bcecca3a06eae8c31aee4485f305a5a1d13627e3d664f167f0823'
SIGNED_SHA = '38e246a0d297cde2c0883b7a18821a44b260ffb180822246492e0090fc6a4a9a'

def rebuild(data, block):
    if hashlib.sha256(data).hexdigest()!=BASE_SHA:
        raise ValueError("Pinned unsigned APK hash mismatch")
    assert len(block)==4096 and block[-16:]==b'APK Sig Block 42'
    out=bytearray(); offsets={}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        entries=z.infolist(); assert entries==sorted(entries,key=lambda x:x.header_offset)
        for i,x in enumerate(entries):
            start=x.header_offset
            end=entries[i+1].header_offset if i+1<len(entries) else z.start_dir
            assert data[start:start+4]==b'PK\x03\x04'
            n,e=struct.unpack_from('<HH',data,start+26)
            h=bytearray(data[start:start+30+n]); extra=data[start+30+n:start+30+n+e]
            assert not any(extra), 'unexpected unsigned local extra'
            offsets[start]=len(out)
            if x.compress_type==0:
                align=16384 if x.filename.startswith('lib/') and x.filename.endswith('.so') else 4
                pad=(-(len(out)+len(h)+6))%align
                extra=struct.pack('<HHH',0xd935,2+pad,align)+bytes(pad)
            else: assert not extra
            struct.pack_into('<H',h,28,len(extra)); out+=h+extra+data[start+30+n+e:end]
        out+=bytes((-len(out))%4096);out+=block
        central=len(out); p=z.start_dir
        for x in entries:
            assert data[p:p+4]==b'PK\x01\x02'
            n,e,c=struct.unpack_from('<HHH',data,p+28); end=p+46+n+e+c
            h=bytearray(data[p:end]);offset=struct.unpack_from('<I',h,42)[0];assert offset==x.header_offset
            struct.pack_into('<I',h,42,offsets[offset]);out+=h;p=end
        assert data[p:p+4]==b'PK\x05\x06' and p+22==len(data)
        tail=bytearray(data[p:]);struct.pack_into('<I',tail,16,central);out+=tail
    if hashlib.sha256(out).hexdigest()!=SIGNED_SHA:
        raise ValueError("Exact signed APK hash mismatch")
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('unsigned',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    block=zlib.decompress(base64.b64decode(Path(__file__).with_name('public-block.zlib.b64').read_text().strip(),validate=True))
    result=rebuild(a.unsigned.read_bytes(),block)
    with a.output.open('xb') as f:f.write(result)
    print('Verified exact signed APK SHA-256', SIGNED_SHA)
