"""Full auto-start for an already authorized Shizuku/Stellar session, plus one user-visible permission request.

The wide.80 onAttachedToWindow hook only acts if the manager is already connected.
The original WideProjectionHelp poll already reconnects when authorized. Extend the
existing policy so it requests user consent ONCE after a late manager connection.
Never auto-grant permission, bypass the Android approval UI, or spam prompts.
"""
from pathlib import Path
import importlib.util
import re

PACKAGE = "com/navipilot/obf"
BASE = Path(__file__).resolve().parents[1] / "wide79/patch.py"
_spec = importlib.util.spec_from_file_location("wide79_automatic", BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

FIELD = ".field private permissionRequested:Z"

SERVICE_CHANGE = """    iput-boolean p4, p0, Lcom/navipilot/obf/WideReconnectPolicy;->wasReady:Z"""
SERVICE_RESET = SERVICE_CHANGE + """

    # wide81: reset the one-shot prompt only on real service state transitions.
    const/4 p3, 0x0
    iput-boolean p3, p0, Lcom/navipilot/obf/WideReconnectPolicy;->permissionRequested:Z"""

DECISION_START = """    :cond_13
"""
DECISION_NEW = """    :cond_13

    # wide81: the manager is alive but permission has not been granted.
    # Invoke the existing Start callback ONCE to let Shizuku/Stellar display
    # its normal user-controlled authorization request. Do not repeat after
    # denial, and do not attempt while the app is in the background.
    if-eqz p4, :wide81_normal_authorized_reconnect
    if-nez p5, :wide81_normal_authorized_reconnect
    if-eqz p7, :wide81_normal_authorized_reconnect
    if-eqz p8, :wide81_normal_authorized_reconnect
    iget-boolean p3, p0, Lcom/navipilot/obf/WideReconnectPolicy;->permissionRequested:Z
    if-nez p3, :wide81_normal_authorized_reconnect
    const/4 p3, 0x1
    iput-boolean p3, p0, Lcom/navipilot/obf/WideReconnectPolicy;->permissionRequested:Z
    const/4 p3, 0x2
    return p3
    :wide81_normal_authorized_reconnect
"""


def auto_consent_request(primary: Path) -> None:
    path = primary / PACKAGE / "WideReconnectPolicy.smali"
    data = path.read_text()
    if "permissionRequested:Z" in data:
        raise ValueError("Auto permission logic already installed")
    if data.count(".field private managerOpened:Z") != 1:
        raise ValueError("Missing expected manager state field")
    data = data.replace(".field private managerOpened:Z",
                        ".field private managerOpened:Z\n" + FIELD, 1)
    header = re.search(r"(?m)^\.method public decide\(JZZZZZZ\)I$", data)
    if not header:
        raise ValueError("Unrecognized reconnection policy signature")
    end = data.find(".end method", header.end())
    if end < 0:
        raise ValueError("Malformed reconnection policy")
    method = data[header.start():end]
    if method.count(SERVICE_CHANGE) != 1:
        raise ValueError("Missing exact manager transition code")
    if method.count(DECISION_START) != 1:
        raise ValueError("Missing exact authorization decision code")
    if "if-eqz p8" not in method or "if-eqz p7" not in method:
        raise ValueError("Expected auto-start and callback guards are missing")
    method = method.replace(SERVICE_CHANGE, SERVICE_RESET, 1)
    method = method.replace(DECISION_START, DECISION_NEW, 1)
    path.write_text(data[:header.start()] + method + data[end:])


def apply(primary: Path) -> None:
    _base.apply(primary)
    auto_consent_request(primary)
