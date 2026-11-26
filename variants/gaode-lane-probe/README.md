# GaodeProbe — 高德一般版車道資料探索（獨立測試）

參考 tc-v61-20261118 的 L1/L2/L4、KeyScan、routeEpoch、單調時鐘、HTTP/SSE 診斷架構。此提交是可執行的 **Mac/PC 離線回放工具**，不是高德重打包 APK，也不是 wide.85 新 APK。

## 使用
1. wide.85 停車時開啟原有事件紀錄，選高德一般版並依正常授權導航；匯出診斷 ZIP，於本機解壓。
2. Node.js 18+：在本目錄執行 `node probe.cjs` 自測；執行 `node server.cjs events2.jsonl events1.jsonl events0.jsonl`（依最舊至最新順序，只列實際存在的完整檔案，單次錄製）。
3. 瀏覽 http://127.0.0.1:8888/，搜尋 lane、recommend、HD、topology。/app 是最後一筆來源時間的回放快照，/keys 欄位索引，/events 類型統計，/event?type=77 類型歷史，/stream 為一次性 SSE 快照，不是即時串流。請勿公開紀錄或此頁。

## 通道對應
- L1：重用 wide47 已授權 Link bizType 113 的 amap_link_packet；不修改其 Binder 授權。wide.85 APK 已靜態確認含紀錄器與路線解析類別；是否產出完整紀錄仍以實際匯出確認。
- L2：目前沒有已核對的高德前方車道查詢，不發送猜測請求。
- L4：沒有已核對的 HD 定位追加監聽器，保留 null。
- L3：停用，避免覆蓋原回呼。
- 既有 type2/4/20/19/100/200 路線生命週期依 variants/wide56/SCHEMA.md；車道欄位僅候選，不映射實體車道、推薦索引、中心線或控制指令。
- 保留 bounded key index、事件計數、接收時間、來源代次、路線撤銷、截斷標記；不保證完整原始報文，原 recorder 已脫敏/限長。
- 資料僅本機處理，無 C4、Navi v2、車輛控制或外部網路輸出。

## 驗證與未完成
本次核心合成測試 23 項已執行通過；未在 Android、實車、真實高德資料或 Node HTTP 服務執行驗收。主分支、正式 APK 不變。仍缺使用者版本高德原始 APK、內部 L2/L4 真實介面與授權、可安裝探針、即時採集接入與台灣路測；不得把候選欄位當作已取得的車道級數據。

### APK 靜態檢查
- wide.85 SHA-256 `344ae6f633a70e92923b627e664e927fda714dca37e8e098e21004ec94a33483` 與正式版相符；classes.dex 命中 `amap_link_packet`、`WideAmapLinkTrace`、`WideAmapLinkRoute`、`AmapLinkService`；未含內嵌高德 APK。
- 騰訊探針 SHA-256 `16fb5edba33d601aed33f04d35c0d8aa2b2f3bc8d6ed27d2d64b540ede3`；classes25.dex 命中 `getHDLaneMatchResult`、`getLaneInfoInRange`、`getLaneMatchedIndex`、`registerAdditionalJsonEventObserver`。字串檢查並非實機驗證。
