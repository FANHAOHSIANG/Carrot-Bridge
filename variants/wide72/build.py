"""Rebuild the tested wide.71 APK with the renamed panes and map-only layout."""
import argparse
import json
import re
import struct
import subprocess
import tempfile
from hashlib import file_digest
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
BASE = "d7753d027d3ddcefd5dfa1805eeb0789db69940617e8dd2c8e782fd577ed2143"
PANE = "Lcom/navipilot/obf/WideDirect$Pane;"
MODE = "Lcom/navipilot/obf/WideSingleProjection;"
PLAN = "Lcom/navipilot/obf/WideGeometry$Plan;"
PACKAGE = Path("com/navipilot/obf")
SIGNATURE = re.compile(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))", re.I)


def edit(path, old, new):
    data = path.read_text()
    if data.count(old) != 1:
        raise ValueError(f"Expected one patch anchor in {path.name}: {old!r}")
    path.write_text(data.replace(old, new))


def rename(directory):
    for file in directory.glob("Wide*.smali"):
        data = file.read_text()
        one = json.dumps("分區一")[1:-1]
        two = json.dumps("分區二")[1:-1]
        updated = re.sub(f"{re.escape(one)}|{re.escape(two)}",
                         lambda m: two if m[0] == one else one, data)
        updated = updated.replace("wide.71", "wide.72")
        if updated != data:
            file.write_text(updated)


def patch(primary, extras):
    for directory in (primary, extras):
        rename(directory)
    settings = primary / "WideSettings.smali"
    edit(settings, ".method public static install(Landroid/app/Activity;)V\n    .locals 8\n",
         f".method public static install(Landroid/app/Activity;)V\n    .locals 8\n\n"
         f"    invoke-static {{p0}}, {MODE}->load(Landroid/app/Activity;)V\n")
    pane = primary / "WideDirect$Pane.smali"
    anchor = f"    invoke-static {{p0}}, Lcom/navipilot/obf/WideProjectionControls;->install({PANE})V\n"
    edit(pane, anchor, anchor + f"\n    invoke-static {{p0}}, {MODE}->addMapMenu({PANE})V\n")
    anchor = "    invoke-direct {v0, v1, p1}, Landroid/widget/PopupMenu;-><init>(Landroid/content/Context;Landroid/view/View;)V\n"
    # Back is inserted first. Add the layout toggle with normal menu ordering.
    data = pane.read_text()
    start = data.index(anchor)
    end = data.index("    .line 229\n", start)
    old = data[start:end]
    edit(pane, old, old.replace(anchor, anchor +
        f"\n    invoke-static {{v0, p1}}, {MODE}->addOption(Landroid/widget/PopupMenu;Landroid/view/View;)V\n"))
    geometry = primary / "WideGeometry$Plan.smali"
    anchor = f"    iput-boolean p5, p0, {PLAN}->controls:Z\n"
    full = f"""
    sget-boolean v0, {MODE}->enabled:Z
    if-eqz v0, :split_projection
    const/4 v0, 0x0
    const/4 v1, 0x1
    iput-boolean v1, p0, {PLAN}->compact:Z
    iput-boolean v0, p0, {PLAN}->controls:Z
    iget v1, p0, {PLAN}->width:F
    iput v1, p0, {PLAN}->mapWidth:F
    iget v1, p0, {PLAN}->height:F
    iput v1, p0, {PLAN}->mapHeight:F
"""
    for field in ("sideX", "sideY", "sideWidth", "sideHeight", "shieldHeight", "controlsHeight"):
        full += f"    iput v0, p0, {PLAN}->{field}:F\n"
    edit(geometry, anchor, anchor + full + "    return-void\n\n    :split_projection\n")
    for cls, signature, count in (
        ("WideLayout", "controlsVisible()Z", 1),
        ("WideDirect", "shield(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;", 8),
    ):
        anchor = f".method public static {signature}\n    .locals {count}\n"
        edit(primary / f"{cls}.smali", anchor, anchor + f"""
    sget-boolean v0, {MODE}->enabled:Z
    if-eqz v0, :split_projection
    const/4 v0, 0x0
    {"return v0" if cls == "WideLayout" else "return-object v0"}
    :split_projection
""")


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def build(base, tools, apktool, destination, work):
    sdk = tools / "android-15"
    dalvik = ("java", "-cp", apktool, HERE.parent / "wide69/Dalvik.java")
    parts = {"classes.dex": work / "primary", "classes8.dex": work / "extras"}
    with ZipFile(base) as source:
        for name, directory in parts.items():
            path = work / name
            path.write_bytes(source.read(name))
            run(*dalvik, "decode", path, directory)
    patch(*(directory / PACKAGE for directory in parts.values()))
    android = tools / "android.jar"
    javac = ("java", "-m", "jdk.compiler/com.sun.tools.javac.Main", "-source", "17", "-target", "17", "-Xlint:-options", "-encoding", "UTF-8")
    stubs, classes, dex = (work / name for name in ("stubs", "compiled", "dex"))
    dex.mkdir()
    run(*javac, "-cp", android, "-d", stubs, HERE / "ProjectionApi.java")
    run(*javac, "-cp", f"{android}:{stubs}", "-d", classes, HERE / "WideSingleProjection.java")
    run("java", "-cp", sdk / "lib/d8.jar", "com.android.tools.r8.D8", "--min-api", 31,
        "--lib", android, "--classpath", stubs, "--output", dex, *classes.rglob("*.class"))
    run(*dalvik, "decode", dex / "classes.dex", parts["classes8.dex"])
    changes = {}
    for name, directory in parts.items():
        path = work / ("updated-" + name)
        run(*dalvik, "assemble", directory, path)
        changes[name] = path.read_bytes()
    unaligned = work / "unaligned.apk"
    aligned = work / "aligned.apk"
    with ZipFile(base) as source, ZipFile(unaligned, "w") as apk:
        manifest = source.read("AndroidManifest.xml")
        for old, new in ((b"w\0i\0d\0e\0.\x007\x001\0", "wide.72".encode("utf-16le")),
                         (struct.pack("<I", 26110783), struct.pack("<I", 26110784))):
            if manifest.count(old) != 1:
                raise ValueError("Unexpected base manifest")
            manifest = manifest.replace(old, new)
        changes["AndroidManifest.xml"] = manifest
        for entry in source.infolist():
            if not SIGNATURE.fullmatch(entry.filename):
                apk.writestr(entry, changes.get(entry.filename, source.read(entry)))
    run(sdk / "zipalign", "-P", 16, "-f", 4, unaligned, aligned)
    run(sdk / "zipalign", "-P", 16, "-c", 4, aligned)
    with ZipFile(base) as source, ZipFile(aligned) as apk:
        assert apk.testzip() is None
        assert set(apk.namelist()) == {n for n in source.namelist() if not SIGNATURE.fullmatch(n)}
        assert {n for n in apk.namelist() if apk.read(n) != source.read(n)} == changes.keys()
    with destination.open("xb") as target:
        target.write(aligned.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "tools", "apktool", "destination"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    with args.base.open("rb") as source:
        if file_digest(source, "sha256").hexdigest() != BASE:
            parser.error("Use the tested, signed wide.71 base")
    with tempfile.TemporaryDirectory(prefix="bridge-wide72-") as temp:
        build(args.base, args.tools, args.apktool, args.destination, Path(temp))
