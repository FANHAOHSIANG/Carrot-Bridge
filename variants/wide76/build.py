"""Build unsigned wide.76 from the exact signed wide.75, retaining its live layout fix."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from zipfile import ZipFile
from patch import apply, verify, PACKAGE

HERE = Path(__file__).resolve().parent
BASE_SHA256 = 'b71cd675cc554a5101baca281c8b1f5c9f8d320f1e81b04ad626b032fb653dfe'
SIGNATURE = re.compile(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))', re.I)

def run(*args):
    subprocess.run([str(a) for a in args], check=True)

def build(args, work):
    dalvik = ('java', '-cp', args.apktool, HERE.parent / 'wide69/Dalvik.java')
    parts = {'classes.dex': work / 'primary', 'classes8.dex': work / 'extras'}
    with ZipFile(args.base) as apk:
        for name, directory in parts.items():
            dex = work / name
            dex.write_bytes(apk.read(name))
            run(*dalvik, 'decode', dex, directory)
    apply(parts['classes.dex'])
    verify(parts['classes.dex'])
    stubs, classes, tests, dex = (work / name for name in ('stubs', 'classes', 'tests', 'dex'))
    dex.mkdir()
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', 17, '-target', 17, '-Xlint:-options', '-d', stubs, HERE / 'tests/Inputs.java', HERE / 'tests/SystemClock.java')
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', 17, '-target', 17, '-Xlint:-options', '-cp', stubs, '-d', classes, HERE / 'WideAmapCameraGlow.java')
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', 17, '-target', 17, '-Xlint:-options', '-cp', f'{stubs}:{classes}', '-d', tests, HERE / 'tests/GlowChecks.java')
    run('java', '-cp', f'{stubs}:{classes}:{tests}', 'com.navipilot.obf.GlowChecks')
    java_home = Path(shutil.which('java')).resolve().parent.parent
    run('java', '-cp', args.sdk / 'lib/d8.jar', 'com.android.tools.r8.D8', '--min-api', 31,
        '--lib', java_home, '--classpath', stubs, '--output', dex, *sorted(classes.rglob('*.class')))
    for path in (parts['classes8.dex'] / PACKAGE).glob('WideAmapCameraGlow*.smali'):
        path.unlink()
    run(*dalvik, 'decode', dex / 'classes.dex', parts['classes8.dex'])
    changes = {}
    for name, directory in parts.items():
        target = work / ('new-' + name)
        run(*dalvik, 'assemble', directory, target)
        changes[name] = target.read_bytes()
    with ZipFile(args.base) as apk:
        manifest = apk.read('AndroidManifest.xml')
        for old, new in [('wide.75'.encode('utf-16le'), 'wide.76'.encode('utf-16le')),
                         (struct.pack('<I', 26110787), struct.pack('<I', 26110788))]:
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
    for name in ('base', 'sdk', 'apktool', 'output'):
        parser.add_argument(name, type=lambda p: Path(p).resolve())
    args = parser.parse_args()
    if hashlib.sha256(args.base.read_bytes()).hexdigest() != BASE_SHA256:
        parser.error('Expected exact signed wide.75')
    if args.output.exists(): parser.error('Choose a new output filename')
    with tempfile.TemporaryDirectory(prefix='wide76-build-') as tmp: build(args, Path(tmp))
