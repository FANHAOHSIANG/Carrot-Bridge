"""Regression checks on the actual binary manifest, not a replacement XML fixture."""
import sys
from zipfile import ZipFile
from patch import activities, manifest, MAIN, OLD_CONFIG, NEW_CONFIG

def check(data):
    original = activities(data)
    modified = manifest(data)
    result = activities(modified)
    assert original[MAIN]['configChanges'][0] == OLD_CONFIG
    assert result[MAIN]['configChanges'][0] == NEW_CONFIG
    # Reproduce the old unhandled change, and ensure all previous bits survive.
    assert 0x200 & ~OLD_CONFIG
    assert not NEW_CONFIG & ~OLD_CONFIG & ~0x250
    for change in [0x200, 0x10, 0x40, 0x250, 0x20, 0x80, 0x100,
                   0x400, 0x800, 0x1000, 0x40000000, 0x200 | 0x400 | 0x1000]:
        assert not change & ~NEW_CONFIG, hex(change)
    # No blanket suppression: locale/MCC and direction changes still follow Android.
    for change in [0x1, 0x4, 0x2000]: assert change & ~NEW_CONFIG
    for name in original:
        for attribute, value in original[name].items():
            if name == MAIN and attribute == 'configChanges': continue
            assert result[name][attribute] == value, (name, attribute)
    assert len(modified) == len(data)
    allowed = set(range(original[MAIN]['configChanges'][1], original[MAIN]['configChanges'][1]+4))
    for marker in ['wide.76'.encode('utf-16le'), (26110788).to_bytes(4, 'little')]:
        index = data.index(marker)
        allowed.update(range(index,index+len(marker)))
    assert all(i in allowed for i,(a,b) in enumerate(zip(data,modified)) if a != b)
    print('Binary manifest: 12 handled scenarios, 3 unhandled controls, other activity attributes preserved')

if __name__ == '__main__':
    with ZipFile(sys.argv[1]) as apk: check(apk.read('AndroidManifest.xml'))
