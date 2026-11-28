# Carrot Bridge wide.89 — 雙高德車道候選即時觀察

- 基於 exact wide.88，App 解析一般版 Type 14 與車機版 13012，透過既有 Navi v2 guidance_current.amap_lane_candidate v1 即時傳遞唯讀候選。
- C4 配套：test/c4-vision-ar-hud f7cbad34f5e38a7efa8cdce30d328126f715d3a3。Mac 配套：test/amap-live-lane-hud-20261128 50c2ac829099e8b7fc9f14115f5c04a666dbc02d；需另外安裝測試層。三端 CI 已通過，尚未實車驗證。
- 不增加車控、車道變換指令、絕對車道定位或 AR 空間對位。不保證高德原始推薦語意、台灣高精度覆蓋或收到全部事件。僅在停車配置、乘客觀察。
- 本版沿用 wide.88，不包含 PRE 線性升降速、20% 速差保護、ROAD 36 正式控速修復。原有正式版不替換。
- 原簽章憑證 SHA256 已核對，APK v3 驗證通過。私鑰不提交 GitHub；只保留本次 APK 公開簽章區塊和固定 hash，可重組完全相同的已簽署 APK。
- APK SHA256: 68418c6919f00fe1f34bf4f03860753b5ddfc470a387df75725d46589c32802a
