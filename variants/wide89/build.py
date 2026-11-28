"""Build exact wide.88 with temporary outbound PRE suppression. No vehicle-side changes."""
import argparse,hashlib,re,struct,subprocess,tempfile
from pathlib import Path
from zipfile import ZipFile
HERE=Path(__file__).resolve().parent
BASE='0cbe7761a024372a9064671064a04ab9268e8d818cd3e7fc307286c9b375ef5a'
SIG=re.compile(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',re.I)
def run(*cmd):subprocess.run([str(x) for x in cmd],check=True)
def replace_method(path, signature, source_reg, keys, empty_is_null):
    s=path.read_text()
    pattern=r"(?m)^(\.method [^\n]*\b"+re.escape(signature)+r")\n[\s\S]*?^\.end method"
    matches=list(re.finditer(pattern,s))
    assert len(matches)==1, f"Expected one exact method in {path.name}: {signature}"
    m=matches[0]
    assert " static " in m.group(1), "Expected static method"
    assert all('"'+key+'"' in m.group() for key in keys), "Unexpected base implementation"
    lines=[m.group(1),"    .locals 3",
           f"    if-eqz {source_reg}, :no_value",
           "    :try_start",
           f"    invoke-virtual/range {{{source_reg} .. {source_reg}}}, Lorg/json/JSONObject;->toString()Ljava/lang/String;",
           "    move-result-object v0",
           "    new-instance v1, Lorg/json/JSONObject;",
           "    invoke-direct {v1, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V"]
    for key in keys:
        lines += [f'    const-string v2, "{key}"',
                  "    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->remove(Ljava/lang/String;)Ljava/lang/Object;"]
    if empty_is_null:
        lines += ["    invoke-virtual {v1}, Lorg/json/JSONObject;->length()I",
                  "    move-result v2","    if-eqz v2, :no_value"]
    lines += ["    :try_end","    return-object v1",
              "    .catch Ljava/lang/Exception; {:try_start .. :try_end} :invalid",
              "    :invalid","    move-exception v0","    :no_value",
              "    const/4 v0, 0x0","    return-object v0",".end method"]
    path.write_text(s[:m.start()]+"\n".join(lines)+s[m.end():])
    result=path.read_text()
    changed=list(re.finditer(pattern,result))
    assert len(changed)==1 and "->put(" not in changed[0].group()
    assert changed[0].group().count("->remove(")==len(keys)

def build(a,w):
    dalvik=('java','-cp',a.apktool,HERE.parent/'wide69/Dalvik.java')
    primary=w/'primary';classes=w/'classes';stubs=w/'stubs';tests=w/'tests';dex=w/'dex';dex.mkdir()
    with ZipFile(a.base) as z:(w/'old.dex').write_bytes(z.read('classes.dex'))
    run(*dalvik,'decode',w/'old.dex',primary)
    pkg=primary/'com/navipilot/obf'
    replace_method(pkg/'WideAmapPreAdjust.smali',
        'finish(Lorg/json/JSONObject;Lorg/json/JSONObject;J)Lorg/json/JSONObject;',
        'p1', ('_copilot_amap_pre_adjust','_copilot_amap_pre_adjust_at','pre_adjust'), True)
    replace_method(pkg/'WideSharedPreAdjust.smali',
        'status(Lorg/json/JSONObject;Ljava/lang/String;JJJZ)Lorg/json/JSONObject;',
        'p0', ('pre_adjust_control',), False)
    for name in ('WideBridgeLog','WideBridge','WideTelemetry','WideCamera'):
        for p in pkg.glob(name+'*.smali'):
            s=p.read_text()
            if 'wide.88' in s:p.write_text(s.replace('wide.88','wide.89'))
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
