"""Rebuild the exact wide.85 APK with diagnostic-only changes; no signing keys here."""
import argparse, hashlib, re, struct, subprocess, tempfile
from pathlib import Path
from zipfile import ZipFile
HERE=Path(__file__).resolve().parent
BASE='344ae6f633a70e92923b627e664e927fda714dca37e8e098e21004ec94a33483'
SIG=re.compile(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',re.I)
def run(*cmd):subprocess.run([str(x) for x in cmd],check=True)
def build(a,w):
    dalvik=('java','-cp',a.apktool,HERE.parent/'wide69/Dalvik.java')
    primary=w/'primary';classes=w/'classes';dex=w/'dex';dex.mkdir()
    with ZipFile(a.base) as z:(w/'old.dex').write_bytes(z.read('classes.dex'))
    run(*dalvik,'decode',w/'old.dex',primary)
    pkg=primary/'com/navipilot/obf'
    target=pkg/'WideAmapLinkTrace.smali'
    assert target.is_file()
    # Update recorder capacity in existing writer only; no change to its toggle or export behavior.
    logger=pkg/'WideBridgeLog.smali'
    s=logger.read_text()
    old='0x400000'
    assert len(re.findall(r'(?m)^\s*const(?:/high16)? [vp]\d+, 0x400000\s*$',s))==1,'unexpected logger rotation literal'
    s=re.sub(r'(?m)^(\s*const(?:/high16)? [vp]\d+, )0x400000(\s*)$',r'\g<1>0x1000000\2',s)
    assert '12 MB' in s and 'wide.73' in s,'unexpected logger labels'
    logger.write_text(s.replace('12 MB','48 MB').replace('wide.73','wide.86'))
    # Remove existing trace class only and assemble fresh implementation.
    target.unlink()
    run('javac','--release','8','-cp',a.json,'-d',classes,HERE/'WideAmapLinkTrace.java',HERE/'ObservationChecks.java')
    run('java','-cp',str(classes)+':'+str(a.json),'com.navipilot.obf.ObservationChecks')
    (classes/'com/navipilot/obf/ObservationChecks.class').unlink()
    run(a.sdk/'d8','--min-api','31','--lib',a.androidjar,'--output',dex,*sorted(classes.rglob('*.class')))
    run(*dalvik,'decode',dex/'classes.dex',primary)
    run(*dalvik,'assemble',primary,w/'new.dex')
    with ZipFile(a.base) as z:
        manifest=z.read('AndroidManifest.xml')
        for old,new in [('wide.85'.encode('utf-16le'),'wide.86'.encode('utf-16le')),(struct.pack('<I',26110797),struct.pack('<I',26110798))]:
            assert manifest.count(old)==1
            manifest=manifest.replace(old,new)
        changes={'classes.dex':(w/'new.dex').read_bytes(),'AndroidManifest.xml':manifest}
        with ZipFile(w/'unaligned.apk','w') as out:
            for entry in z.infolist():
                if not SIG.fullmatch(entry.filename):out.writestr(entry,changes.get(entry.filename,z.read(entry)))
    run(a.sdk/'zipalign','-P','16','-f','4',w/'unaligned.apk',a.output)
    run(a.sdk/'zipalign','-P','16','-c','4',a.output)
    with ZipFile(a.base) as old,ZipFile(a.output) as new:
        assert new.testzip() is None
        entries={n for n in old.namelist() if not SIG.fullmatch(n)}
        assert set(new.namelist())==entries
        assert {n for n in entries if old.read(n)!=new.read(n)}==set(changes)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('base','sdk','androidjar','apktool','json','output'):p.add_argument(n,type=lambda x:Path(x).resolve())
    a=p.parse_args()
    if hashlib.sha256(a.base.read_bytes()).hexdigest()!=BASE:p.error('Expected exact signed wide.85')
    if a.output.exists():p.error('choose unused output path')
    with tempfile.TemporaryDirectory(prefix='wide86-') as t:build(a,Path(t))
