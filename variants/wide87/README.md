# wide.87 車機版被動診斷採集

沿用 wide.86 一般版 Link、48 MB 輪替與既有診斷開關，新增 amap_auto_packet：在既有來源驗證接受 AUTONAVI_STANDARD_BROADCAST_SEND 後、原解析前紀錄 key_types、數值、候選路線／車道／HUD／定位／ADAS／JSON 欄位、單調時鐘與截斷標記。保留 KEY_TYPE 與候選原始編碼，不猜測方向或座標系。未獲 Android 發送者資訊時沿用既有來源過濾，不能視為密碼學身分證明。每秒最多 12 筆，節點、文字、陣列有限制，私密欄位與未知文字遮蔽，位置資訊仍敏感。既有來源選擇不變；不是同時訂閱兩套導航。

APK 靜態線索：nativeGetRouteInfo、RoutePointlist、jniSendArHudRouteInfoData；JsonProtocolService、ProtocolService、AmapAutoService 的存在不證明第三方具備授權。未新增 Binder 呼叫、主動廣播、電子地平線或原生車道中心線輸出。先用已收到的實車廣播確認 10001、13012 等實際事件及資料，再研究正常授權的服務。未改變任何車控、HUD 或 Navi v2。停車開啟紀錄、選擇高德車機版、正常使用後停車匯出，另附同時段 C4 rlog。不可公開含位置的 ZIP。
