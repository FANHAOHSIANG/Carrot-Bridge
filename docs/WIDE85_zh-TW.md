# wide.85｜版本說明、配套與驗證

[回首頁](../README.md) · [安裝](INSTALL_zh-TW.md) · [功能](FEATURES_zh-TW.md) · [Release](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/tag/wide.85)

## 版本定位

wide.85 是 Android App 發布版本，沿用已簽署的原 APK，不更換簽章或重建發布附件。正式版名稱指 App 的公開發布層級，不代表已完成每種車機、導航來源或實車控制驗收。

- 版本名 wide.85；Android versionCode 26110797；Android 12 以上。
- APK：Carrot-Bridge-wide.85.apk。
- SHA-256：`344ae6f633a70e92923b627e664e927fda714dca37e8e098e21004ec94a33483`。
- 原簽章憑證 SHA-256：`eb0f6a44174aecf09cedc237be2ca0305ea491d47b381407d31e903acbd34b46`。
- 同簽章舊版可覆蓋安裝；未驗收裝置先保留備份。不要把 Source code ZIP 當成 APK。

## 新功能

- 保留 wide.83 自動投屏、wide.84 高德路線欄位，新增 `BRIDGE_OBS_VERSION`、`BRIDGE_OBS_SESSION`、`BRIDGE_OBS_SEQUENCE`。觀察資料在來源切換、中斷或無有效樣本時重設。
- 高德車機版的 `EXIT_NAME_INFO`、`EXIT_DIRECTION_INFO`、`SEG_REMAIN_DIS`、`CUR_SEG_NUM`、`CUR_POINT_NUM`、`CUR_ROAD_NAME`、`NEXT_ROAD_NAME`、`ROAD_TYPE`、`ICON`、`NEW_ICON`、`CAR_DIRECTION`、`EXTRA_DRIVE_WAY`、`ROUTE_REMAIN_DIS`、`ROUTE_ALL_DIS`、`ROUTE_REMAIN_TIME` 及格式化字串以實際收到的有效值為準。
- 這些欄位位於現有 Navi v2 的可選 `amap_exit_info`，scope 為 display_only；兩個 C4 分支接收後保留於 `carrotNavi.amapExitInfo.fieldsJson`。檢查時效及選定來源，不新增車控權限。
- HUD 模式 6 顯示出口名稱，並可附明確方向文字及合法格式的剩餘路程。未知數字方向與車道代碼不直接解讀。沒有新資料或逾時則隱藏。
- 觀察工作階段不是穩定的 route ID、event ID 或匝道結束判定。**新版 PRE 實際控速、線性升降速未啟用。** 既有車控保持原分支策略。

## 建議搭配及可追溯版本

| 元件 | 版本快照（2026-11-26） |
| --- | --- |
| Android 已簽 APK | [wide.85 tag 與原始碼](https://github.com/FANHAOHSIANG/Carrot-Bridge/tree/wide.85) |
| 獨立 Test | [15a81ff](https://github.com/FANHAOHSIANG/openpilot-carrot/commit/15a81ff840cc6a1e92519f6e0d4463e37db23f32) |
| Tony 融合 Test | [5eda71a](https://github.com/FANHAOHSIANG/openpilot-carrot/commit/5eda71aad247220246bc8b662b6d5642e9c481fb) |
| Mac HUD | [204b941](https://github.com/FANHAOHSIANG/carrotMAC-HUD/commit/204b94185a7c11fc11e5e790b7b7b5c861e001ca) |

C4 Test 與 Mac main 為滾動分支，快照不等於目前 HEAD。直連不需要 Mac；Mac HUD 請退出 Jetlink 後執行原更新工具 Update-HUD-Zh-TW.command，既有補丁版本不符時先檢查，勿強制覆蓋。新 Swift 建置因 ONNX 下載端 TLS 憑證失敗，未替換原本可用的 Jetlink。

## 已完成的驗證

- [wide85 編譯與 Java 檢查](https://github.com/FANHAOHSIANG/Carrot-Bridge/actions/runs/45754440065)
- [APK 原簽章、重建、對齊檢查](https://github.com/FANHAOHSIANG/Carrot-Bridge/actions/runs/45754827016)
- [獨立 Test Navi v2 相容性](https://github.com/FANHAOHSIANG/openpilot-carrot/actions/runs/45754492586)
- [Tony Test Navi v2 相容性](https://github.com/FANHAOHSIANG/openpilot-carrot/actions/runs/45754513562)
- [Mac HUD 補丁相容性](https://github.com/FANHAOHSIANG/carrotMAC-HUD/actions/runs/45752768203)

尚未完成：wide.85 車機自動投屏實測、各來源真實廣播覆蓋與匝道判定、線性升降速閉迴路及封閉場地驗收。實際車速不能以目標速度離線回放代替。

## 回報資料

停車匯出「即時診斷 → 報告 → 匯出報告與事件 ZIP」，並附同時段 C4 Log、APK 版本、車機／Android／地圖版本、C4 分支及提交。觀察識別碼出現在有效 Navi v2 封包時，能比對樣本先後；不要公開私密位置、帳密或連線資訊。
