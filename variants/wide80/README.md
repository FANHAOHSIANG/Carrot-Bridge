# wide.80｜開啟 Carrot Bridge 自動恢復上次投屏（測試）

這是建立在 wide.79 上的**測試版**，不會覆寫已驗收的 wide.77 正式版，也不修改分區、Google SDK、導航資料與車控邏輯。

## 預期行為

- **分區一（左側導航）**沿用 `copilot_tw_projection/navigation_package` 保存的高德車機版、高德一般版、Google 地圖或 Google NOO 來源，重開後維持上次選擇。
- **分區二（右側 App）**沿用 `copilot_tw_projection/side_package` 保存的神盾或其他 App；選空白／時鐘、或關閉分區二時不開右側 App 投屏。
- 當 Carrot Bridge 畫面掛載、投屏管理服務（Stellar 或 Shizuku）已連線、且目前沒有投屏 Binder 時，主動呼叫**原本「啟動投屏」的 callback**。建立連線後由現有 `WideDirect.connected` 路徑恢復兩個分區。
- 如果管理服務尚未啟動，保留現有 `WideProjectionHelp` 的自動開啟管理工具和有限重試流程，不會直接跳過授權。
- 已有投屏時不重連；由分區一（左側導航）的內部 map pane 提出一次啟動請求，分區二（右側 App）的內部 shield pane 不重複請求。手動切換和重試維持可用。

## 權限前提

第一次使用或 Android 撤銷 Shizuku/Stellar 授權後，仍必須遵守系統權限確認；不聲稱能靜默越過權限。車機完全斷電／管理服務停止時，自動投屏取決於管理服務能否重新啟動。

## 測試和建置

以原始簽章的 wide.77 APK 為基底，先套用 wide.79 的共用導航預調修補，再套用本版的 **Pane 掛載自動連線 hook**。鎖定基底 SHA-256，避免對錯版 APK 注入。

```sh
python3 variants/wide80/tests/test_patch.py
python3 variants/wide80/build.py Carrot-Bridge-wide.77.apk /path/to/build-tools/35.0.0 /path/to/apktool.jar /path/to/json.jar Carrot-Bridge-wide.80-unsigned.apk
```

GitHub Actions 先編譯未簽章 APK，再簽署並上傳**測試用 APK** 至預發行版。若使用獨立測試簽章，Android 無法直接覆蓋既有正式版，須先備份設定並移除舊版；如可取得與正式版相同的私鑰才可直接覆蓋更新。

車機實測依序確認：

1. 已有授權且 Stellar／Shizuku 開啟 → 強制結束 Bridge，重開後自動恢復兩分區，不按「開始投屏」。
2. 分區二換神盾或任意其他 App → 關閉、重開後恢復同一 App；改為時鐘或關閉分區二則不啟動右側投屏。
3. 分區一在高德車機版／高德一般版／Google 間切換 → 重開保留原選擇，並確認沒有重複啟動、閃屏或黑屏。
4. 管理服務關閉時啟動 Bridge → 恢復服務及授權後可以重連；未授權時只呈現正常權限流程。
5. 日／夜模式切換、收合或重新開啟分區二 → wide.77 已修復的連線不中斷特性維持。

驗證層級：wide.80 已通過 host-only 自動測試、19+25 項既有導航檢查及 APK 對齊／完整性檢查；[初始建置紀錄](https://github.com/FANHAOHSIANG/Carrot-Bridge/actions/runs/45241392612)。可安裝測試 APK 由後續發行流程產生。**尚未完成 Android 車機安裝及實車測試。**
