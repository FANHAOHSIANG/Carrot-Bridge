"""Host-only structural regression for the auto-resume hook (not a device test)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

p = Path(__file__).resolve().parents[1] / 'patch.py'
spec = importlib.util.spec_from_file_location('bridge80_patch', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    file = root / mod.PACKAGE / 'WideDirect$Pane.smali'
    file.parent.mkdir(parents=True)
    sample = '''.class Lcom/navipilot/obf/WideDirect$Pane;
.method protected onAttachedToWindow()V
    .registers 2
    invoke-super {p0}, Landroid/widget/LinearLayout;->onAttachedToWindow()V
    invoke-direct {p0}, Lcom/navipilot/obf/WideDirect$Pane;->startIfNeeded()V
    return-void
.end method
'''
    file.write_text(sample)
    mod.auto_restore(root)
    patched = file.read_text()
    assert '    .registers 3' in patched
    assert patched.count('WideProjectionHelp;->start(') == 1
    assert 'WideDirect;->projectionReady()Z' in patched
    assert 'WideProjectionHelp;->connected()Z' in patched
    assert '->shield:Z' in patched
    assert '->start:Lcom/navipilot/obf/tr;' in patched
    assert ':wide80_auto_restore_done' in patched
    assert patched.count('    return-void') == 1
    try:
        mod.auto_restore(root)
    except ValueError:
        pass
    else:
        raise AssertionError('Double injection must fail closed')
    file.write_text(sample.replace('->startIfNeeded()V', '->unknown()V'))
    try:
        mod.auto_restore(root)
    except ValueError:
        pass
    else:
        raise AssertionError('Unexpected attachment must fail closed')

print('PASS: auto-resume guards and fail-closed patch checks')
