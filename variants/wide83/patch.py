"""Restore the existing projection callback on visible pane startup and focus.

Uses the shared WideProjectionHelp poller and its existing permission/retry policy.
Never grants permission or creates a second projection session.
"""
from pathlib import Path
import importlib.util
import re

PACKAGE = "com/navipilot/obf"
BASE = Path(__file__).resolve().parents[1] / "wide82/patch.py"
_spec = importlib.util.spec_from_file_location("wide82_base", BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

ATTACH = """    iget-boolean v0, p0, Lcom/navipilot/obf/WideDirect$Pane;->shield:Z

    if-nez v0, :cond_17

    invoke-virtual {p0}, Lcom/navipilot/obf/WideDirect$Pane;->getContext()Landroid/content/Context;

    move-result-object v0

    invoke-static {v0}, Lcom/navipilot/obf/WideDirect;->access$1(Landroid/content/Context;)Landroid/app/Activity;

    move-result-object v0

    iget-object v1, p0, Lcom/navipilot/obf/WideDirect$Pane;->start:Lcom/navipilot/obf/tr;

    invoke-static {v0, v1}, Lcom/navipilot/obf/WideProjectionHelp;->attach(Landroid/app/Activity;Lcom/navipilot/obf/tr;)V"""

WAIT = """    iget-boolean v0, v5, Lcom/navipilot/obf/WideDirect$Pane;->shield:Z

    if-nez v0, :cond_13b

    invoke-virtual {p0}, Lcom/navipilot/obf/WideDirect$Pane;->getContext()Landroid/content/Context;

    move-result-object v0

    invoke-static {v0}, Lcom/navipilot/obf/WideDirect;->access$1(Landroid/content/Context;)Landroid/app/Activity;

    move-result-object v0

    iget-object v1, v5, Lcom/navipilot/obf/WideDirect$Pane;->start:Lcom/navipilot/obf/tr;

    invoke-static {v0, v1}, Lcom/navipilot/obf/WideProjectionHelp;->attach(Landroid/app/Activity;Lcom/navipilot/obf/tr;)V"""

AUTO = """    invoke-direct {p0}, Lcom/navipilot/obf/WideDirect$Pane;->wide83AutoAttach()V"""

PANE = """
.method private wide83AutoAttach()V
    .locals 3
    iget-boolean v0, p0, Lcom/navipilot/obf/WideDirect$Pane;->attached:Z
    if-eqz v0, :done
    iget-boolean v0, p0, Lcom/navipilot/obf/WideDirect$Pane;->disposed:Z
    if-nez v0, :done
    invoke-static {}, Lcom/navipilot/obf/WideDirect;->projectionReady()Z
    move-result v0
    if-nez v0, :done
    iget-object v1, p0, Lcom/navipilot/obf/WideDirect$Pane;->start:Lcom/navipilot/obf/tr;
    if-eqz v1, :done
    invoke-virtual {p0}, Lcom/navipilot/obf/WideDirect$Pane;->getContext()Landroid/content/Context;
    move-result-object v0
    iget-boolean v2, p0, Lcom/navipilot/obf/WideDirect$Pane;->shield:Z
    if-eqz v2, :active
    invoke-static {v0}, Lcom/navipilot/obf/WidePanels;->sidePackage(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v2
    if-eqz v2, :done
    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z
    move-result v2
    if-nez v2, :done
    :active
    invoke-static {v0}, Lcom/navipilot/obf/WideDirect;->access$1(Landroid/content/Context;)Landroid/app/Activity;
    move-result-object v0
    if-eqz v0, :done
    invoke-virtual {v0}, Landroid/app/Activity;->isFinishing()Z
    move-result v2
    if-nez v2, :done
    invoke-virtual {v0}, Landroid/app/Activity;->isDestroyed()Z
    move-result v2
    if-nez v2, :done
    invoke-static {v0, v1}, Lcom/navipilot/obf/WideProjectionHelp;->attach(Landroid/app/Activity;Lcom/navipilot/obf/tr;)V
    invoke-virtual {v0}, Landroid/app/Activity;->hasWindowFocus()Z
    move-result v2
    if-eqz v2, :done
    invoke-static {}, Lcom/navipilot/obf/WideProjectionHelp;->wide83Kick()V
    :done
    return-void
.end method

.method public onWindowFocusChanged(Z)V
    .locals 0
    invoke-super {p0, p1}, Landroid/widget/LinearLayout;->onWindowFocusChanged(Z)V
    if-eqz p1, :done
    invoke-direct {p0}, Lcom/navipilot/obf/WideDirect$Pane;->wide83AutoAttach()V
    :done
    return-void
.end method
"""

HELP = """
.method static wide83Kick()V
    .locals 3
    # Both panes share the original poll and policy. Coalesce, never reset attempts.
    sget-object v0, Lcom/navipilot/obf/WideProjectionHelp;->main:Landroid/os/Handler;
    sget-object v1, Lcom/navipilot/obf/WideProjectionHelp;->poll:Ljava/lang/Runnable;
    invoke-virtual {v0, v1}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    const/4 v2, 0x1
    sput-boolean v2, Lcom/navipilot/obf/WideProjectionHelp;->running:Z
    invoke-virtual {v0, v1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z
    move-result v2
    if-nez v2, :done
    const/4 v2, 0x0
    sput-boolean v2, Lcom/navipilot/obf/WideProjectionHelp;->running:Z
    :done
    return-void
.end method
"""

def _replace_block(text, signature, old, new):
    m = re.search(r"(?m)^\.method [^\n]*" + re.escape(signature) + r"$", text)
    if not m:
        raise ValueError("Missing pinned method " + signature)
    end = text.index(".end method", m.end())
    body = text[m.start():end]
    # Allow debug directives between exact original instructions.
    lines = old.splitlines()
    pattern = r"\n(?:[ \t]*\n|[ \t]*\.line \d+\n)*".join(re.escape(line) for line in lines if line.strip())
    matches = list(re.finditer(pattern, body))
    if len(matches) != 1:
        raise ValueError("Unexpected original callback path " + signature)
    match = matches[0]
    return text[:m.start()] + body[:match.start()] + new + body[match.end():] + text[end:]

def restore_projection(primary):
    pane = primary / PACKAGE / "WideDirect$Pane.smali"
    help_file = primary / PACKAGE / "WideProjectionHelp.smali"
    p, h = pane.read_text(), help_file.read_text()
    if "wide83AutoAttach" in p or "wide83Kick" in h or re.search(r"(?m)^\.method .*onWindowFocusChanged\(Z\)V$",p):
        raise ValueError("Unexpected existing projection lifecycle hook")
    if "->retry()V" not in h or '->schedule()V' not in h or '->postDelayed(Ljava/lang/Runnable;J)Z' not in h:
        raise ValueError("Original reconnect scheduler missing")
    p = _replace_block(p, "onAttachedToWindow()V", ATTACH, AUTO)
    p = _replace_block(p, "startIfNeeded()V", WAIT, AUTO)
    pane.write_text(p + "\n" + PANE)
    help_file.write_text(h + "\n" + HELP)

def apply(primary):
    _base.apply(primary)
    restore_projection(primary)
