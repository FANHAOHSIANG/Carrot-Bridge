"""Add only display observation hooks to the exact wide.88 APK. Fail on unexpected bytecode."""
import re
P="Lcom/navipilot/obf/WideLaneLive;"
def entry(path,signature,call):
    s=path.read_text()
    rx=re.compile(r"(?ms)^\.method [^\n]* "+re.escape(signature)+r"\n(.*?)^\.end method")
    hits=list(rx.finditer(s))
    assert len(hits)==1,(path,signature,len(hits))
    m=hits[0];body=m.group(1)
    first=re.search(r"(?m)^    [a-z][a-z0-9/-]*(?:\s|$)",body)
    assert first and call not in body,(path,signature)
    pos=m.start(1)+first.start()
    path.write_text(s[:pos]+"    "+call+"\n\n"+s[pos:])
def apply(pkg):
    entry(pkg/"WideAmapSource.smali","select(Ljava/lang/String;)V","invoke-static/range {p0 .. p0}, "+P+"->select(Ljava/lang/String;)V")
    n=pkg/"WideAmapLinkNavigation.smali"
    entry(n,"reset(J)V","invoke-static/range {p1 .. p2}, "+P+"->reset(J)V")
    entry(n,"invalidate()V","invoke-static {}, "+P+"->invalidate()V")
    entry(n,"accept(JILorg/json/JSONObject;JJ)Z","invoke-static/range {p1 .. p8}, "+P+"->link(JILorg/json/JSONObject;JJ)V")
    p=pkg/"MG.smali";s=p.read_text()
    anchor="    move-object/16 p2, v9"
    assert s.count(anchor)==1,"unexpected Navi v2 serialization anchor"
    call="    invoke-static {v8, v9, v1}, "+P+"->decorate(Ljava/lang/String;Lorg/json/JSONObject;Ljava/util/Map;)Lorg/json/JSONObject;\n\n    move-result-object v9\n\n"
    p.write_text(s.replace(anchor,call+anchor,1))
