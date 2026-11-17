# wide.78：恢復高德車機版原生預調／智慧調速（測試版）

基於使用者驗收的 wide.77；保留日夜切換、分區重啟與測速紅光修正。wide.77 仍是正式 Latest，本版需要實車驗證，請小心使用。

## 使用條件

1. Android 安裝原簽章 wide.78，可覆蓋 wide.77；選用「高德車機版」並開啟原生「預調／智慧調速」。本版沿用原生策略與道路類型條件，沒有另寫通用彎道演算法。高德一般版、Google NOO 不在本次恢復範圍。
2. comma 更新 `FANHAOHSIANG/openpilot-carrot` 的 `test/carrot-wip-upstream-20261104` 或 `test/tony-carrot-wip-integrated-20261117`，並重新啟動。**只更新 APK，舊車端不會採用新增欄位。**
3. Carrot Web 的導航減速主設定 `AutoNaviSpeedCtrlMode` 必須大於 0；0 會停用此預調建議。不需要改動轉向設定。App 導航連線、有效引導與車端縱向控制仍須可用。
4. 預調另走獨立速度欄位，不要求為此開啟 TDX／OSM 道路速限傳送。原有道路速限、測速與 ATC 仍各自處理；較低限制優先。

## 恢復的行為

例如道路速限 100、原生策略建議 60，車端保留道路速限 100，以獨立 `pre` 候選參與目標速度選擇；若測速或轉彎要求 40，40 仍優先。這不會把巡航設定直接調高，也沒有新增 HUD 畫面。

App 將原生策略產生時間一起傳送，拒絕舊結果及地圖切換前結果。車端以「發送前策略年齡＋接收後單調時鐘經過時間」限制有效期為 2 秒；網路傳輸耗時不在此計算內，兩端不需同步時鐘。停止導航、偏離路線、斷線或過期會撤銷本項候選。新接收端也相容舊 App（沒有預調資料就不採用）。

## 驗證與限制

- App 19 項離線檢查通過：來源、有效期、切換、無效目標、不改寫速限。
- 車端 73 項離線測試通過：實際 Cap'n Proto 編解碼、完整 CarrotServ 更新與發布、快取結果過期、較低限制仲裁，以及既有導航回歸。
- `tools/check_pre_adjust_portable.py` 使用原始服務方法與實際訊息格式，隔離原生 Params／socket／車輛硬體。未代表實車縱向控制已驗收。
- APK 與 wide.77 的非簽章檔案僅主 DEX 和版本資訊有變動；未更換投屏服務或原有紅光實作。

## 可重建來源

`build.py` 使用 SHA-256 固定的 wide.77 APK、既有 `variants/wide69/Dalvik.java`、apktool 2.12.1、Android 15 build-tools 與 org.json 20240303。測試替身僅供編譯／測試，不封裝進 APK。私有簽章不存於此目錄。

```bash
python3 variants/wide78/build.py wide.77.apk /path/to/build-tools /path/to/apktool.jar /path/to/json.jar wide78-unsigned.apk
```
