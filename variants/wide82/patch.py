"""Extend the existing Amap Auto receiver; do not modify vehicle-control fields."""
from pathlib import Path
import importlib.util
import re

PACKAGE = "com/navipilot/obf"
BASE = Path(__file__).resolve().parents[1] / "wide81/patch.py"
_spec = importlib.util.spec_from_file_location("wide81_base", BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
CAPTURE = "    invoke-static/range {p1 .. p1}, Lcom/navipilot/obf/WideAmapExitInfo;->capture(Landroid/content/Intent;)V"
DECORATE = "    invoke-static {v8, v9, v1}, Lcom/navipilot/obf/WideAmapExitInfo;->decorate(Ljava/lang/String;Lorg/json/JSONObject;Ljava/util/Map;)Lorg/json/JSONObject;"

def apply(primary: Path) -> None:
    _base.apply(primary)
    path=primary/PACKAGE/"Z3.smali"
    text=path.read_text()
    headers=list(re.finditer(r"(?m)^\.method public final l\(Landroid/content/Intent;[^\n]*\)V$",text))
    if len(headers)!=1:
        raise ValueError("Expected unique instance Amap Auto guidance handler with Intent first")
    h=headers[0]
    end=text.index(".end method",h.end())
    body=text[h.end():end]
    if "CAMERA_DIST" not in body or "CAMERA_SPEED" not in body:
        raise ValueError("Unexpected Amap guidance handler")
    # Insert immediately before the first executable instruction, after register/debug directives.
    first=re.search(r"(?m)^    [a-z][a-z0-9/-]*(?:\s|$)",body)
    if first is None or CAPTURE in body:
        raise ValueError("Missing first receiver instruction or duplicate hook")
    at=h.end()+first.start()
    path.write_text(text[:at]+CAPTURE+"\n\n"+text[at:])
    path=primary/PACKAGE/"MG.smali"
    text=path.read_text()
    anchor="    move-object/16 p2, v9"
    if text.count(anchor)!=1 or DECORATE in text:
        raise ValueError("Unexpected Navi v2 serialization hook")
    path.write_text(text.replace(anchor,DECORATE+"\n\n    move-result-object v9\n\n"+anchor))
