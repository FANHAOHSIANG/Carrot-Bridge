"""Patch the exact wide.74 layout toggle to recompose without Activity.recreate."""
from pathlib import Path

PACKAGE = Path("com/navipilot/obf")
MODE = "Lcom/navipilot/obf/WideSingleProjection;"
TAG = "carrot.bridge.map-only-menu"


def replace(path, before, after):
    source = path.read_text()
    if source.count(before) != 1:
        raise ValueError(f"Unexpected wide.74 anchor in {path.name}: {before!r}")
    path.write_text(source.replace(before, after))


def apply(primary, extras):
    menu = extras / PACKAGE / "WideSingleProjection.smali"
    # Snapshot state lets both the map and side-pane composition observe the same toggle.
    replace(menu, ".field static enabled:Z", """
.field private static final layoutMode:Lcom/navipilot/obf/pK;

.method static constructor <clinit>()V
    .locals 2
    sget-object v0, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;
    sget-object v1, Lcom/navipilot/obf/bT;->k:Lcom/navipilot/obf/bT;
    invoke-static {v0, v1}, Lcom/navipilot/obf/GS;->f(Ljava/lang/Object;Lcom/navipilot/obf/KV;)Lcom/navipilot/obf/pK;
    move-result-object v0
    sput-object v0, Lcom/navipilot/obf/WideSingleProjection;->layoutMode:Lcom/navipilot/obf/pK;
    return-void
.end method

.method static enabled()Z
    .locals 1
    sget-object v0, Lcom/navipilot/obf/WideSingleProjection;->layoutMode:Lcom/navipilot/obf/pK;
    invoke-virtual {v0}, Lcom/navipilot/obf/pK;->getValue()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Ljava/lang/Boolean;
    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z
    move-result v0
    return v0
.end method

.method static setEnabled(Z)V
    .locals 1
    invoke-static {p0}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object p0
    sget-object v0, Lcom/navipilot/obf/WideSingleProjection;->layoutMode:Lcom/navipilot/obf/pK;
    invoke-virtual {v0, p0}, Lcom/navipilot/obf/pK;->setValue(Ljava/lang/Object;)V
    return-void
.end method

.method private static syncMapMenu(Landroid/view/View;)V
    .locals 1
    invoke-static {}, Lcom/navipilot/obf/WideSingleProjection;->enabled()Z
    move-result v0
    if-nez v0, :show
    const/16 v0, 0x8
    goto :apply
    :show
    const/4 v0, 0x0
    :apply
    invoke-virtual {p0, v0}, Landroid/view/View;->setVisibility(I)V
    return-void
.end method
""")
    # Install the recovery menu once with the map view and toggle only its visibility.
    replace(menu, f"""    sget-boolean v0, {MODE}->enabled:Z

    if-eqz v0, :cond_5a

    iget-boolean""", "    iget-boolean")
    replace(menu, """    .line 39
    const-string""", f"""    const-string v1, "{TAG}"
    invoke-virtual {{v0, v1}}, Landroid/view/View;->setTag(Ljava/lang/Object;)V
    invoke-static {{v0}}, {MODE}->syncMapMenu(Landroid/view/View;)V

    .line 39
    const-string""")
    replace(menu, "    invoke-virtual {p0}, Landroid/app/Activity;->recreate()V", f"""
    invoke-static {{v1}}, {MODE}->setEnabled(Z)V
    invoke-virtual {{p0}}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v1
    invoke-virtual {{v1}}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v1
    const-string v2, "{TAG}"
    invoke-virtual {{v1, v2}}, Landroid/view/View;->findViewWithTag(Ljava/lang/Object;)Landroid/view/View;
    move-result-object v1
    if-eqz v1, :cond_34
    invoke-static {{v1}}, {MODE}->syncMapMenu(Landroid/view/View;)V""")
    replace(menu, f"    sput-boolean p0, {MODE}->enabled:Z",
            f"    invoke-static {{p0}}, {MODE}->setEnabled(Z)V")
    for name in ("WideLayout", "WideGeometry$Plan", "WideDirect", "WideSingleProjection"):
        directory = extras if name == "WideSingleProjection" else primary
        path = directory / PACKAGE / (name + ".smali")
        for register in (("v0", "v1") if path == menu else ("v0",)):
            replace(path, f"    sget-boolean {register}, {MODE}->enabled:Z",
                    f"    invoke-static {{}}, {MODE}->enabled()Z\n    move-result {register}")
