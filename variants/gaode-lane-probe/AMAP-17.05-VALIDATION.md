# 高德 17.05.0.2005 — GaodeProbe 驗證紀錄

使用者提供的原始 APK：amap-global-17-05-0-2005.apk，SHA-256 `544f31054a75820eb683a1e8f8f8e5bf4c13db6bb1a9fde60d41cc7e295dba0d`，180677842 bytes，9 DEX。Manifest package=com.autonavi.minimap，versionCode=170500。

## 實際 DEX 類別定義
- com.amap.ams.IAMSLocationService: addLaneMatchInfoCallback(ILaneMatchInfoCallback):void、removeLaneMatchInfoCallback(ILaneMatchInfoCallback):void
- com.amap.ams.aidldefine.ILaneMatchInfoCallback: onLaneMatchInfoReport(LaneMatchInfo):void、onLocationStatusReport(LocationStatus):void
- LaneMatchInfo: accuracy:F、altitude:D、bearing:F、laneMatchData:[B、speed:F、tickTime:J、updateUtcTime:J、sourceType:I、sourceSubType:I
- com.autonavi.jni.ae.pos.LocPlaneMatchInfo: coarseLatitude:I、coarseLongitude:I、laneIdx:I、lateralDis:I、longitDis2Start:I、state:I
- com.autonavi.jni.ae.guide.model.LaneInfo: backLane:[I、frontLane:[I、laneCount:I、pointLat:D、pointLon:D

Manifest: AmapLinkService exported=true；AmapLocationSubService exported=false。類別存在不等於可正常存取或台灣有有效資料。L2/L4 暫不啟用，不猜測車道索引或偏移單位，不改原廠 APK/權限。

## 實際可測試的方案
保留 wide.85 與原高德，正常授權 Link，停車開啟事件紀錄；人工駕駛，停車匯出 ZIP。在 Mac 使用獨立 GaodeProbe v0.2 Python 診斷套件（由對話附件交付，未上傳此分支）匯入 ZIP，查看候選欄位、路線完整性、來源代次、時效與截斷。僅 localhost；不接 C4 控制。/stream 為單次歷史快照，不是 live。

本次 Python 套件實際執行 10 個單元測試全通過、7 個 HTTP 路徑回傳 200；舊 Navipilot 真實 ZIP 可讀但無 amap_link_packet。尚無新高德版本實際車道事件；不能宣稱高精定位或 NOO 精度提升已驗證。

下一驗收：正常授權 Link 封包數、車道欄位覆蓋率、推薦與實際車道區分、車道索引方向、座標系與時間對齊、路線切換與缺資料時撤回。HUD/NOO 影子觀察需真實樣本後另行驗證。正式 APK/C4/Mac HUD 均不修改。
