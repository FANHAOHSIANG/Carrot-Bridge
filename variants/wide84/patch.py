"""Preserve the exact wide83 auto-projection and Amap metadata injection."""
from pathlib import Path
import importlib.util
_spec=importlib.util.spec_from_file_location("wide83_base",Path(__file__).resolve().parents[1]/"wide83/patch.py")
_base=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
PACKAGE=_base.PACKAGE
apply=_base.apply
