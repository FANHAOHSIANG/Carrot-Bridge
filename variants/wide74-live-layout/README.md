# wide.75 分區二即時切換

「關閉分區二／顯示分區二」使用 Compose 的可觀察版面狀態，取代原先的 Activity 重建。分區一沿用原本的 AndroidView 與投屏工作階段，尺寸交由現有虛擬顯示器調整流程處理。分區一右下角的恢復選單只在全幅時顯示，版面偏好存入原本的設定。

[下載已簽署的 wide.75 APK](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/download/wide.75/Carrot-Bridge-wide.75.apk)

## 建置

以 GitHub Releases 的 wide.74 APK 為基底，使用 JDK 21、Python 3.11+、Apktool 2.12.1 及 Android Build Tools 35 的 zipalign。

```sh
python3 variants/wide74-live-layout/build.py Carrot-Bridge-wide.74.apk Carrot-Bridge-wide.75-unsigned.apk \
  --apktool /path/to/apktool_2.12.1.jar --zipalign /path/to/zipalign
```

建置更換兩個 DEX、更新 APK 至 wide.75，並重新對齊。套件名稱沿用 wide.74。需以原簽章簽署才能覆蓋原 APK。

## 實機驗收

在車機開啟導航後，分別測試關閉及顯示分區二。確認分區一全幅與分割互換、導航仍進行、地圖沒有回到啟動畫面，並確認全幅下能開啟恢復選單。有接 HUD 時，另核對轉送影像在調整後繼續更新。Android 或高德若在虛擬顯示器尺寸改變時自行重建畫面，仍須依實機紀錄確認。
