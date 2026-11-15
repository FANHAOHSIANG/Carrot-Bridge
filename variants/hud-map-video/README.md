# Android 高德 HUD 影像試作

Carrot Bridge 可以將已啟動投屏的高德車機版或一般版分區，以最高 5 FPS 的 JPEG 影像送到 comma 的 Navi v2 `render:map_main`。畫面保留高德本身的地圖、路線與畫面上的提示。試作只取高德的投屏分區，畫面經現有區網連線送出。開關預設關閉。

## 停車測試

1. 安裝用原簽章簽署的測試 APK。開啟 Carrot Bridge，確認已連到支援 `render:map_main` 的 comma 測試版。
2. 選擇高德車機版或高德一般版並啟動投屏。在導航分區的選單勾選「HUD 地圖影像（測試）」，用高德開始導航。
3. 分別測試 comma 直連 HUD 和 CarrotMacHUD 轉接。在模式 7 與全導航查看高德畫面及路線。接收 JPEG 的支援情況取決於實際安裝的 HUD 版本。
4. 關閉影像選項、停止導航或切換來源，確認高德影像退場。分別以兩個高德來源重試。

這是測試分支，請先在停車時確認。影像多少會增加 Android 投屏負擔，畫面可能延遲。這項試作透過既有地圖影像接收器對接模式 7 與全導航。模式 1、5 的畫面是否能沿用各自的配置顯示地圖或提醒，仍需驗證。

## 建置

以 GitHub Releases 的 `wide.70` APK 為基底。建置工具會核對 APK 的 SHA-256，組裝後再確認只有 `classes.dex` 的內容發生變動，以及 ZIP 完整性和對齊。

```bash
python3 variants/hud-map-video/build.py wide70.apk Carrot-Bridge-hud-map-test-unsigned.apk \
  --android /path/to/android-35/android.jar \
  --apktool /path/to/apktool_2.12.1.jar \
  --d8 /path/to/r8.jar \
  --zipalign /path/to/zipalign
```

驗證時使用 Python 3.11+、JDK 21、D8 8.7.18 和 Android Build Tools 35。輸出是未簽 APK，維持 wide.70 的套件名稱與版本。若要覆蓋同版本，請用原本的 Android 簽章簽署。若車機上的版本較新，請先確認相容的版本與升級路徑。
