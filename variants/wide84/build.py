"""Build unsigned wide.84 from the exact signed wide.77, retaining its live layout fix."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from zipfile import ZipFile
from patch import apply, PACKAGE

HERE = Path(__file__).resolve().parent
BASE_SHA256 = '779c550c05ce5b59193f1c1b1a498e8f9b40f5d1eb27789514ab7ba14e51bc82'
SIGNATURE = re.compile(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))', re.I)

def run(*args):
    subprocess.run([str(a) for a in args], check=True)

def build(args, work):
    dalvik = ('java', '-cp', args.apktool, HERE.parent / 'wide69/Dalvik.java')
    parts = {'classes.dex': work / 'primary'}
    with ZipFile(args.base) as apk:
        for name, directory in parts.items():
            dex = work / name
            dex.write_bytes(apk.read(name))
            run(*dalvik, 'decode', dex, directory)
    run('python3', HERE.parent / 'wide81/tests/test_patch.py')
    apply(parts['classes.dex'])
    stubs, classes, tests, dex = (work / name for name in ('stubs', 'classes', 'tests', 'dex'))
    dex.mkdir()
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', 17, '-target', 17, '-Xlint:-options', '-d', stubs, '-cp', args.json, HERE.parent / 'wide79/tests/BuildInputs.java', *sorted((HERE.parent / 'wide79/tests/android').rglob('*.java')), *sorted((HERE.parent / 'wide82/tests/android').rglob('*.java')))
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', 17, '-target', 17, '-Xlint:-options', '-cp', f'{stubs}:{args.json}', '-d', classes, HERE.parent / 'wide78/WideAmapPreAdjust.java', HERE.parent / 'wide79/WideSharedPreAdjust.java', HERE / 'WideAmapExitInfo.java')
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', 17, '-target', 17, '-Xlint:-options', '-cp', f'{stubs}:{classes}:{args.json}', '-d', tests, HERE.parent / 'wide78/tests/PreAdjustChecks.java', HERE.parent / 'wide79/tests/SharedChecks.java', HERE / 'tests/ExitInfoChecks.java')
    run('java', '-cp', f'{stubs}:{classes}:{tests}:{args.json}', 'com.navipilot.obf.PreAdjustChecks')
    run('java', '-cp', f'{stubs}:{classes}:{tests}:{args.json}', 'com.navipilot.obf.SharedChecks')
    run('java', '-cp', f'{stubs}:{classes}:{tests}:{args.json}', 'com.navipilot.obf.ExitInfoChecks')
    java_home = Path(shutil.which('java')).resolve().parent.parent
    run('java', '-cp', args.sdk / 'lib/d8.jar', 'com.android.tools.r8.D8', '--min-api', 31,
        '--lib', java_home, '--classpath', stubs, '--classpath', args.json, '--output', dex, *sorted(classes.rglob('*.class')))
    for path in (parts['classes.dex'] / PACKAGE).glob('WideAmapPreAdjust*.smali'):
        path.unlink()
    run(*dalvik, 'decode', dex / 'classes.dex', parts['classes.dex'])
    changes = {}
    for name, directory in parts.items():
        target = work / ('new-' + name)
        run(*dalvik, 'assemble', directory, target)
        changes[name] = target.read_bytes()
    with ZipFile(args.base) as apk:
        manifest = apk.read('AndroidManifest.xml')
        for old, new in [('wide.77'.encode('utf-16le'), 'wide.84'.encode('utf-16le')),
                         (struct.pack('<I', 26110789), struct.pack('<I', 26110796))]:
            if manifest.count(old) != 1: raise ValueError('Unexpected APK version')
            manifest = manifest.replace(old, new)
        changes['AndroidManifest.xml'] = manifest
        unaligned = work / 'unaligned.apk'
        with ZipFile(unaligned, 'w') as out:
            for entry in apk.infolist():
                if not SIGNATURE.fullmatch(entry.filename):
                    out.writestr(entry, changes.get(entry.filename, apk.read(entry)))
    aligned = work / 'aligned.apk'
    run(args.sdk / 'zipalign', '-P', 16, '-f', 4, unaligned, aligned)
    run(args.sdk / 'zipalign', '-P', 16, '-c', 4, aligned)
    with ZipFile(args.base) as old, ZipFile(aligned) as new:
        assert new.testzip() is None
        entries = {n for n in old.namelist() if not SIGNATURE.fullmatch(n)}
        assert set(new.namelist()) == entries
        assert {n for n in entries if old.read(n) != new.read(n)} == set(changes)
    with args.output.open('xb') as out: out.write(aligned.read_bytes())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'sdk', 'apktool', 'json', 'output'):
        parser.add_argument(name, type=lambda p: Path(p).resolve())
    args = parser.parse_args()
    if hashlib.sha256(args.base.read_bytes()).hexdigest() != BASE_SHA256:
        parser.error('Expected exact signed wide.77')
    if args.output.exists(): parser.error('Choose a new output filename')
    with tempfile.TemporaryDirectory(prefix='wide84-build-') as tmp: build(args, Path(tmp))
