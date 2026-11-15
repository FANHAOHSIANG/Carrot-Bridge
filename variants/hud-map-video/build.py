"""Build the unsigned Android HUD map experiment from the released wide.70 APK."""
import argparse
from hashlib import file_digest
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from zipfile import ZipFile

from patch import BASE_SHA256, apply

HERE = Path(__file__).resolve().parent
SIGNATURE = re.compile(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))", re.I)


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def build(args, work):
    base, helper, stubs, classes, d8 = (work / name for name in ("base", "helper", "stubs", "classes", "d8"))
    dalvik = ("java", "-cp", args.apktool, HERE.parent / "wide69/Dalvik.java")
    dex = work / "classes.dex"
    with ZipFile(args.base) as apk:
        dex.write_bytes(apk.read(dex.name))
    run(*dalvik, "decode", dex, base)
    apply(base / "com/navipilot/obf")

    javac = ("java", "-m", "jdk.compiler/com.sun.tools.javac.Main", "-source", "17",
             "-target", "17", "-Xlint:-options", "-encoding", "UTF-8")
    run(*javac, "-cp", args.android, "-d", stubs, HERE / "stubs/ProjectionAndNavi.java")
    run(*javac, "-cp", f"{args.android}:{stubs}", "-d", classes, *sorted((HERE / "src").glob("*.java")))
    d8.mkdir()
    run("java", "-cp", args.d8, "com.android.tools.r8.D8", "--min-api", "31",
        "--lib", args.android, "--classpath", stubs, "--output", d8, *sorted(classes.rglob("*.class")))
    run(*dalvik, "decode", d8 / "classes.dex", helper)
    for smali in helper.rglob("*.smali"):
        target = base / smali.relative_to(helper)
        with target.open("xb") as target_file, smali.open("rb") as source:
            shutil.copyfileobj(source, target_file)
    run(*dalvik, "assemble", base, dex)

    unaligned, aligned = work / "unaligned.apk", work / "aligned.apk"
    with ZipFile(args.base) as original, ZipFile(unaligned, "w") as target:
        for entry in original.infolist():
            if not SIGNATURE.fullmatch(entry.filename):
                target.writestr(entry, dex.read_bytes() if entry.filename == dex.name else original.read(entry))
    run(args.zipalign, "-P", "16", "-f", "4", unaligned, aligned)
    run(args.zipalign, "-P", "16", "-c", "4", aligned)
    with ZipFile(args.base) as original, ZipFile(aligned) as target:
        if target.testzip():
            raise ValueError("APK CRC verification failed")
        expected = {name for name in original.namelist() if not SIGNATURE.fullmatch(name)}
        if set(target.namelist()) != expected:
            raise ValueError("Unexpected APK entries")
        changed = {name for name in expected if target.read(name) != original.read(name)}
        if changed != {dex.name}:
            raise ValueError(f"Unexpected APK payload changes: {changed}")
    with args.output.open("xb") as target, aligned.open("rb") as source:
        shutil.copyfileobj(source, target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "output"):
        parser.add_argument(name, type=Path)
    for name in ("android", "apktool", "d8", "zipalign"):
        parser.add_argument(f"--{name}", type=lambda value: Path(value).resolve(), required=True)
    args = parser.parse_args()
    with args.base.open("rb") as source:
        if file_digest(source, "sha256").hexdigest() != BASE_SHA256:
            parser.error("Expected the exact released wide.70 APK")
    if args.output.exists():
        parser.error("Choose a new output filename")
    with tempfile.TemporaryDirectory(prefix="bridge-hud-map-") as temp:
        build(args, Path(temp))
