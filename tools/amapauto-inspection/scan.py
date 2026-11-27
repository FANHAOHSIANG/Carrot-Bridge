import hashlib, zipfile, re, struct, collections, sys
from pathlib import Path
p=Path(sys.argv[1])
print("APK size",p.stat().st_size,"SHA256",hashlib.file_digest(p.open("rb"),"sha256").hexdigest())
groups={
"route":r"routepolyline|routegeometry|routepoint|routepath|routecoord|route.?shape|linkinfo|segmentinfo|pathpoint|navi.?path|route.?data|route.?line|route.?info",
"lane":r"lanecenter|lane.?boundary|lane.?match|lane.?connect|lane.?width|lane.?geometry|lane.?polyline|lane.?loc|lane.?guid|optimal.?lane|front.?lane|back.?lane|lane.?count|lane.?info|extension.?lane|locplane",
"horizon":r"electronic.?horizon|ehorizon|e.?horizon|adasis|adas.?horizon|adas.?data|road.?curvature|ahead.?curvature|high.?precision|high.?freq.?loc|hd.?lane|hd.?map",
"ipc":r"EXTRA_DRIVE_WAY|CUR_SEG_NUM|CUR_POINT_NUM|SEND.*NAVI|RECEIVE.*NAVI|amap.*broadcast|autonavi.*broadcast|ILaneMatch|IAMSLocation|AmapLinkService|ALinkService|lane.?info.?callback|lane.?loc.?info.?observer|lane.?info.?in.?range|high.?freq.?loc.?info|send.?lane|send.?route|broadcast.?lane|broadcast.?route|register.?lane|register.?adas"
}
regs={k:re.compile(v,re.I) for k,v in groups.items()}
def dexstrings(b):
    if not b.startswith(b"dex\n"):return
    count,off=struct.unpack_from("<II",b,56)
    if count>2000000 or off+4*count>len(b):raise ValueError("DEX bounds")
    for i in range(count):
        a=struct.unpack_from("<I",b,off+4*i)[0]
        if a>=len(b):continue
        for _ in range(5):
            if a>=len(b):break
            v=b[a];a+=1
            if v<128:break
        e=b.find(b"\0",a,min(a+4096,len(b)))
        if e>=0:yield b[a:e].decode("utf8","replace")
def scan(strings):
    out={k:set() for k in regs}
    for s in strings:
        if len(s)>280:continue
        for k,r in regs.items():
            if r.search(s):out[k].add(s)
    return out
with zipfile.ZipFile(p) as z:
    print("ZIP entries",len(z.namelist()),"DEX", [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex",n)])
    print("Native libraries", [n for n in z.namelist() if n.startswith("lib/") and n.endswith(".so")])
    total=collections.defaultdict(set)
    for n in z.namelist():
        if re.fullmatch(r"classes\d*\.dex",n):
            out=scan(dexstrings(z.read(n)))
        elif n.startswith("lib/arm64-v8a/") and n.endswith(".so"):
            out=scan(m.group().decode("ascii") for m in re.finditer(rb"[\x20-\x7e]{5,280}",z.read(n)))
        else:continue
        for k,ss in out.items():
            if ss:
                print(f"\n{n} {k} {len(ss)} hits")
                # prioritized identifiers; report is evidence of presence, not availability
                for s in sorted(ss,key=lambda s:(len(s)>150,len(s),s))[:100]:
                    print(" ",s)
                    total[k].add(s)
    print("\nSUMMARY distinct reported strings", {k:len(v) for k,v in total.items()})
print("Static strings do not establish callable APIs, live output, Taiwan coverage, or control suitability.")
