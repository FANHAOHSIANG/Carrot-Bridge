"""Build exact wide.88 with enhanced passive AMap Auto route diagnostics."""
import argparse,hashlib,re,struct,subprocess,tempfile
from pathlib import Path
from zipfile import ZipFile
HERE=Path(__file__).resolve().parent
BASE='0cbe7761a024372a9064671064a04ab9268e8d818cd3e7fc307286c9b375ef5a'
SIG=re.compile(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',re.I)
def run(*cmd):subprocess.run([str(x) for x in cmd],check=True)
def build(a,w):
    dalvik=('java','-cp',a.apktool,HERE.parent/'wide69/Dalvik.java')
    primary=w/'primary';classes=w/'classes';stubs=w/'stubs';tests=w/'tests';dex=w/'dex';dex.mkdir()
    with ZipFile(a.base) as z:(w/'old.dex').write_bytes(z.read('classes.dex'))
    run(*dalvik,'decode',w/'old.dex',primary)
    pkg=primary/'com/navipilot/obf'
    source=pkg/'WideAmapSource.smali'
    s=source.read_text()
    assert s.count('WideAutoObservation;->capture(Landroid/content/Intent;)V')==1,'expected existing accepted receiver hook'
    old=list(pkg.glob('WideAutoObservation*.smali'))
    assert len(old)>=2,'expected original observation classes'
    for p in old:p.unlink()
    trace=pkg/'WideAmapLinkTrace.smali'
    assert trace.is_file(),'expected Link trace hook class'
    trace.unlink()
    for name in ('WideBridgeLog','WideBridge','WideTelemetry','WideCamera'):
        for p in pkg.glob(name+'*.smali'):
            s=p.read_text()
            if 'wide.88' in s:p.write_text(s.replace('wide.88','wide.89'))
    run('javac','--release','8','-cp',a.json,'-d',stubs,*sorted((HERE.parent/'wide88/stubs').rglob('*.java')))
    run('javac','--release','8','-cp',str(stubs)+':'+str(a.json),'-d',classes,HERE/'WideAutoObservation.java',HERE/'WideAmapLinkTrace.java',HERE/'WideLaneCandidate.java')
    run('javac','--release','8','-cp',str(stubs)+':'+str(a.json)+':'+str(classes),'-d',tests,HERE/'AutoChecks.java',HERE/'ObservationChecks.java')
    run('java','-cp',':'.join(map(str,[stubs,a.json,classes,tests])),'com.navipilot.obf.AutoChecks')
    run('java','-cp',':'.join(map(str,[stubs,a.json,classes,tests])),'com.navipilot.obf.ObservationChecks')
    run(a.sdk/'d8','--min-api','31','--lib',a.androidjar,'--classpath',stubs,'--output',dex,*sorted(classes.rglob('*.class')))
    run(*dalvik,'decode',dex/'classes.dex',primary)
    run(*dalvik,'assemble',primary,w/'new.dex')
    with ZipFile(a.base) as z:
        manifest=z.read('AndroidManifest.xml')
        for old,new in [('wide.88'.encode('utf-16le'),'wide.89'.encode('utf-16le')),(struct.pack('<I',26110800),struct.pack('<I',26110801))]:
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
    if hashlib.sha256(a.base.read_bytes()).hexdigest()!=BASE:p.error('Expected exact signed wide.88')
    if a.output.exists():p.error('choose unused output path')
    with tempfile.TemporaryDirectory(prefix='wide89-') as t:build(a,Path(t))
