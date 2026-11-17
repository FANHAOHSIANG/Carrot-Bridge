"""Targeted binary manifest edit; preserves all unrelated resource IDs and bytes."""
from pathlib import Path
import struct

MAIN = 'com.jixiexiaoge.drivingassist.MainActivity'
OLD_CONFIG = 0x40001da0
NEW_CONFIG = OLD_CONFIG | 0x200 | 0x10 | 0x40  # uiMode, keyboard, navigation
ANDROID = 'http://schemas.android.com/apk/res/android'

def u32(data, at): return struct.unpack_from('<I', data, at)[0]

def strings(data, start):
    _, header, _ = struct.unpack_from('<HHI', data, start)
    count, _, flags, offset, _ = struct.unpack_from('<5I', data, start + 8)
    values = []
    def length(at, utf8):
        n = data[at] if utf8 else struct.unpack_from('<H', data, at)[0]
        size, high = (1, 0x80) if utf8 else (2, 0x8000)
        at += size
        if n & high:
            extra = data[at] if utf8 else struct.unpack_from('<H', data, at)[0]
            n = ((n & (high - 1)) << (8 if utf8 else 16)) | extra
            at += size
        return n, at
    for i in range(count):
        at = start + offset + u32(data, start + header + 4 * i)
        n, at = length(at, bool(flags & 0x100))
        if flags & 0x100:
            n, at = length(at, True)
            values.append(data[at:at+n].decode('utf-8'))
        else:
            values.append(data[at:at+2*n].decode('utf-16le'))
    return values

def activities(data):
    kind, header, size = struct.unpack_from('<HHI', data)
    if kind != 3 or size != len(data): raise ValueError('Expected binary Android XML')
    at, pool, result = header, None, {}
    while at < size:
        kind, head, count = struct.unpack_from('<HHI', data, at)
        if count < head or count < 8 or at + count > size: raise ValueError('Bad chunk')
        if kind == 1:
            pool = strings(data, at)
        elif kind == 0x102 and pool[u32(data, at + 20)] == 'activity':
            attr_start, attr_size, attr_count = struct.unpack_from('<HHH', data, at + 24)
            attrs = {}
            for i in range(attr_count):
                pos = at + 16 + attr_start + i * attr_size
                ns, name = struct.unpack_from('<II', data, pos)
                if ns == 0xffffffff or pool[ns] != ANDROID: continue
                typ, value = data[pos + 15], u32(data, pos + 16)
                attrs[pool[name]] = (pool[value] if typ == 3 else value, pos + 16, typ)
            result[attrs['name'][0]] = attrs
        at += count
    return result

def manifest(data):
    activity = activities(data)[MAIN]
    value, offset, typ = activity['configChanges']
    if value != OLD_CONFIG or typ not in (0x10, 0x11):
        raise ValueError('Expected wide.76 main activity configuration flags')
    out = bytearray(data)
    struct.pack_into('<I', out, offset, NEW_CONFIG)
    for old, new in [('wide.76'.encode('utf-16le'), 'wide.77'.encode('utf-16le')),
                     (struct.pack('<I', 26110788), struct.pack('<I', 26110789))]:
        if out.count(old) != 1: raise ValueError('Unexpected version encoding')
        out = out.replace(old, new)
    return bytes(out)

def side_selection(primary):
    path = primary / 'com/navipilot/obf/WidePanels.smali'
    data = path.read_text()
    anchor = '.method static synthetic lambda$1(Landroid/app/Activity;Ljava/util/ArrayList;Landroid/content/DialogInterface;I)V\n    .locals 0\n'
    if data.count(anchor) != 1: raise ValueError('Expected wide.76 side picker')
    new = anchor.replace('.locals 0', '.locals 2') + '''
    invoke-virtual {p1, p3}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/String;
    invoke-static {p0}, Lcom/navipilot/obf/WidePanels;->sidePackage(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v0
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :selection_changed
    invoke-interface {p2}, Landroid/content/DialogInterface;->dismiss()V
    return-void
    :selection_changed
'''
    path.write_text(data.replace(anchor, new))
