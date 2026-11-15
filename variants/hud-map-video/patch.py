"""Attach HUD map capture to the exact wide.73 projection and Navi v2 ABI."""
from pathlib import Path

PREFIX = "Lcom/navipilot/obf/"
HUD = PREFIX + "HudMapVideo;"
PANE = PREFIX + "WideDirect$Pane;"
SESSION = PREFIX + "WideDirect$Session;"
BASE_SHA256 = "ebb65c8f206421ec7e7752a66bc5b195a8d948aabc57d22f9868bd8348ab6830"


def once(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Unexpected wide.73 anchor: {before[:100]!r}")
    return text.replace(before, after, 1)


def method(text, marker, update):
    start = text.index(marker)
    end = text.index(".end method", start)
    return text[:start] + update(text[start:end]) + text[end:]


def apply(package: Path):
    pane = package / "WideDirect$Pane.smali"
    text = pane.read_text()
    anchor = f"    invoke-static {{p0}}, {PREFIX}WideProjectionStatus;->onFrame({PANE})V\n"
    text = once(text, anchor, anchor + f"\n    invoke-static {{p0}}, {HUD}->onFrame({PANE})V\n")
    text = method(text, ".method private stop()V", lambda body: once(
        body, "    .locals 2\n", f"    .locals 2\n\n    invoke-static {{p0}}, {HUD}->clear({PANE})V\n"))
    anchor = f"    iput-object v1, p0, {PANE}->workerSession:{SESSION}"
    text = once(text, anchor, f"    iput-object p2, v1, {SESSION}->hudMapPackage:Ljava/lang/String;\n\n" + anchor)
    anchor = "    invoke-virtual {v0}, Landroid/widget/PopupMenu;->show()V"
    text = once(text, anchor, f"""
    invoke-virtual {{v0}}, Landroid/widget/PopupMenu;->getMenu()Landroid/view/Menu;
    move-result-object v1
    invoke-static {{p0, v1}}, {HUD}->addMenu({PANE}Landroid/view/Menu;)V

{anchor}""")
    text = method(text, ".method synthetic lambda$7$", lambda body: once(
        body, "    move-result v1\n", f"""    move-result v1

    invoke-static {{p0, v1}}, {HUD}->menuClick({PANE}I)Z
    move-result v2
    if-eqz v2, :hud_map_other_item
    return v2
    :hud_map_other_item
"""))
    pane.write_text(text)
    session = package / "WideDirect$Session.smali"
    anchor = ".field volatile closed:Z"
    session.write_text(once(session.read_text(), anchor, anchor + "\n\n.field hudMapPackage:Ljava/lang/String;"))

    control = package / "XG.smali"
    text = control.read_text()
    text = once(text, '    :goto_17a\n    new-instance v5, Lcom/navipilot/obf/NW;\n\n    if-eqz v8, :cond_187\n\n    invoke-static {v6, v13}, Lcom/navipilot/obf/tv;->o(Ljava/lang/Object;Ljava/lang/Object;)Z',
                f'    :goto_17a\n    new-instance v5, Lcom/navipilot/obf/NW;\n\n    if-eqz v8, :cond_187\n\n    invoke-static {{v6, v9}}, {HUD}->handles(Ljava/lang/String;Ljava/lang/String;)Z')
    anchor = "    iput-object v12, v6, Lcom/navipilot/obf/XG;->j:Lcom/navipilot/obf/QG;"
    text = once(text, anchor, anchor + f"\n    invoke-static {{v12}}, {HUD}->prepareManifest({PREFIX}QG;)V")
    anchor = "    invoke-virtual {v6, v8, v9, v13, v12}, Lcom/navipilot/obf/XG;->m(JLcom/navipilot/obf/RG;Lcom/navipilot/obf/QG;)V"
    text = once(text, anchor, anchor + f"\n    invoke-static {{v6, v12}}, {HUD}->useManifest({PREFIX}XG;{PREFIX}QG;)V")
    anchor = "    iput-object v1, p0, Lcom/navipilot/obf/XG;->j:Lcom/navipilot/obf/QG;"
    text = once(text, anchor, anchor + f"\n    invoke-static {{p0}}, {HUD}->reset({PREFIX}XG;)V")
    text = method(text, ".method public final r(Ljava/lang/String;ZLorg/json/JSONObject;", lambda body: once(
        body, "    .locals 21\n", f"    .locals 21\n\n    invoke-static/range {{p0 .. p3}}, {HUD}->observeStatus({PREFIX}XG;Ljava/lang/String;ZLorg/json/JSONObject;)V\n"))
    control.write_text(text)

    message = package / "kO.smali"
    text = once(message.read_text(), ".field public final a:Lcom/navipilot/obf/uc;",
                ".field public final a:Lcom/navipilot/obf/uc;\n.field public final hudOpcode:I")
    text = once(text, "    .locals 0\n", f"""    .locals 1
    const/4 v0, 0x1
    invoke-direct {{p0, p1, v0}}, {PREFIX}kO;-><init>({PREFIX}uc;I)V
    return-void
.end method

.method public constructor <init>({PREFIX}uc;I)V
    .locals 0
""")
    anchor = f"    iput-object p1, p0, {PREFIX}kO;->a:{PREFIX}uc;"
    message.write_text(once(text, anchor, anchor + f"\n    iput p2, p0, {PREFIX}kO;->hudOpcode:I"))

    writer = package / "v30.smali"
    marker = f".method public final b({PREFIX}uc;)V"
    text = once(writer.read_text(), marker, f"""{marker}
    .locals 1
    const/4 v0, 0x1
    invoke-virtual {{p0, p1, v0}}, {PREFIX}v30;->b({PREFIX}uc;I)V
    return-void
.end method

.method public final b({PREFIX}uc;I)V""")
    for original, flag in (("0xc1", "0xc0"), ("0x81", "0x80")):
        text = once(text, f"    const/16 v1, {original}",
                    f"    move/from16 v1, p2\n    or-int/lit16 v1, v1, {flag}")
    writer.write_text(text)

    websocket = package / "mO.smali"
    anchor = f"    invoke-virtual {{v0, v1}}, {PREFIX}v30;->b({PREFIX}uc;)V"
    websocket.write_text(once(websocket.read_text(), anchor,
                             f"    iget v2, v5, {PREFIX}kO;->hudOpcode:I\n"
                             f"    invoke-virtual {{v0, v1, v2}}, {PREFIX}v30;->b({PREFIX}uc;I)V"))
