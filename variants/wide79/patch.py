from pathlib import Path
import importlib.util

PACKAGE = 'com/navipilot/obf'
spec = importlib.util.spec_from_file_location('wide78_patch', Path(__file__).resolve().parents[1] / 'wide78/patch.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

def apply(primary):
    base.apply(primary)
    path = primary / PACKAGE / 'MG.smali'
    s = path.read_text()
    old = '    move-object/16 p2, v9'
    assert s.count(old) == 1
    s = s.replace(old, '''    invoke-static {v8, v9, v1}, Lcom/navipilot/obf/WideSharedPreAdjust;->decorate(Ljava/lang/String;Lorg/json/JSONObject;Ljava/util/Map;)Lorg/json/JSONObject;

    move-result-object v9

''' + old)
    path.write_text(s)
    path = primary / PACKAGE / 'WideVariant.smali'
    s = path.read_text()
    old = '    invoke-static/range {p0 .. p0}, Lcom/navipilot/obf/WideAmapLinkIntegration;->prepare(Landroid/content/Context;)V'
    assert s.count(old) == 1
    path.write_text(s.replace(old, old + '\n\n    invoke-static/range {p0 .. p0}, Lcom/navipilot/obf/WideSharedPreAdjust;->init(Landroid/content/Context;)V'))
    path = primary / PACKAGE / 'WideAmapSource.smali'
    s = path.read_text()
    assert 'preAdjustSource()' not in s
    path.write_text(s + '''
.method public static preAdjustSelectedAt()J
    .locals 2
    sget-wide v0, Lcom/navipilot/obf/WideAmapSource;->selectedSince:J
    return-wide v0
.end method

.method public static preAdjustSource()Ljava/lang/String;
    .locals 2
    sget-object v0, Lcom/navipilot/obf/WideAmapSource;->selected:Ljava/lang/String;
    const-string v1, "com.autonavi.amapauto"
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :phone
    const-string v0, "amap_auto"
    return-object v0
    :phone
    const-string v1, "com.autonavi.minimap"
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :google
    const-string v0, "amap_phone"
    return-object v0
    :google
    invoke-static {}, Lcom/navipilot/obf/WideGoogleNav;->selected()Z
    move-result v1
    if-eqz v1, :none
    const-string v0, "google_noo"
    return-object v0
    :none
    const-string v0, ""
    return-object v0
.end method
''')
