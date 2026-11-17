"""Feed glow after Z3.A validates either high-level Amap camera broadcast."""
from pathlib import Path

PACKAGE = Path('com/navipilot/obf')
CALL = '    invoke-static {v0}, Lcom/navipilot/obf/WideAmapCameraGlow;->updateCamera(Lcom/navipilot/obf/T4;)V'

def apply(primary):
    receiver = primary / PACKAGE / 'Z3.smali'
    text = receiver.read_text()
    old = '    invoke-static {v1, v4, v6}, Lcom/navipilot/obf/WideAmapCameraGlow;->update(III)V\n'
    anchor = '    invoke-virtual/range {v16 .. v22}, Lcom/navipilot/obf/IG;->r(Lcom/navipilot/obf/T4;JJZ)V\n'
    if text.count(old) != 1 or text.count(anchor) != 1:
        raise ValueError('Expected exact wide.75 camera receiver')
    text = text.replace(old, '')
    text = text.replace(anchor, anchor + '\n    move-object/from16 v0, v17\n' + CALL + '\n')
    receiver.write_text(text)

def verify(primary):
    text = (primary / PACKAGE / 'Z3.smali').read_text()
    def body(name):
        start = text.index('.method public final ' + name + '(')
        return text[start:text.index('.end method', start)]
    assert CALL in body('A')
    assert text.count('->updateCamera(') == 1
    assert 'WideAmapCameraGlow;->update(III)' not in text
    for method, distance, limit in [('k', 'CAMERA_DISTANCE', 'CAMERA_SPEED_LIMIT'),
                                     ('l', 'CAMERA_DIST', 'CAMERA_SPEED')]:
        code = body(method)
        assert 'Z3;->A(Landroid/content/Intent;' in code
        assert distance in code and limit in code
    source = (primary / PACKAGE / 'WideAmapSource.smali').read_text()
    assert 'WideAmapCameraGlow;->clear()V' in source
    redraw = (primary / PACKAGE / 'WideStatusBorder$1.smali').read_text()
    assert 'SystemClock;->elapsedRealtime()J' in redraw
