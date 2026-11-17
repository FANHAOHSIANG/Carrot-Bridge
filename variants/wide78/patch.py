from pathlib import Path

PACKAGE = 'com/navipilot/obf'

def apply(primary):
    path = primary / PACKAGE / 'MG.smali'
    text = path.read_text()
    old = '    invoke-static {v2, v3}, Lcom/navipilot/obf/WideAmapPreAdjust;->mark(Lorg/json/JSONObject;Ljava/lang/Integer;)Lorg/json/JSONObject;'
    new = '''    iget-object v4, v14, Lcom/navipilot/obf/HG;->k:Lcom/navipilot/obf/R4;

    invoke-static {v2, v3, v4}, Lcom/navipilot/obf/WideAmapPreAdjust;->mark(Lorg/json/JSONObject;Ljava/lang/Integer;Lcom/navipilot/obf/R4;)Lorg/json/JSONObject;'''
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    path = primary / PACKAGE / 'WideAmapSource.smali'
    text = path.read_text()
    assert 'preAdjustAllowed' not in text
    path.write_text(text + '''
.method public static preAdjustAllowed(J)Z
    .locals 3
    sget-boolean v0, Lcom/navipilot/obf/WideAmapSource;->ready:Z
    if-eqz v0, :reject_pre
    sget-object v0, Lcom/navipilot/obf/WideAmapSource;->selected:Ljava/lang/String;
    const-string v1, "com.autonavi.amapauto"
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :reject_pre
    sget-wide v0, Lcom/navipilot/obf/WideAmapSource;->selectedSince:J
    cmp-long v2, p0, v0
    if-ltz v2, :reject_pre
    const/4 v0, 0x1
    return v0
    :reject_pre
    const/4 v0, 0x0
    return v0
.end method
''')
