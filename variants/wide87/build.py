"""Build exact wide.86 with passive Amap Auto accepted-broadcast observation."""
import argparse,hashlib,re,struct,subprocess,tempfile
from pathlib import Path
from zipfile import ZipFile
HERE=Path(__file__).resolve().parent
BASE='e0f31266ce9ae9a0a757e9ddd4d9fd1098fa86eb79ab5e765fb814f19b1401f1'
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
    m=re.search(r'(?m)^\.method [^\n]*accept\(Landroid/content/BroadcastReceiver;Landroid/content/Intent;\)Z\n[\s\S]*?^\.end method',s)
    assert m,'existing receiver acceptance method missing'
    body=m.group()
    # This invocation occurs only after matches(selected,sender,action) succeeds.
    anchor=re.search(r'(?m)^    invoke-virtual \{[^\n]+\}, Ljava/util/WeakHashMap;->put\(Ljava/lang/Object;Ljava/lang/Object;\)Ljava/lang/Object;\s*$',body)
    assert anchor and len(re.findall(r'WeakHashMap;->put\(',body))==1 and '->matches(' in body,'unexpected acceptance path'
    hook='    invoke-static/range {p1 .. p1}, Lcom/navipilot/obf/WideAutoObservation;->capture(Landroid/content/Intent;)V\n\n'
    body=body[:anchor.start()]+hook+body[anchor.start():]
    source.write_text(s[:m.start()]+body+s[m.end():])
    for p in pkg.glob('WideBridgeLog*.smali'):
        s=p.read_text()
        if 'wide.86' in s:p.write_text(s.replace('wide.86','wide.87'))
    # Correct known stale diagnostic version labels, only in WideBridge/report helpers.
    for name in ('WideBridge','WideTelemetry','WideCamera'):
        for p in pkg.glob(name+'*.smali'):
            s=p.read_text()
            if 'Carrot Bridge wide.73' in s:p.write_text(s.replace('Carrot Bridge wide.73','Carrot Bridge wide.87'))
    run('javac','--release','8','-cp',a.json,'-d',stubs,*sorted((HERE/'stubs').rglob('*.java')))
    run('javac','--release','8','-cp',str(stubs)+':'+str(a.json),'-d',classes,HERE/'WideAutoObservation.java')
    run('javac','--release','8','-cp',str(stubs)+':'+str(a.json)+':'+str(classes),'-d',tests,HERE/'AutoChecks.java')
    run('java','-cp',':'.join(map(str,[stubs,a.json,classes,tests])),'com.navipilot.obf.AutoChecks')
    run(a.sdk/'d8','--min-api','31','--lib',a.androidjar,'--classpath',stubs,'--output',dex,*sorted(classes.rglob('*.class')))
    run(*dalvik,'decode',dex/'classes.dex',primary)
    run(*dalvik,'assemble',primary,w/'new.dex')
    with ZipFile(a.base) as z:
        manifest=z.read('AndroidManifest.xml')
        for old,new in [('wide.86'.encode('utf-16le'),'wide.87'.encode('utf-16le')),(struct.pack('<I',26110798),struct.pack('<I',26110799))]:
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
    if hashlib.sha256(a.base.read_bytes()).hexdigest()!=BASE:p.error('Expected exact signed wide.86')
    if a.output.exists():p.error('choose unused output path')
    with tempfile.TemporaryDirectory(prefix='wide87-') as t:build(a,Path(t))
