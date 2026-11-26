"""Add a one-shot launch-time projection handshake on top of wide.79.

The existing navigation and side-panel preferences remain the source of truth.
This hook does not override selected apps or bypass Android authorization. It
uses the existing 'Start projection' callback once if a projection manager is
already connected; the existing poller handles services that become ready later.
"""
from pathlib import Path
import importlib.util
import re

PACKAGE = 'com/navipilot/obf'
BASE = Path(__file__).resolve().parents[1] / 'wide79/patch.py'
_spec = importlib.util.spec_from_file_location('wide79_projection_patch', BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

HOOK = '''
    # wide80: restore the previously selected map and side app on Activity startup.
    iget-boolean v0, p0, Lcom/navipilot/obf/WideDirect$Pane;->shield:Z
    if-nez v0, :wide80_auto_restore_done
    invoke-static {}, Lcom/navipilot/obf/WideDirect;->projectionReady()Z
    move-result v0
    if-nez v0, :wide80_auto_restore_done
    invoke-static {}, Lcom/navipilot/obf/WideProjectionHelp;->connected()Z
    move-result v0
    if-eqz v0, :wide80_auto_restore_done
    iget-object v1, p0, Lcom/navipilot/obf/WideDirect$Pane;->start:Lcom/navipilot/obf/tr;
    if-eqz v1, :wide80_auto_restore_done
    invoke-virtual {p0}, Landroid/view/View;->getContext()Landroid/content/Context;
    move-result-object v0
    invoke-static {v0}, Lcom/navipilot/obf/WideVariant;->activity(Landroid/content/Context;)Landroid/app/Activity;
    move-result-object v0
    if-eqz v0, :wide80_auto_restore_done
    invoke-static {v0, v1}, Lcom/navipilot/obf/WideProjectionHelp;->start(Landroid/app/Activity;Lcom/navipilot/obf/tr;)V
    :wide80_auto_restore_done
'''


def auto_restore(primary: Path) -> None:
    pane = primary / PACKAGE / 'WideDirect$Pane.smali'
    source = pane.read_text()
    header = re.search(r'(?m)^\.method\s+[^\n]*\bonAttachedToWindow\(\)V\s*$', source)
    if not header:
        raise ValueError('Expected live projection pane attachment')
    end = source.find('.end method', header.end())
    if end < 0:
        raise ValueError('Malformed pane attachment')
    body = source[header.start():end]
    if 'wide80_auto_restore_done' in body:
        raise ValueError('Auto-restore already installed')
    if body.count('    return-void') != 1 or '->startIfNeeded()V' not in body:
        raise ValueError('Unexpected pane startup: refusing unsafe patch')
    registers = re.search(r'(?m)^\s*\.(registers|locals)\s+(\d+)\s*$', body)
    if not registers:
        raise ValueError('Missing register declaration')
    count = int(registers.group(2))
    needed = 3 if registers.group(1) == 'registers' else 2
    if count < needed:
        # Existing p0 is referenced via the p register alias. Refuse if an
        # existing v1 could alias p0 before expanding the local register set.
        if re.search(r'\bv1\b', body):
            raise ValueError('Cannot safely expand register allocation')
        body = body[:registers.start(2)] + str(needed) + body[registers.end(2):]
    body = body.replace('    return-void', HOOK + '\n    return-void', 1)
    pane.write_text(source[:header.start()] + body + source[end:])


def apply(primary: Path) -> None:
    _base.apply(primary)
    auto_restore(primary)
