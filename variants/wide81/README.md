# Carrot Bridge wide.81｜完整投屏自啟流程（測試）

本版在 wide.77 正式版 APK 為基底套用 wide.79 共用導航預調，加入經過使用者授權的投屏全自動接續邏輯。**不包含 wide.80 在 Pane 掛載時重複觸發啟動的 hook**；使用 WideProjectionHelp 原本每 1.5 秒的輪詢機制，不重複發起投屏請求。

## 實際行為

1. 開啟 Carrot Bridge，記住 **分區一＝左側導航**與**分區二＝右側神盾／其他 App** 的選擇。
2. 若 Shizuku／Stellar 服務正在運行、Bridge 以前已被授權：由既有重連邏輯主動啟動投屏，**不需要點「啟動投屏」**。
3. 若服務尚未運行：沿用原本的「自動開啟管理工具」設定，只啟動一次管理工具；不能代替 Android 啟動 Shell 權限服務。
4. 若服務晚於 Carrot Bridge 才啟動且尚未授權：主動觸發原本的授權／啟動 callback **一次**，讓 Shizuku／Stellar 顯示正常的使用者授權提示；**不會自行同意授權，也不會在被拒後反覆要求**。
5. 首次授權成功後，既有 Policy 最多嘗試五次連線，每次間隔至少 5 秒；當已有投屏、服務失效、或 App 不在前景時停止重試。
6. 重新啟動 App 後，若系統仍保存永久授權且服務可用，全部自動恢復。Stellar 管理器本身的開機自啟與其「跟隨 Stellar 服務啟動」權限仍須在管理器內配置。

## 重要限制

- 無 root 或系統級權限時，Android **禁止第三方 App 默默核准自己的 Shizuku／Stellar 權限**。本版會自動「發起」授權請求，但第一次授權／權限被系統撤銷／被使用者拒絕仍需使用者同意。
- 官方 Shizuku 以無線偵錯或 ADB 啟動，重開裝置後通常需要重新啟動服務；Carrot Bridge 無法自行憑空取得 ADB 授權。
- 此次只動投屏重連 policy，不修改導航、車控或其他權限。
- 建置與 host-only 結構測試通過不等於車機實測；未實測前不合併 main。

## 建置
```sh
python3 variants/wide81/tests/test_patch.py
python3 variants/wide81/build.py Carrot-Bridge-wide.77.apk /path/to/build-tools/35.0.0 /path/to/apktool.jar /path/to/json.jar Carrot-Bridge-wide.81-unsigned.apk
```

**原簽章更新說明：** GitHub Actions 只編譯未簽章 APK，不公開 keystore、密碼或私鑰。必須由原版簽章完成後比對 wide.77 憑證指紋，才能發布可覆蓋安裝的 APK。