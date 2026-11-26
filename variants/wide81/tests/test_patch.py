"""Host-only structural tests for one-shot Shizuku/Stellar consent and reconnect policy."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

script = Path(__file__).resolve().parents[1] / "patch.py"
spec = importlib.util.spec_from_file_location("bridge81", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SAMPLE = """.class public Lcom/navipilot/obf/WideReconnectPolicy;
.super Ljava/lang/Object;
.field private managerOpened:Z
.field private wasReady:Z
.field private attempts:I
.method public decide(JZZZZZZ)I
    .locals 1
    const/4 v0, 0x0
    :cond_4
    iget-boolean p3, p0, Lcom/navipilot/obf/WideReconnectPolicy;->wasReady:Z
    if-eq p4, p3, :cond_d
    invoke-virtual {p0}, Lcom/navipilot/obf/WideReconnectPolicy;->retry()V
    iput-boolean p4, p0, Lcom/navipilot/obf/WideReconnectPolicy;->wasReady:Z
    :cond_d
    if-eqz p6, :cond_13
    invoke-virtual {p0}, Lcom/navipilot/obf/WideReconnectPolicy;->retry()V
    return v0
    :cond_13

    const/4 p3, 0x1
    if-eqz p4, :cond_32
    if-eqz p5, :cond_3b
    if-eqz p7, :cond_3b
    iget p4, p0, Lcom/navipilot/obf/WideReconnectPolicy;->attempts:I
    const/4 p5, 0x5
    if-ge p4, p5, :cond_3b
    const/4 p1, 0x2
    return p1
    :cond_32
    if-eqz p8, :cond_3b
    iget-boolean p1, p0, Lcom/navipilot/obf/WideReconnectPolicy;->managerOpened:Z
    :cond_3b
    return v0
.end method
"""

with TemporaryDirectory(prefix="wide81-regression-") as tmp:
    base = Path(tmp)
    target = base / mod.PACKAGE / "WideReconnectPolicy.smali"
    target.parent.mkdir(parents=True)
    target.write_text(SAMPLE)
    mod.auto_consent_request(base)
    text = target.read_text()
    assert text.count(".field private permissionRequested:Z") == 1
    assert text.count("->permissionRequested:Z") == 3
    assert "iput-boolean p3, p0, Lcom/navipilot/obf/WideReconnectPolicy;->wasReady:Z" not in text
    assert "if-eqz p4, :wide81_normal_authorized_reconnect" in text
    assert "if-nez p5, :wide81_normal_authorized_reconnect" in text
    assert "if-eqz p7, :wide81_normal_authorized_reconnect" in text
    assert "if-eqz p8, :wide81_normal_authorized_reconnect" in text
    assert "if-nez p3, :wide81_normal_authorized_reconnect" in text
    assert "return p3" in text
    assert "if-eqz p5, :cond_3b" in text  # original authorized reconnect retained
    try: mod.auto_consent_request(base)
    except ValueError: pass
    else: raise AssertionError("Double patch must be rejected")
    target.write_text(SAMPLE.replace("if-eqz p8", "if-eqz v0"))
    try: mod.auto_consent_request(base)
    except ValueError: pass
    else: raise AssertionError("Unknown reconnect path must be rejected")

print("PASS: request consent once after manager appears; preserve 5-try authorized reconnect")
