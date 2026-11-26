# Carrot Bridge

**一個 Android App，整合導航、神盾、comma 車況與外接 HUD。**

適用 Android 12 以上手機／車機。可單獨當分割畫面使用，也可搭配支援 Carrot Navi v2 的 C3、C3X 或 comma four。高德與內建 Google 導航可提供有效引導；車輛是否採用資料仍由 Carrot 版本、車型、設定及安全條件決定。

## 下載與需求

| 版本／工具 | 下載 | 用途 |
| --- | --- | --- |
| **Carrot Bridge wide.85** | **[下載 APK](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/download/wide.85/Carrot-Bridge-wide.85.apk)** · [版本說明與 SHA-256](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/tag/wide.85) | 目前主推版本，原簽章可覆蓋相容舊版 |
| wide.77 | [歷史驗收版](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/tag/wide.77) | 曾獲使用者實機確認；保留歷史下載，Android 降版可能需備份及重裝 |
| Stellar | [官方 APK](https://github.com/roro2239/Stellar/releases/download/v1.1%28101000%29/stellar-v1.1-release.apk) | 投屏管理工具，需開啟 Shizuku 相容層 |
| Shizuku | [官方 APK](https://github.com/RikkaApps/Shizuku/releases/download/v13.6.0/shizuku-v13.6.0.r1086.2650830c-release.apk) | 與 Stellar 擇一 |
| 高德地圖 | [車機版](https://www.amapauto.com/) · [一般版](https://mobile.amap.com/cn/download.html) | 依所選地圖安裝 |
| Google 地圖 | [Google Play](https://play.google.com/store/apps/details?id=com.google.android.apps.maps&hl=zh-TW) | 官方地圖投屏 |
| 神盾測速照相 | [Google Play](https://play.google.com/store/apps/details?id=tw.com.ainvest.outpack&hl=zh-TW) | 神盾投屏與紅光提醒 |

[所有版本](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases) · [詳細安裝](docs/INSTALL_zh-TW.md) · [Google NOO 金鑰](docs/GOOGLE_SDK_zh-TW.md) · [投屏授權](third_party/projection/README.md)

> [!IMPORTANT]
> wide.85 沿用原簽章，已通過建置、APK v3 簽章與檔案雜湊檢查。正式發布不等於每種車機已驗收；自動投屏實機效果仍須確認。**新版交流道 PRE 控速、線性升降速尚未接入實際車控。** 請停車設定，不以 App 畫面或導航引導代替駕駛判斷。

## 三步開始使用

1. **安裝**：下載 wide.85 APK；同簽章舊版可直接覆蓋。依需求裝高德、Google Maps、神盾。只使用分割投屏不需要 comma。
2. **設定投屏**：啟動 Stellar 或 Shizuku，首次依 Android 正常授權。橫向左側地圖是分區二；右側神盾、其他 App 或時鐘是分區一。選好兩區後，重新開 App 會嘗試自動恢復；服務停止或授權撤銷時仍須正常啟動／授權。
3. **連接 comma（選用）**：Android 與 comma 使用互通的區域網路，在 App 填入實際 comma 位址。停車核對來源、引導、Navi v2 與車端收件。Google NOO 另外需要自己的 [Google SDK Key](docs/GOOGLE_SDK_zh-TW.md)，可能產生 API 費用。

## 地圖怎麼選

| 地圖選項 | 投屏／導航 | 傳給 comma 的資料 |
| --- | --- | --- |
| 高德車機版 | 同機高德車機 App | 有效轉彎、距離、道路、測速／號誌（依實際廣播）；wide.82–85 增加出口及路線原始資料 |
| 高德一般版 | 同機高德 App、Link 授權 | 有效引導、路名、選定路線及下一步；相機與倒數視來源輸出 |
| Google 地圖（僅投屏） | 官方 Google Maps App | 不擷取該 App 的導航引導或路線 |
| Google 導航 NOO | 內建 SDK、搜尋／收藏／導航 | 目前及下一引導、距離、位置、路線；不保證提供 Google 速限、測速或號誌 |

高德不需額外申請 Google Key；一般版需正常 Link 認證。完整路線須來源真的供應，不另請 Mapbox 重規劃。TDX／OSM 是獨立道路資料來源，不是 Google Maps 回傳。

## 功能總覽

| 功能 | 怎麼用／範圍 |
| --- | --- |
| 雙區投屏、自動恢復 | 各區「⋯」選 App；拖曳分隔線，記憶橫直向比例；已授權且服務可用時嘗試自動啟動 |
| 獨立返回、重開、收合 | 各區選單「返回投屏 App／重新開啟」；下方面板可收合及恢復 |
| 日夜模式與版面 | 沿用 wide.77 的畫面重建修正，重選同一 App 不必重建；裝置差異仍須確認 |
| 常用地址與 Google 收藏 | 三組常用地址、最近導航、內建 NOO 搜尋；一般版高德鍵盤可切換位置 |
| OSM 速限圓牌 | 顯示、隱藏、長按移動；無有效資料顯示「—」 |
| 道路速限傳送 | TDX／OSM 獨立開關；只傳符合道路及方向配對的資料，衝突或過期撤銷 |
| 神盾紅光 | 有效辨識到 500 m 內固定／移動測速時，App 四邊紅光；神盾語音由神盾提供，不宣稱已接入車端測速煞車 |
| Amap2Tesla | 選「Amap2Tesla 僅投神盾」，在同網路瀏覽器輸入 App 提供的網址；與 comma 資料分開 |
| 車況與快捷操作 | 分區一下方面板「切換」；顯示車速、橫縱向、授權及連線，操作須車端支援 |
| 診斷與紀錄 | 「即時診斷 → 報告 → 開始記錄／匯出報告與事件 ZIP」；搭配同時段 C4 Log |

## wide.85 新增了什麼

| 版本 | 主要變更 |
| --- | --- |
| wide.78–79 | 舊有高德及三來源轉彎預調資料配套，車端仍依原有策略與限制 |
| wide.80–83 | 投屏啟動掛點、等待授權與自動重連；83 保留兩區共用流程 |
| wide.82 | 高德出口名稱、方向、路段及車道原始資料（僅顯示） |
| wide.84 | 總路程、剩餘路程、時間及新版轉向圖示原始欄位 |
| **wide.85** | 新增導航觀察資料版本、工作階段識別碼、樣本序號；來源切換／中斷後重設，方便 App ZIP 與 C4 Log 比對 |

wide.85 的觀察 ID **不是**已確認的路線 ID、交流道事件 ID 或匝道完成訊號。不依未知數字圖示推測方向，不提供新的速度或轉向命令。[完整更新紀錄](CHANGELOG.md) · [wide.85 來源與驗證](docs/WIDE85_zh-TW.md)

## 搭配 comma 與外接 HUD

| 搭配方式 | 適合用途 | 入口 |
| --- | --- | --- |
| 只用 Android | 地圖、神盾、分割投屏 | 不用改 comma |
| 官方 Carrot | 已支援的 Navi v2、ATC、速限及彎速；依官方版本設定 | [官方 carrot-wip](https://github.com/ajouatom/openpilot/tree/carrot-wip) |
| 獨立 Test | 個人導航接收、路線配對、OSM 彎速與 HUD 配套 | [分支](https://github.com/FANHAOHSIANG/openpilot-carrot/tree/test/carrot-wip-upstream-20261104) |
| Tony 融合 Test | 融合 Tony／Carrot 及個人導航 HUD 配套；不同控制選項須另核對 | [分支](https://github.com/FANHAOHSIANG/openpilot-carrot/tree/test/tony-carrot-wip-integrated-20261117) |
| C4 USB 直連 TURZX | 不需要 Mac；支援相容 HUD 與資料 | [HUD 設定](docs/HUD_zh-TW.md) |
| Mac Jetlink HUD | 用相容 Jetlink 與 Mac HUD 轉送 | [CarrotMacHUD](https://github.com/FANHAOHSIANG/carrotMAC-HUD) |

兩個 Test 分支已納入 wide.85 觀察識別碼接收。導航模式 6 的標題區可顯示有效高德出口名稱、明確方向文字及格式化剩餘路程；並非每個行車模式都顯示。紅綠燈、測速、道路速限、導航距離及車況仍依資料源和畫面模式。Mac 沿用現有 Jetlink；新 Swift 依賴下載憑證問題尚未解決。

> [!WARNING]
> 個人 Test 分支是滾動開發，不是 comma 原廠正式車控版本。可能非預期減速、偏移或退出控制。實機前先核對車型、線束與既有設定，保留已知可用版本；不以新版 App 作為提高轉向權限或修改安全限制的理由。

[分支比較](docs/C4_BRANCHES_zh-TW.md) · [官方設定說明](docs/CARROT_SETTINGS_zh-TW.md) · [測試分支安裝及回復](docs/C4_TEST_INSTALL_zh-TW.md)

## 常見問題

| 問題 | 先檢查 |
| --- | --- |
| 還要按「啟動投屏」？ | 確認 Stellar／Shizuku 服務與授權仍有效、兩區已選 App；若仍需手動，記錄車機型號與 ZIP |
| 看得到地圖但 C4 沒導航？ | 地圖是否為僅投屏模式、選定來源是否真的導航、Navi v2 收件與網路是否正常 |
| HUD 沒有新增出口資訊？ | 使用高德車機版、有有效廣播、更新對應 C4／Mac HUD，查看模式 6；過期或未知值不顯示 |
| PRE 一直在／巡航忽快忽慢？ | 新版控速尚未啟用，保留原車控並回報同一行程資料，勿為測試刻意重現危險情境 |
| APK 安裝衝突？ | 核對 Android 12+、完整 APK 與原簽章；不要任意刪除舊 App 資料 |
| 如何回報？ | App 版本、地圖版本、車機型號、comma 分支／提交、發生時間；停車匯出 ZIP 及同次 C4 Log，分享前檢查位置與帳密 |

## 完整文件

[功能手冊](docs/FEATURES_zh-TW.md) · [安裝與排錯](docs/INSTALL_zh-TW.md) · [HUD](docs/HUD_zh-TW.md) · [C4 分支](docs/C4_BRANCHES_zh-TW.md) · [版本說明](docs/WIDE85_zh-TW.md) · [更新紀錄](CHANGELOG.md) · [開發與重建](docs/BUILD_zh-TW.md) · [資料來源及授權](docs/DATA_SOURCES_zh-TW.md)

上游專案、第三方 App 與圖資各自沿用原有授權。[Stellar 與 Shizuku 授權](third_party/projection/README.md#版本與校驗)
