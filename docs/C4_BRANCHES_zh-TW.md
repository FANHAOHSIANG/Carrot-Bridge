# Carrot Bridge × C4：官方與個人測試分支

[回首頁](../README.md) · [App 功能](FEATURES_zh-TW.md) · [測試分支安裝](C4_TEST_INSTALL_zh-TW.md)

**官方**在本文指 ajouatom 的 Carrot `carrot-wip`，不是 comma.ai 原版 openpilot；官方 Carrot 本身亦為滾動開發分支。

## 核對版本

| 元件 | 核對基準（2026-11-15） |
| --- | --- |
| Android | Carrot Bridge wide.70；main `4e7190bdc3e503e9d64b045eda259cfbf8be6db1` |
| 官方 Carrot | ajouatom/openpilot `carrot-wip`，`baab16bb9666eb51a5047aaa586e4517c6155a40` |
| 個人測試 | FANHAOHSIANG/openpilot-carrot `test/carrot-wip-upstream-20261104`，`796633626c61ef0fa9486ba0898a970b99f2d31a` |

表格是此版本快照。官方後續可能納入相同修正；舊比較文件的歷史表格不能當成目前分支行為。

## 使用體驗比較

| 功能 | 官方 Carrot | 個人測試分支 |
| --- | --- | --- |
| 高德／Google／神盾投屏 | Android 自己完成，可不接 C4 | 相同 |
| Google NOO 搜尋與規劃 | App 內完成 | 相同 |
| Navi v2 轉彎、距離、道路速限 | 有接收及處理路徑，需來源實際提供 | 保留原有基礎功能 |
| ATC 轉彎減速與轉向資訊 | 有對應設定和候選處理 | 保留；不是測試分支獨有 |
| 導航路線彎速 | 已有 route 選擇、曲率及速度候選 | 新增路線／定位／方向／近端視覺配對，依距離形成速度上限，並處理出彎釋放 |
| 高德一般版長路線 | cereal／control 上限為 256 點，會截斷 | 完整接收最多 4,096 點；超限或任一座標無效則撤銷 |
| 高速直線短折返 | 原有曲率處理 | 已納入特定短折線誤減速修正，不代表所有 ROUTE 誤判均已消失 |
| 未設目的地的彎速預覽 | 未見本專案這套離線 OSM 模組 | `OsmCurveSpeedEnabled`，使用 C4 本機圖資及道路配對；有導航路線時優先用導航 |
| 高德手機倒數、USB HUD | 依上游現有支援 | 已合併車端中性倒數、三燈／測速顯示配套，仍需相符來源與 App 版本 |
| HUD 藍線穩定修正 | 現有路線／模型／HUD 管線 | PR #41 核對時仍 open、draft、未合併；不得宣稱已修好 |
| 實車效果 | 隨車型、設定、模型與來源不同 | 離線修正不等於實車保證；須逐項驗收 |

**導航資料、畫面指示、實際車輛動作是三個層次。** 接到左／右轉，可能產生 ATC 引導或速度候選；是否轉向還取決於模型與橫向支援。車外方向燈另需車型、線束、SPAS 或其他支援路徑，不因安裝本 App 或測試分支自動獲得。尤其不能由某一車型可用推論同名車款／年份全部可用。

## C4 設定與操作

先停車確認原本 C4 控制正常，再接入資料。設定頁名稱可能依語言或版本不同，以下參數識別碼供核對，**不要求一次全開或覆寫既有設定**。

| 目的 | App 操作 | C4 設定／條件 | 期待觀察 |
| --- | --- | --- | --- |
| 只用投屏 | 選地圖及分區一 App | 不必換分支 | 正常畫面、觸控與語音 |
| 接收導航 | 高德開始導航／Google NOO 開始導航，核對 Navi v2 | 同網路可互通，接收服務運作 | 轉彎、距離、停止撤銷在車端更新 |
| 轉彎前減速 | 提供有效轉彎及距離 | `AutoTurnControl` 的 2／3 可產生轉彎速度候選；需可用的縱向控制 | ATC／turn 候選與距離變化，不保證一定達固定轉彎速度 |
| 導航轉向資訊 | 同上 | `AutoTurnControl` 的 1／2 保留 ATC 類型；3 為速度處理、不保留該轉向類型 | 僅代表車端資訊路徑；實際轉向、車外燈另查硬體與控制支援 |
| 道路速限 | 開啟「傳送道路速限至 C4（TDX／OSM）」 | `AutoRoadSpeedLimitOffset >= 0`、有效道路速限及導航狀態等條件 | road 候選；App 圓牌與車端採用分別確認 |
| 導航相機減速 | 來源必須真的提供有效相機類型、速限及距離 | `AutoNaviSpeedCtrlMode > 0` 等原有條件 | cam／section 等候選；不適用於未傳出的神盾辨識 |
| 視覺＋導航彎速 | 來源提供有效路線 | `TurnSpeedControlMode=2` 包含視覺與路線；仍受資料與模式條件限制 | vturn／route 候選，取最終允許的速度上限 |
| 測試分支離線 OSM 彎速 | App 不必設目的地 | 開啟 `OsmCurveSpeedEnabled`，模式 2／3／4 有幾何路徑，圖資有效且道路配對通過 | 無導航路線時可供速度預覽；不設定目的地、不提供導航轉彎或方向燈 |
| C4 USB 直連 TURZX HUD | 來源與版本提供對應顯示資料 | 既有 `ClusterHud=1` 及相容接線／HUD | 駕駛摘要、系統資訊中的提醒；不是號誌煞停控制 |

`AutoTurnControlSpeedTurn` 是轉彎速度計算的設定之一，並非保證每個彎都精確降到該值；跟車、其他上限、駕駛操作、實際縱向控制都會影響車速。App 與官方 C4 的這些設定是傳送端及接收端的不同條件，不會因 App 打開開關就自動改寫 C4 設定。

### 測試分支離線 OSM

停車保持 C4 開機、連上非計量 Wi-Fi，依 Carrot Web 的 OSM 狀態確認圖資下載完成。範圍包含台灣本島及離島；不要把「已開啟功能」當成「已下載全部圖資」。路段不明、高架／平行道路歧義、定位或圖資無效時可能不參與。關閉 `OsmCurveSpeedEnabled` 可停用這項補充來源，導航路線本身仍按既有設定處理。

此處僅是速度預覽，不會因道路看起來向左就自行設定目的地或保證車輛左轉。App 的 OSM 速限圓牌和此功能分開。

### HUD 與版本限制

測試分支已有高德 Link 倒數和 USB HUD 車端配套；對手機 Link，只有確認過的中性秒數，不猜紅／綠燈，且不連接號誌煞停控制。車端文件提到 wide.71，但本次查到最新正式發布 APK 仍是 wide.70，所以不能把後續功能寫成 wide.70 安裝後即有。

Google NOO、兩種高德使用不同畫面及資料來源；收到幾何路線不等於能像 Mapbox 一樣完整顯示 HUD 導航地圖。C4 直連 HUD 與經 CarrotMacHUD 轉送也須分別核對接收／顯示版本。PR #41 藍線修正未合併，維持獨立驗證。

## 第一次接入的檢查順序

1. 記下目前 C4 分支、提交及設定，確保能回到已知可用版本。
2. 停車設定一條導航，核對 App 的來源、引導、路線與 Navi v2。
3. 核對 C4 的轉彎與距離；改選路線、停止導航及斷線後，確認舊資料會撤銷。
4. 再逐項確認需要的車端設定。記錄 App、C4 的同時間資料，不以畫面或送出計數單獨判定控制成功。
5. 出現異常減速、偏移、失去提示或程序警告時立即接管、停止該項測試，保留紀錄。不要在行駛中改設定。

## 核對依據

- [官方 Carrot README 與發布政策](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/README.md)。
- [官方 CarrotServ：ATC、速限、模式條件](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/carrot_serv.py)。
- [官方 CarrotMan：路線選擇與既有曲率](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/carrot_man.py)。
- [官方接收解析上限](https://github.com/ajouatom/openpilot/blob/baab16bb9666eb51a5047aaa586e4517c6155a40/openpilot/selfdrive/carrot/carrot_navi_control.py)。
- [測試分支路線／OSM 整合](https://github.com/FANHAOHSIANG/openpilot-carrot/blob/796633626c61ef0fa9486ba0898a970b99f2d31a/openpilot/selfdrive/carrot/carrot_man.py)。
- [測試分支接收上限及倒數](https://github.com/FANHAOHSIANG/openpilot-carrot/blob/796633626c61ef0fa9486ba0898a970b99f2d31a/openpilot/selfdrive/carrot/carrot_navi_control.py)。
- [ROUTE 短折返修正與離線驗證範圍](https://github.com/FANHAOHSIANG/openpilot-carrot/blob/796633626c61ef0fa9486ba0898a970b99f2d31a/docs/route_short_reversal_20261115_zh-TW.md)。
- [高德 USB HUD 合併說明](https://github.com/FANHAOHSIANG/openpilot-carrot/blob/796633626c61ef0fa9486ba0898a970b99f2d31a/docs/carrot_navi_7714_branch_comparison.md)。
- [PR #41 當前狀態](https://github.com/FANHAOHSIANG/openpilot-carrot/pull/41)。
