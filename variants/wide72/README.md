# Carrot Bridge wide.72

分區一是地圖投屏，分區二是神盾或其他 App 投屏。分區選單提供「關閉分區二」。切換會重建畫面並記住選擇。單區模式可以從地圖右下角的「⋯」選「顯示分區二」。

以已測試的 wide.71 APK 為基底，SHA-256 為 `d7753d027d3ddcefd5dfa1805eeb0789db69940617e8dd2c8e782fd577ed2143`。以 JDK 21、Python 3.12、Android SDK 35 及 Apktool 2.12.1 執行：

```sh
python3 variants/wide72/build.py WIDE71_APK TOOLS APKTOOL_JAR Carrot-Bridge-wide.72-unsigned.apk
```

使用原簽章與 [簽署工具](../wide55/sign.py)。APK 結構與 34 項道路速限離線檢查已通過，實機啟動、切換、旋轉與投屏銜接待驗證。
