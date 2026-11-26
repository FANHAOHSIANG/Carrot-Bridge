# 外接 HUD 畫面與功能

> 2026-11-26：wide.85 配套已合併兩個 Test 分支，Mac HUD 亦有對應更新。新增高德車機出口名稱、明確方向文字與格式化剩餘路程，目前接入導航模式 6 的標題區；未知／過期資料不顯示。不改巡航控制。詳見 [wide.85 配套](WIDE85_zh-TW.md)。Mac 沿用已安裝的 Jetlink，完整 Swift 新建置受 ONNX 下載站憑證阻擋。以下原有畫面位置是歷史基準，依實際 HUD 版本為準。

[回首頁](../README.md) · [官方設定建議](CARROT_SETTINGS_zh-TW.md) · [官方與測試分支比較](C4_BRANCHES_zh-TW.md)

TURZX 外接 HUD 會顯示 comma 的車況、駕駛輔助狀態及收到的導航提示。以 1920 × 462 橫向畫面為例，預設左側是車道和車況，右側有導航時顯示引導，無導航時切回行程摘要。Carrot Bridge 的地圖和神盾投屏繼續在 Android 車機或手機上操作。

## 接法與適用裝置

| 接法 | 適用裝置 | 使用方式 |
| --- | --- | --- |
| **comma → USB → TURZX** | C3、C3X、comma four，須使用有外接 HUD 功能的 Carrot 版本及相容的 TURZX `1CBE:0092` | TURZX 接到 comma 可用的 USB 資料端口。在 Carrot Web 的「顯示 → 外接 HUD」設 `ClusterHud=1`，由 comma 繪圖並輸出。Mac 可以關機。 |
| **comma → USB → Mac Jetlink → USB → TURZX** | CarrotMacHUD 文件已記錄 comma four／Mac mini 搭配。C3、C3X 的這組 Mac 接法需另核對相容版本 | comma four 的 Port 2 接 Mac，TURZX 接 Mac 的另一個 USB 埠。安裝相容的 CarrotMacHUD，開啟 Jetlink 與 HUD helper。Mac 負責繪圖與 USB 輸出，車況和導航資料仍來自 comma。 |

`ClusterHud=1` 管理 comma 的直連 USB 輸出。Mac 接法以 Jetlink 與 HUD helper 的連線為準。前方相機畫面還需要 comma 對 Mac 提供相機預覽。既有 Mac HUD 使用者可參考專案首頁的繁中更新與對應版本。〔[官方支援裝置](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/README.md) · [官方外接 HUD 手冊](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/cluster/README.md) · [CarrotMacHUD 下載與說明](https://github.com/FANHAOHSIANG/carrotMAC-HUD)〕

## 會看到什麼

| 情境 | 畫面與資訊 |
| --- | --- |
| **一般行駛** | 大字車速、道路速限、巡航設定速度、跟車間距格、檔位、方向燈及車道置中狀態。上方有時鐘與導航連線標記，側邊可見加速度、轉向、油量／電量與胎壓。顯示項目隨車型和資料而異。 |
| **3D 車道／前方相機** | 顯示車道線、道路邊緣、預測行駛路徑、前車與跟車距離。雷達或盲點資料可用時，可顯示周圍車輛、速度及距離。支援切到前方一般／廣角相機，保留相應的路徑與車輛疊圖。 |
| **導航中** | 右側可顯示目前和下一個路口的圖示、距離和路名，例如「右轉 · 130 m」。有相應資料時也可顯示車道指引、剩餘里程／時間與測速提醒。`NAVI` 代表外部導航已連接。 |
| **減速狀態** | 有有效速度候選時可看到 `cam`／`section`（測速／區間）、`road`（道路速限）、`atc`（導航轉彎）、`vturn`（視覺彎速）或 `route`（路線彎速）等來源。道路速限、執法速限與巡航設定速度各有不同用途。 |
| **P 檔** | 車輛圖、日期／時鐘、可用的電量和胎壓。本次行程可顯示距離、時間、平均速度、輔助駕駛比例和急加速／急煞車／急轉彎次數。直連版本有取得天氣資料時也能顯示天氣。 |
| **R 檔** | 車輛圖、方向盤角度、可用的左右盲點狀態，以及隨方向盤轉動的估算倒車軌跡。倒車時仍須直接看原車後方影像與周圍環境。 |
| **系統資訊／診斷** | 網路、影格率、相機狀態、CPU、溫度、記憶體、磁碟和校正角度。延遲、轉向與除錯圖表可選擇固定顯示。 |

HUD 在 comma 已進入行車狀態且取得檔位時會切換 P／R 專用畫面。熄火後 HUD 預設休眠。資料缺少或過期時，對應欄位會省略或以 `—` 表示。〔[官方 HUD 繪圖與模式](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/cluster/README.md) · [測試分支顯示來源](https://github.com/FANHAOHSIANG/openpilot-carrot/blob/796633626c61ef0fa9486ba0898a970b99f2d31a/openpilot/selfdrive/carrot/cluster/cluster_renderer.py)〕

### 選擇畫面

在「顯示 → 外接 HUD → 畫面與相機」找 `ClusterHudScreenMode`。設定值以官方 `carrot-wip` 2026-11-15 核對版本為準。Mac helper 的選項依其版本而定。

| 值 | 畫面 |
| ---: | --- |
| `-1` | 全幅 3D 駕駛畫面。切到前方相機時使用模式 `0` 的資訊版面。 |
| **`0`** | **日常建議**。駕駛畫面搭配自動切換的導航／行程欄。 |
| `1` | 轉向、橫向規劃、即時扭力與延遲診斷。 |
| `2` | 固定系統資訊與裝置負載。 |
| `3`／`4` | 全幅除錯圖表／駕駛畫面加圖表。 |
| `5` | 駕駛畫面加固定行程摘要。 |
| `6` | 全導航版面。依來源顯示引導、導航媒體與提醒。 |
| `7` | 駕駛畫面加官方導航模型地圖預覽。預覽需有新的地圖影像。 |

左右欄可用 `ClusterHudPanelLayout` 對調。直連版的 `ClusterHudCameraViewMode=0` 是預設 3D，`1` 為較低的 3D 視角，`2`／`3` 是一般／廣角道路相機，`4` 依速度切換相機。〔[官方設定選單](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot_settings.json)〕

## 地圖、號誌與測速會在 HUD 出現什麼

| 來源 | 可顯示的內容與前提 |
| --- | --- |
| **高德車機版** | 收到有效欄位時顯示轉彎、距離和道路資訊。相符的版本送來確認的直行燈態或執法資料時，測試分支能顯示號誌秒數、測速限速和剩餘距離。 |
| **高德一般版** | Link 授權與導航有效時可提供轉彎、距離、道路名和選定路線。中性號誌倒數需來源確實輸出、配套 C4 與 HUD；wide.85 實際相容性仍依資料確認。手機版測速封包仍待驗證。 |
| **Google 導航 NOO** | 可用的 SDK 引導可顯示轉彎、下一步、距離和道路資訊。路線座標可供接收端使用，地圖影像及號誌／測速欄位需有對應的來源。 |
| **Google 地圖（僅投屏）** | Google Maps 畫面留在 Android 分區。HUD 保有 comma 車況，轉彎引導需選用有導航資料輸出的來源。 |
| **TDX／OSM 和神盾** | App 開啟道路速限傳送且 comma 收到有效值時，HUD 可顯示道路速限。神盾紅光與語音提醒留在 Android。 |

行駛畫面的線是模型預測的路徑。導航地圖的路線需要地圖媒體或官方導航模型預覽。Carrot Bridge 傳送的路線座標可用於導航資料處理，HUD 地圖畫面依收到的媒體決定。外部導航藍線有歷史修正 PR；本次不宣稱全場景驗收完成。〔[導航資料與影像格式](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/carrot_navi_api.md) · [HUD 藍線 PR #41](https://github.com/FANHAOHSIANG/openpilot-carrot/pull/41)〕

### 測試分支與 Mac HUD 的提醒位置

- 測試分支的**駕駛摘要（5）和系統資訊（2）**可同時顯示兩種提示。車道區右上是三燈與秒數，右下是測速牌與距離。全導航與小地圖使用原有號誌區，有來源圖片時優先顯示圖片。
- 高德車機版收到有效紅／綠燈態時亮對應燈，已確認的直行綠燈最多顯示三秒。手機版倒數配套以暗色三燈和中性秒數顯示。路口燈色及通行仍以實際號誌為準。
- 有效區間測速優先顯示區間剩餘距離。資料撤銷、逾時或距離用盡後，對應提示會消失。
- 測試分支有繁中行程、駕駛資訊和部分 ATC／TBT 文字。Mac 經更新可跟隨 comma 的繁中設定，來源圖片照原樣顯示。Mac 的 P 檔目前顯示已轉送的車況與行程。

**個人測試分支請小心使用。** 顯示功能需同時配對 Android、comma 和 HUD 版本。先停車檢查車況、模式及導航提示，再以實際資料核對。〔[USB HUD 合併說明](https://github.com/FANHAOHSIANG/openpilot-carrot/blob/796633626c61ef0fa9486ba0898a970b99f2d31a/docs/carrot_navi_7714_branch_comparison.md) · [Mac HUD 更新紀錄](https://github.com/FANHAOHSIANG/carrotMAC-HUD/blob/4236ce3e751daaaf29e46c308390eef13e083b1a/README.md)〕
