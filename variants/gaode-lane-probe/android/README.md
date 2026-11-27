# Android GaodeProbe 0.1 Link observer

Standalone package tw.carrot.gaodeprobe; original Gaode and Carrot Bridge remain installed. Uses the exported Link service only, actual application identity, normal authorization and callback UID checks. If refused, stop; no workarounds. Does not access non-exported L4 service, patch Gaode, collect native centerlines, or modify vehicle control. Android foreground service records only user-started authorized callbacks. Local bounded redacted JSONL; use Stop then Export. No background auto-start, no network endpoint. New run overwrites previous local file after confirmation. Position and route data may still be private; share only deliberately. APK test signer is per build, so later test APK updates may require uninstall/reinstall. Do not use simultaneously with Bridge Link until coexistence is verified; independent subscription may be refused. Device test pending.

Build: bash variants/gaode-lane-probe/android/build.sh (Android SDK 35, build-tools 35.0.0, JDK 17). CI artifact is not a release. Only if build succeeds is there a signed APK. No claim of actual lane data acquisition. Exported JSONL uses prior replay probe event format.

## APK 下載

- [GaodeProbe 0.1 Link Test 預發布頁](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/tag/gaodeprobe-0.1-link-test)
- [原始成功建置與暫存產物](https://github.com/FANHAOHSIANG/Carrot-Bridge/actions/runs/45879309561)

預發布流程只轉存既有成功建置的 APK，不重新簽署，也不變更正式版。
