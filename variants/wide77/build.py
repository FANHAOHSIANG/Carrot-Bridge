"""Build the night-mode continuity fix from the signed wide.76 APK."""
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile
from patch import manifest, side_selection
from test_manifest import check

HERE = Path(__file__).resolve().parent
BASE_SHA256 = '7b083b16b1aabe1ac0e3bb122890e04f525bbad4b16688f1db65388a879a7335'
SIGNATURE = re.compile(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))', re.I)

def run(*args): subprocess.run([str(a) for a in args], check=True)

def build(args, work):
    dalvik = ('java', '-cp', args.apktool, HERE.parent/'wide69/Dalvik.java')
    primary = work/'primary'
    with ZipFile(args.base) as old:
        raw = old.read('AndroidManifest.xml')
        check(raw)
        (work/'classes.dex').write_bytes(old.read('classes.dex'))
    run(*dalvik, 'decode', work/'classes.dex', primary)
    # Existing callback dispatches new resources to Compose without rebuilding views.
    inherited = (primary/'com/navipilot/obf/Ug.smali').read_text()
    start = inherited.index('.method public final onConfigurationChanged(')
    callback = inherited[start:inherited.index('.end method', start)]
    assert 'Activity;->onConfigurationChanged(' in callback
    assert 'zi;->a(Ljava/lang/Object;)V' in callback
    assert 'recreate()' not in callback
    side_selection(primary)
    run(*dalvik, 'assemble', primary, work/'new-classes.dex')
    changes = {'classes.dex': (work/'new-classes.dex').read_bytes(),
               'AndroidManifest.xml': manifest(raw)}
    with ZipFile(args.base) as old, ZipFile(work/'unaligned.apk', 'w') as apk:
        for item in old.infolist():
            if not SIGNATURE.fullmatch(item.filename):
                apk.writestr(item, changes.get(item.filename, old.read(item)))
    run(args.sdk/'zipalign', '-P', 16, '-f', 4, work/'unaligned.apk', work/'aligned.apk')
    run(args.sdk/'zipalign', '-P', 16, '-c', 4, work/'aligned.apk')
    with ZipFile(args.base) as old, ZipFile(work/'aligned.apk') as new:
        entries = {n for n in old.namelist() if not SIGNATURE.fullmatch(n)}
        assert set(new.namelist()) == entries and new.testzip() is None
        assert {n for n in entries if old.read(n) != new.read(n)} == set(changes)
    with args.output.open('xb') as out: out.write((work/'aligned.apk').read_bytes())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base','sdk','apktool','output'): parser.add_argument(name, type=lambda p: Path(p).resolve())
    args = parser.parse_args()
    if hashlib.sha256(args.base.read_bytes()).hexdigest() != BASE_SHA256: parser.error('Expected signed wide.76')
    if args.output.exists(): parser.error('Choose a new output filename')
    with tempfile.TemporaryDirectory(prefix='wide77-build-') as tmp: build(args,Path(tmp))
