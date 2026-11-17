# wide.77｜日夜模式切換保留投屏

## 本次修正

wide.76 主 Activity 的 `configChanges=0x40001da0` 沒有 `uiMode`。
車機進入隧道、自動切換深色主題時，Android 預設會銷毀並重建主 Activity。
既有 `WideDirect.Pane.onDetachedFromWindow` / `onSurfaceTextureDestroyed`
會停止投屏 session，因此兩個 App 可能一起重開、導航路線中斷。

wide.77 為**主 Activity**補上 `uiMode|keyboard|navigation`，新值 `0x40001ff0`。
繼續呼叫既有 `Ug.onConfigurationChanged`，保留 Android 資源更新與 Compose
設定變更通知，不鎖住白天主題、不關閉車機自動夜間模式。Google 導航 Activity
原本已有這三項，本次不變。

另修正分區二選單：重選目前同一個 App 時只關閉選單，保留投屏；選不同 App
仍依原流程切換。保留手動重新連線入口。

## 其他重啟因素核對

| 情況 | 程式核對結果／處理 |
| --- | --- |
| 日夜主題／車用 UI 模式變更 | 本版補上主 Activity 的 uiMode 處理，消除這項設定造成的預設重建。 |
| 鍵盤／導覽輸入硬體變動 | 本版補上 keyboard、navigation；不等於修改導航路線。 |
| 旋轉、螢幕尺寸、最小尺寸、螢幕布局、密度、字體縮放 | 原本已有對應 configChanges，這次保留。 |
| 分區二關閉／恢復 | 保留 wide.75 Compose 即時布局修正，沒有 Activity.recreate 呼叫。 |
| 拖曳分區、顯示尺寸改變 | 既有 resizeDisplay/finishResize 在同一 session 上調尺寸；IME 顯示時會延後縮放。被投屏 App 對尺寸改變的處理仍由該 App 決定。 |
| 重選相同分區二 App | 本版新增相同 package 判斷，避免無意義重建。 |
| 重選相同地圖來源 | WideVariant.select 原本已有相同來源直接返回的保護。 |
| 手動重新連線、換不同導航／分區二 App、切換投屏鍵盤位置 | 既有明確 restart 路徑；不取消必要的重建。切換鍵盤位置目前仍會重新連線，請在開始導航前設定。 |
| 投屏服務 Binder 改變、授權或服務中斷 | 既有程式會重建連線；相同 Binder 的重複連線回報原本已有去重。 |
| View 被真正移除、Surface 被銷毀 | 會關閉 session 並釋放 Surface；本版避免 uiMode 導致這條路徑，未讓失效 Surface 永久存活。 |
| 語言／文字方向變更 | 本版未攔截，仍可能重建。 |
| 系統清除背景程序、車機休眠／斷電、導航 App 自身崩潰或自行重建 | 本版無法保證保留第三方 App 路線，需對應裝置紀錄確認，不能宣稱全部重啟都已解決。 |

## 驗證與安裝

- 以原簽章 wide.76 APK 重建；承接 wide.76 測速紅光修正。
- versionCode 26110789、versionName wide.77；可直接覆蓋安裝。
- 實際 binary manifest 檢查：12 組處理情境、3 組未攔截對照、其他 Activity 屬性及非目標 bytes 保持不變。
- 檢查繼承的設定變更回呼仍轉送 Compose，DEX 重組與 APK ZIP/16 KiB 對齊檢查。
- **尚未完成車機／模擬器的日夜切換實測。** 這是測試版，請小心使用。

停車後先開始導航並保留分區二，在車機系統手動切換白天／夜間數次，確認兩個
App 沒有啟動畫面、導航目的地與路線仍在；分區二關閉與開啟各做一次。
之後再確認實際隧道切換。若仍重啟，需要紀錄當時是否整個 Carrot Bridge
重開，或只有高德重開，以區分主程式與第三方 App／車機系統行為。

重建（JDK 21、Apktool 2.12.1、Android build-tools 35.0.0）：

```sh
python3 variants/wide77/build.py Carrot-Bridge-wide.76.apk /path/to/android-15 /path/to/apktool.jar wide77-unsigned.apk
```

官方參考：[處理設定變更](https://developer.android.com/guide/topics/resources/runtime-changes)、
[Activity configChanges](https://developer.android.com/guide/topics/manifest/activity-element#config)、
[深色主題](https://developer.android.com/develop/ui/views/theming/darktheme)。
