"""Build the unsigned split-toggle test APK from the published wide.74 APK."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from zipfile import ZipFile

from patch import apply

HERE = Path(__file__).resolve().parent
BASE_SHA256 = "e838258c1eb857202d24ee05ea1a8b392615d428416c4506e8f4cbc969c44a2d"
SIGNATURE = re.compile(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))", re.I)


def digest(source):
    return hashlib.file_digest(source, "sha256").hexdigest()


def run(*args):
    subprocess.run(args, check=True)


def release_manifest(original):
    manifest = original
    for old, new in (("wide.74".encode("utf-16le"), "wide.75".encode("utf-16le")),
                     (struct.pack("<I", 26110786), struct.pack("<I", 26110787))):
        if manifest.count(old) != 1:
            raise ValueError("Unexpected wide.74 manifest version")
        manifest = manifest.replace(old, new)
    return manifest


def build(args, work):
    dalvik = ("java", "-cp", args.apktool, HERE.parent / "wide69/Dalvik.java")
    paths = {name: (work / name, work / (name + "-decoded"), work / ("new-" + name))
             for name in ("classes.dex", "classes8.dex")}
    with ZipFile(args.base) as base:
        for name, (dex, smali, _) in paths.items():
            dex.write_bytes(base.read(name))
            run(*dalvik, "decode", dex, smali)
        apply(*(item[1] for item in paths.values()))
        for _, smali, output in paths.values():
            run(*dalvik, "assemble", smali, output)

        unaligned = work / "unaligned.apk"
        with ZipFile(unaligned, "w") as apk:
            for item in base.infolist():
                if not SIGNATURE.fullmatch(item.filename):
                    data = paths.get(item.filename)
                    payload = data[2].read_bytes() if data else base.read(item)
                    if item.filename == "AndroidManifest.xml":
                        payload = release_manifest(payload)
                    apk.writestr(item, payload)

    aligned = work / "aligned.apk"
    run(args.zipalign, "-P", "16", "-f", "4", unaligned, aligned)
    run(args.zipalign, "-P", "16", "-c", "4", aligned)
    with ZipFile(args.base) as base, ZipFile(aligned) as apk:
        expected = {name for name in base.namelist() if not SIGNATURE.fullmatch(name)}
        if set(apk.namelist()) != expected or apk.testzip():
            raise ValueError("APK inventory or ZIP integrity mismatch")
        changed = {name for name in expected if apk.read(name) != base.read(name)}
        if changed != set(paths) | {"AndroidManifest.xml"}:
            raise ValueError(f"Unexpected APK payload changes: {changed}")
    with args.output.open("xb") as target, aligned.open("rb") as source:
        shutil.copyfileobj(source, target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "output", "apktool", "zipalign"):
        flag = f"--{name}" if name in ("apktool", "zipalign") else name
        kwargs = {"required": True} if flag.startswith("--") else {}
        parser.add_argument(flag, type=lambda value: Path(value).resolve(), **kwargs)
    args = parser.parse_args()
    with args.base.open("rb") as base:
        if digest(base) != BASE_SHA256:
            parser.error("Expected the exact wide.74 release APK")
    if args.output.exists():
        parser.error("Choose a new output filename")
    with tempfile.TemporaryDirectory(prefix="carrot-live-layout-") as work:
        build(args, Path(work))
