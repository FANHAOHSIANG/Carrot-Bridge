# 官方 Carrot 設定建議

[回首頁](../README.md) · [外接 HUD 畫面](HUD_zh-TW.md) · [官方與測試分支比較](C4_BRANCHES_zh-TW.md)

適用於使用 ajouatom 官方 `carrot-wip` 的 **C3、C3X 與 comma four**。以下設定以 2026-11-15 核對的 `baab16bb` 為準。已有正常使用的車型、線束、方向盤和縱向控制設定，先備份，再按需要一次調整一項。

## 從哪裡設定

1. 停車，將 Android 與 comma 接上可互通的 Wi-Fi 或熱點。用 comma 畫面上的白色蘿蔔圖示開啟 Carrot Web QR Code，或從同一網路打開 `http://<comma 的區網 IP>:7000`。
2. 在 Carrot Web 選「設定 → carrotpilot」。可按下表的位置找功能，或以欄內的設定名稱搜尋。名稱可能隨顯示語言改變。
3. 在 Carrot Bridge 的連線設定填 comma 的位址，選高德車機版、高德一般版或 Google 導航 NOO，開始一條路線。先核對 App 即時診斷的來源、引導、Navi v2，再看 comma 或 HUD 是否收到相同的轉彎、距離。切來源或停止導航後確認舊提示消失。

本機 Carrot Web 使用 `7000`，Carrot Navi v2 使用 `7714`。在 App 依欄位輸入 comma 的位址。〔[Carrot Web 連接步驟](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/docs/user/en/carrot-web.md#connecting) · [Navi v2 通訊](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/carrot_navi_api.md#1-connection-overview)〕

## 第一次用，依目標選一種

| 想要的體驗 | 起步建議 |
| --- | --- |
| **只看 USB HUD** | 接好相容 TURZX。`ClusterHud=1`、`ClusterHudScreenMode=0`、`ClusterHudCameraViewMode=0`、亮度與編碼器都先用 `0`（自動）。原有駕駛參數沿用已驗證的設定。 |
| **看導航和轉彎提示** | 先停車確認 App 與 comma 收件。`AutoTurnControl=0` 可保留引導畫面、關閉 ATC 轉向與減速。若要保留原有視覺彎速並先隔離導航彎速，可用 `TurnSpeedControlMode=1`。第一次比對時先關閉 App 的道路速限傳送。另有原車／導航減速設定時，按下表分別確認。 |
| **想用導航轉彎減速** | 確認 TBT 距離與路線正確，且車輛已有可用的縱向控制，再用 `AutoTurnControl=3` 單獨確認 ATC 轉彎速度。要比較導航路線的彎道速度，再從 `TurnSpeedControlMode=1` 試 `2`。一次只調一項，依 comma 顯示的 `atc`、`route`、`vturn` 辨認實際生效來源。 |

駕駛輔助功能隨車型、線束、模型與設定而異。確認外部導航時先在停車狀態看資料，行駛時留意道路並準備接管。〔[官方速度與減速說明](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/docs/user/en/speed-deceleration.md)〕

## 外接 HUD

官方選單「顯示 → 外接 HUD」（Display → External HUD）。以下值適用於 comma USB 直連。

| 設定 | 怎麼設 |
| --- | --- |
| `ClusterHud` | `1` 開啟相容 TURZX 直連，`0` 關閉。 |
| `ClusterHudScreenMode` | 先用 `0`（導航／行程自動切換）。偏好固定行程用 `5`，系統資訊用 `2`。其他值見[畫面模式表](HUD_zh-TW.md#選擇畫面)。 |
| `ClusterHudCameraViewMode` | 先用 `0`（3D）。想看實景可選 `2` 一般前方相機或 `3` 廣角。 |
| `ClusterHudPanelLayout` | `0` 駕駛左、資訊右。`1` 對調。 |
| `ClusterHudBrightness`／`ClusterHudTheme` | 亮度 `0` 自動，`1` 到 `100` 固定百分比。主題 `0` 自動，`1` 深色，`2` 淺色。 |
| `ClusterHudOrientation`／`ClusterHudMirror` | 顛倒安裝用方向 `2`（180°），正常用 `0`。只有經反射觀看才需要考慮開啟鏡像。 |
| `ClusterHudEncoder` | 優先 `0` 自動。黑屏時先排查 USB 資料線、TURZX 型號及外接 HUD 開關。 |
| `ClusterHudDebug` | 日常用 `0`。若需停車檢查通電畫面，可暫用 `1`，完成後調回 `0`。 |
| `ClusterHudRadarInfo`／`ClusterHudRadarDisplay` | 可依畫面需求選前車速度／距離或更細的雷達點顯示。剛安裝先保留原值，確認資料有更新。 |
| `ClusterNaviMapTheme`／`ClusterNaviMapType`／`ClusterNaviMapFps` | 供有輸出地圖影像的導航來源使用。可先選 `1` 深色、`0` 一般地圖與 `1`（10 FPS）。地圖 FPS 與 HUD 螢幕輸出各自設定。 |

依據〔[官方外接 HUD 說明](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/cluster/README.md) · [官方設定選單](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot_settings.json)〕

## 導航、道路速限與彎速

| 官方設定／位置 | 值與建議 |
| --- | --- |
| **自動轉彎 `AutoTurnControl`**／駕駛 → 轉向 → 變換車道（自動轉彎） | `0` 關閉 ATC，`1` 保留 ATC 轉向類型，`2` 同時啟用 ATC 轉向與轉彎速度，`3` 僅啟用 ATC 轉彎速度。剛接外部導航先用 `0` 看引導，確認只需轉彎減速再試 `3`。實際轉向與車外方向燈受車型與硬體支援影響。 |
| **轉向速度 `AutoTurnControlSpeedTurn`**／同上 | 官方初始值 `20 km/h`。這是 ATC 計算用的參考目標。先用既有已驗證的值，觀察轉彎距離和 `atc`，再依車輛反應調整。實際車速還會受其他速度上限與控制條件影響。 |
| **轉彎前右方向燈加項 `AutoTurnControlRightLaneChange`**／同上 | 第一次接導航留 `0`。此設定用於相容的方向燈硬體、側後車況及 ATC 模式 `1`／`2`，HUD 中的轉彎箭頭與車外燈是兩種資料。 |
| **彎速模式 `TurnSpeedControlMode`**／駕駛 → 速度與減速 → 彎道與轉彎 | `0` 關這組彎速候選，`1` 視覺彎速，`2` 視覺加轉彎點附近的路線彎速，`3` 由有效路線速度提供候選。先比較 `1`，導航與定位核對後再試 `2`。官方模式 `2` 的路線候選只在轉彎距離約 ±500 m 內參與。 |
| **彎道速率 `AutoCurveSpeedFactor`／最低速度 `AutoCurveSpeedLowerLimit`**／同上 | 視覺彎道速率調高，同一彎道的計算目標會降低。先保留原值，必要時以選單一步比較。最低速度會限制彎速候選能降到多低，急彎需要足夠減速時避免提高。 |
| **路線彎速比例 `MapTurnSpeedFactor`**／同上 | 先保留原值。`100%` 方便對照收到的路線目標，調低會降低候選速度，還會受彎速最低速度約束。 |
| **模型速度 `ApplyModelSpeed`**／同上 | 比較導航或視覺彎速時可用 `0`，避免此獨立功能改變巡航設定速度。 |
| **道路速限容許值 `AutoRoadSpeedLimitOffset`**／駕駛 → 速度與減速 → 速限 | `-1` 停用「速限＋偏移」這一個速度候選。想跟隨已確認的道路速限時，在 App 開啟 TDX／OSM 速限傳送，先確認道路、方向和速限正確，再用 `0`。例如道路限速 60，`0` 的候選為 60。獨立的 `AutoRoadSpeedAdjust`／`AutoSpeedUptoRoadSpeedLimit` 也可能影響巡航設定速度，首次比對可先維持 `0`。 |
| **導航測速減速 `AutoNaviSpeedCtrlMode`**／駕駛 → 速度與減速 → 測速照相 | `0` 關閉這組導航事件減速，`1` 固定及區間，`2` 再含減速丘，`3` 再含有效移動測速事件。先核對來源確實交付相機類型、速限及距離，再依需要選模式。沿用已確認可用的原車導航設定。 |
| **測速目標與減速時機**／同上 | `AutoNaviSpeedSafetyFactor=100%` 時目標等於收到的執法速限。`AutoNaviSpeedCtrlEnd` 加大會提早完成減速。`AutoNaviSpeedDecelRate` 較小會提早開始減速，`120` 為官方初始值。先確認來源正確，再一次比較一項。 |
| **導航提示倒數 `AutoNaviCountDownMode`**／同上 | `0` 停止導航事件倒數，`1` 包含轉彎與速度事件，`2` 加入減速丘。這組依距離和車速計算的提示秒數，與高德提供的號誌剩餘秒數分開。 |

`NAVI` 亮起後先看資料是否新鮮，尤其是高架／平面路段、改道和導航停止。只有地圖投屏、神盾紅光或 HUD 顯示並不足以核對減速來源。依 HUD 或 comma 的來源標籤與紀錄確認當下採用了哪個速度候選。〔[官方速度與減速](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/docs/user/en/speed-deceleration.md) · [官方 ATC 與速度候選程式](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/carrot_serv.py)〕

個人測試分支的台灣離線 OSM 彎道預覽使用 `OsmCurveSpeedEnabled`，另需下載圖資與確認道路配對。使用這項功能請先閱讀[分支比較與測試提醒](C4_BRANCHES_zh-TW.md#測試分支離線-osm)。
