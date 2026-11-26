#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
HERE="$ROOT/variants/gaode-lane-probe/android"
SDK="$ANDROID_HOME"
BT="$SDK/build-tools/35.0.0"
JAR="$SDK/platforms/android-35/android.jar"
OUT="$HERE/out"
rm -rf "$OUT"; mkdir -p "$OUT/classes" "$OUT/dex" "$OUT/src"
cp "$ROOT/variants/wide47/src/WideAmapLink.java" "$ROOT/variants/wide47/src/WideAmapLinkTrace.java" "$ROOT/variants/amap-link1/src/WideAmapLinkCodec.java" "$ROOT/variants/amap-link1/src/WideAmapLinkPolicy.java" "$OUT/src/"
python3 - "$OUT/src/WideAmapLink.java" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text()
needle='if (token != null && !token.isEmpty() && token.length() <= 4096) {'
assert s.count(needle)==1
p.write_text(s.replace(needle,'if (false) {'))
PY
javac -source 8 -target 8 -classpath "$JAR" -d "$OUT/classes" "$OUT/src/"*.java "$HERE/src/"*.java
"$BT/d8" --lib "$JAR" --min-api 26 --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')
"$BT/aapt2" link -I "$JAR" --manifest "$HERE/AndroidManifest.xml" -o "$OUT/unsigned.apk"
(cd "$OUT/dex" && zip -q -j "$OUT/unsigned.apk" classes*.dex)
"$BT/zipalign" -p -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
keytool -genkeypair -keystore "$OUT/test.jks" -storepass android -keypass android -alias gaode-test -dname "CN=GaodeProbe Test" -keyalg RSA -keysize 2048 -validity 365
"$BT/apksigner" sign --ks "$OUT/test.jks" --ks-pass pass:android --key-pass pass:android --out "$OUT/GaodeProbe-0.1-link-test.apk" "$OUT/aligned.apk"
"$BT/apksigner" verify --verbose --print-certs "$OUT/GaodeProbe-0.1-link-test.apk"
(cd "$OUT" && sha256sum GaodeProbe-0.1-link-test.apk > SHA256SUMS.txt)
