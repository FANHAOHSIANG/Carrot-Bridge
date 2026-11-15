# Carrot Bridge

**讓 Android 手機或車機同時顯示導航、神盾與 comma 車況，並把支援的導航資料交給 Carrot。**

整合高德車機版、高德一般版、Google 地圖投屏與內建 Google 導航 NOO。可單獨當分割畫面使用，也可連接 **C3、C3X 或 comma four**，提供轉彎引導、路線及已確認的道路速限。comma 須使用支援 Carrot Navi v2 的 Carrot 版本。車輛是否採用資料，取決於分支、設定、模型及車型支援。

**[下載 APK](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/download/wide.70/Carrot-Bridge-wide.70.apk)** · **[完整功能手冊](docs/FEATURES_zh-TW.md)** · **[安裝與操作](docs/INSTALL_zh-TW.md)** · **[官方設定建議](docs/CARROT_SETTINGS_zh-TW.md)** · **[外接 HUD](docs/HUD_zh-TW.md)** · **[分支比較](docs/C4_BRANCHES_zh-TW.md)** · **[測試分支安裝](docs/C4_TEST_INSTALL_zh-TW.md)**

> [!WARNING]
> `test/carrot-wip-upstream-20261104` 是持續變動的個人測試分支，請小心使用。可能發生非預期減速、路線偏差、功能失效或退出控制。請停車設定，先確認車型與線束支援、保留回復方法，駕駛全程注意道路並隨時接管。離線測試通過不等於實車驗收，不能依賴 App 或測試分支自動完成路口轉彎。

## wide.74 HUD 測試版

**[下載 wide.74 測試 APK](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/tag/wide.74)** · **[功能示意圖、各地圖可顯示的效果、搭配分支與 Carrot Web 設定](docs/WIDE74_HUD_zh-TW.md)**

wide.74 新增兩版高德的 HUD 地圖影像，並包含高德車機版測速紅光與分區一全幅。建議先停車驗收。

## 下載與需求

目前正式發布版 **wide.70**，需 **Android 12 以上**。投屏時在同一台 Android 安裝目標 App，並啟動 **Stellar 或 Shizuku 擇一**；Stellar 須開啟 Shizuku 相容層。

| 項目 | 下載／教學 | 什麼時候需要 |
| --- | --- | --- |
| **Carrot Bridge wide.70** | **[主程式 APK](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/download/wide.70/Carrot-Bridge-wide.70.apk)** | 所有功能入口；同簽章舊版可覆蓋更新 |
| Stellar 1.1 | [官方 APK](https://github.com/roro2239/Stellar/releases/download/v1.1%28101000%29/stellar-v1.1-release.apk) | 投屏授權工具，與 Shizuku 擇一 |
| Shizuku 13.6.0 | [官方 APK](https://github.com/RikkaApps/Shizuku/releases/download/v13.6.0/shizuku-v13.6.0.r1086.2650830c-release.apk) | 投屏授權工具，與 Stellar 擇一 |
| 高德車機版／一般版 | [車機版](https://www.amapauto.com/) · [一般版](https://mobile.amap.com/cn/download.html) | 選用對應高德來源時 |
| Google 地圖 | [Google Play](https://play.google.com/store/apps/details?id=com.google.android.apps.maps&hl=zh-TW) | 選「Google 地圖（僅投屏）」時 |
| Google 導航 NOO | [Google 金鑰設定](docs/GOOGLE_SDK_zh-TW.md) | 已內建；需 Google Play 服務、網路、定位與自己的 Cloud 金鑰，使用量可能計費 |
| 神盾測速照相 | [Google Play](https://play.google.com/store/apps/details?id=tw.com.ainvest.outpack&hl=zh-TW) | 神盾投屏與 App 紅光提醒 |

[最新版與 SHA-256](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/latest) · [歷史版本](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases) · [投屏授權步驟](third_party/projection/README.md)

## 每個地圖可以做什麼？

| 來源 | 畫面與操作 | 可交給 comma 的資料 | 用法與限制 |
| --- | --- | --- | --- |
| **高德車機版** | 投屏同機高德車機 App，在高德內設目的地 | 導航通道提供的轉彎、距離等引導，其他欄位依實際收到的資料 | 適合車機介面；有畫面不代表廣播已到達，完整路線與相機不保證每個版本都有 |
| **高德一般版** | 投屏同機高德手機 App，透過 Link 授權與訂閱 | 有效轉彎、距離、道路名稱；收到完整選定路線後可傳路線與下一步 | 使用高德自己的路線，不另請 Mapbox 重規劃；長路線以測試分支配套較完整，手機版相機仍未確認 |
| **Google 地圖（僅投屏）** | 顯示官方 Google Maps App | 此模式不提供該 App 的路線／轉彎串接 | 使用熟悉的 Google Maps 畫面與語音；要把 Google 路線送 comma，選 NOO |
| **Google 導航 NOO** | 在 Carrot Bridge 內搜尋、收藏、規劃與導航 | SDK 提供的目前／下一轉彎、距離、位置與路線 | 不是讀取另一個 Google Maps App；不保證有 Google 速限、相機或號誌 |
| **神盾測速照相** | 分區一投屏，提醒與語音由神盾提供 | wide.70 的神盾影像辨識未接入 comma 測速出站流程 | 符合辨識條件時，Carrot Bridge 四邊閃紅光 |
| **TDX／OSM 道路速限** | 獨立道路資料功能，可顯示 OSM 圓牌 | 開啟傳送後，優先送道路與方向已確認的 TDX，否則採合格 OSM | 與導航來源不同；衝突、過期或道路不明時撤銷，不是測速點清冊 |

三個可提供導航資料的來源是高德車機版、高德一般版、Google 導航 NOO；**四個地圖選項的能力不同**。[各來源操作與判讀](docs/FEATURES_zh-TW.md#地圖與導航)

## 三個導航來源的 NOO 能力

本專案使用 **導航輔助（NOO）** 這個名稱，對應 App 裡的「Google 導航 NOO」。三個來源提供相符的轉彎種類與距離時，Carrot 可依設定計算 **ATC 轉彎減速**。有可用的路線幾何時，才有條件參與 **路線彎速（ROUTE）**。

| 來源 | 適合用來做什麼 |
| --- | --- |
| **高德車機版** | 使用車機導航的轉彎、距離等廣播。收到有效執法速限與距離時，也可提供測速提醒及對應減速候選。 |
| **高德一般版** | 透過 Link 使用高德的轉彎和選定路線。長路線可用個人測試分支的接收配套，手機版測速仍待封包驗證。 |
| **Google 導航 NOO** | 由內建 SDK 提供當前與下一個轉彎、距離和有效路線區段，適合先核對導航引導與 ATC。 |

Carrot 的轉向、變道與車外方向燈各有車型、硬體和設定條件。各來源的資料前提和官方／測試分支的差異見[導航輔助（NOO）比較](docs/FEATURES_zh-TW.md#導航輔助noo比較)。

## 其他功能

| 功能 | 能做到什麼 | 操作入口 |
| --- | --- | --- |
| 分區投屏 | 分區一放神盾／其他 App／時鐘；分區二放地圖 | 各區「⋯」選單 |
| 比例與橫直向適配 | 拖曳後適配投屏，橫直向比例分別保存 | 分隔線或「版面與比例設定」 |
| 返回、重啟與收合 | 各區分別返回 App、重新開啟；下方面板可收合 | 選單第一項「返回投屏 App」；「⌄」及「⋯ → 展開面板」 |
| 車況與即時診斷 | comma 車速、橫／縱向狀態、投屏授權與導航通道狀態 | 分區一下方面板「切換 → 即時診斷」 |
| 操作面板 | 原有快捷操作；車端相關項目依連線及支援生效 | 分區一下方面板「切換」 |
| 常用地址 | 三組名稱／地址，點選開啟、長按編輯；必要時複製貼上 | 「三個常用地址」 |
| Google 收藏與最近導航 | 快速重選目的地，結束導航回到搜尋頁 | Google NOO 搜尋畫面 |
| 高德一般版鍵盤 | 切到導航區或裝置主畫面 | 分區二選單的鍵盤選項 |
| OSM 速限牌 | 顯示、隱藏、長按移動；無資料顯示「—」 | 「顯示 OSM 速限牌」 |
| 道路速限傳送 | 獨立決定是否送已確認的 TDX／OSM 速限到 comma | 設定中的「傳送道路速限」開關 |
| 神盾紅光 | 辨識到 500 公尺內固定／移動測速後，App 四邊閃紅光 | 「神盾紅光提醒、取樣與尺寸保護」；需足夠視窗尺寸 |
| Amap2Tesla | 讓另一裝置的瀏覽器顯示神盾投屏 | 「Amap2Tesla 僅投神盾」；輸入 App 顯示的完整網址 |
| 記錄與匯出 | 分享診斷、開始記錄、匯出報告與事件 ZIP | 「即時診斷 → 報告」；分享前檢查位置與路線資料 |

[完整功能手冊](docs/FEATURES_zh-TW.md) 說明各功能的前提與限制。儲存庫中的歷史台灣測速版本仍保留，不能把歷史功能清單直接套在 wide.70。

## 外接 HUD 會顯示什麼？

相容的 TURZX 可直連 comma，或透過相容的 Mac Jetlink 與 CarrotMacHUD 轉送。常用畫面有車速、檔位、道路速限、巡航、3D 車道與前車距離，另有導航轉彎、P 檔行程、R 檔估算軌跡與系統資訊。各地圖會送哪些提示、高德倒數和測速牌會出現在哪裡，可查[外接 HUD 畫面與功能](docs/HUD_zh-TW.md)。

使用官方 Carrot 和 USB 直連 HUD 時，可從 `ClusterHud=1`、`ClusterHudScreenMode=0` 開始。接好地圖後，先確認轉彎和距離收件，再決定要不要開啟轉彎減速、道路速限與彎速功能。各項位置、設定值及建議順序見[官方 Carrot 設定建議](docs/CARROT_SETTINGS_zh-TW.md)。

## 搭配官方或測試分支的體驗

此處「官方」指 **ajouatom 的 Carrot `carrot-wip`**，並非 comma.ai 原版 openpilot。比較核對於 **2026-11-15**；官方 `carrot-wip` 本身也是滾動開發分支。

| 項目 | 官方 Carrot `carrot-wip` | 個人 `test/carrot-wip-upstream-20261104` |
| --- | --- | --- |
| App 投屏、Google 搜尋、神盾畫面 | 可獨立使用，不要求換 comma 分支 | 相同 |
| Navi v2 引導與轉彎減速 | 有接收與 ATC 路徑，需有效資料、設定及車型支援 | 保留相同基礎功能 |
| 路線彎速 | 有既有路線曲率處理 | 加入定位、方向、近端視覺配對與彎道上限釋放修正 |
| 高德 Link 長路線 | 核對版本的接收／控制解析最多保留 256 點 | 最多完整保留 4,096 點，超限或座標無效撤銷 |
| 高速直線短折返誤減速 | 核對版本的原有曲率算法 | 已合併特定短折返修正，實車反應待驗證 |
| 無目的地的 OSM 彎速預覽 | 未見本專案這套離線 OSM 預覽模組 | 有全台圖資下載與速度預覽，需圖資、道路配對及對應設定 |
| 外接 HUD | 有駕駛、行程、系統、導航、P／R 檔等畫面 | 另有繁中和高德三燈／測速提醒配套。手機倒數需配套 App 輸出 |
| HUD 導航藍線 | 依現有路線、模型及 HUD 管線 | 穩定修正 [PR #41](https://github.com/FANHAOHSIANG/openpilot-carrot/pull/41) 核對時仍為草稿、未合併 |

**官方也能使用有效導航資料，測試分支主要增加配套與修正。** 接到轉彎提示不等於車輛一定轉彎；畫面方向指示也不等於車外方向燈能點亮。[設定、硬體條件與驗證層級](docs/C4_BRANCHES_zh-TW.md)

## comma four 測試分支安裝短網址

在 **comma four 的 Custom software／自訂軟體 URL** 畫面輸入：

```text
https://da.gd/cb-test
```

**這是測試分支，請小心使用。** 此短網址限 **comma four（MICI）**，安裝 `FANHAOHSIANG/openpilot-carrot` 的 `test/carrot-wip-upstream-20261104` 最新內容。已核對下載檔，實機安裝、首次開機及車輛驗收待確認。C3、C3X 可搭配已安裝的相容 Carrot 使用 App。請先閱讀[完整安裝步驟、備用長網址與回復方式](docs/C4_TEST_INSTALL_zh-TW.md)。

## 第一次使用

1. 停車後安裝 APK、目標地圖及投屏工具；啟動 Stellar／Shizuku，再回 App 授權。
2. 「分區二 ⋯」選地圖；「分區一 ⋯ → 選擇投屏 App／空白畫面」選神盾、其他 App 或時鐘。
3. Google NOO 先完成 [金鑰設定](docs/GOOGLE_SDK_zh-TW.md)；高德則在對應 App 內設目的地並開始導航。
4. 要連 comma，讓兩端網路互通並設定 comma 位址。依序核對 App 引導、Navi v2 與 comma 接收。畫面和減速分別確認，參考[官方設定建議](docs/CARROT_SETTINGS_zh-TW.md)。
5. 要試個人分支，先閱讀[測試提醒、安裝入口與回復方式](docs/C4_TEST_INSTALL_zh-TW.md)。只用投屏可直接在 Android 操作。

[更新紀錄](CHANGELOG.md) · [wide.70 驗證範圍](variants/wide70/README.md) · [開發與重建](docs/BUILD_zh-TW.md) · [資料來源與授權](docs/DATA_SOURCES_zh-TW.md)

上游專案、第三方 App 與圖資各自沿用原有授權。[Stellar 與 Shizuku 授權](third_party/projection/README.md#版本與校驗)
