# comma four 個人測試分支安裝

[回 Carrot Bridge](../README.md) · [官方／測試比較](C4_BRANCHES_zh-TW.md) · [Android 安裝](INSTALL_zh-TW.md)

> [!WARNING]
> **這是個人測試分支，請小心使用，不是穩定版或實車安全認證。** 可能發生非預期減速、路線偏差、功能失效或退出控制。請先確認車型、線束及回復方式，停車安裝與設定；駕駛全程注意道路並準備立即接管。
>
> 本安裝入口已做離線檔案與下載驗證，**尚未在 comma four 實機完成安裝、首次開機及車輛驗收**。若目前需要已驗證的日常使用環境，請保留你已知可用的版本。

## 安裝目標

| 項目 | 值 |
| --- | --- |
| 裝置 | **限 comma four（MICI）** |
| 儲存庫 | [FANHAOHSIANG/openpilot-carrot](https://github.com/FANHAOHSIANG/openpilot-carrot) |
| 分支 | `test/carrot-wip-upstream-20261104` |
| 核對時提交 | `796633626c61ef0fa9486ba0898a970b99f2d31a`（2026-11-15） |
| 更新方式 | 安裝時取上述分支當時最新內容；不是固定在核對提交 |
| 顯示提醒 | 安裝進度畫面顯示 `TEST BRANCH` |

**C3、C3X 和 comma four 均可搭配相容的 Carrot 使用 App。** C3／C3X 請使用符合硬體的 Carrot 安裝方式。下方短網址是 comma four 的測試分支入口。Android 手機或車機請下載 [Carrot Bridge APK](https://github.com/FANHAOHSIANG/Carrot-Bridge/releases/download/wide.70/Carrot-Bridge-wide.70.apk)。

## comma 安裝網址

在 comma four 的 **Custom software／自訂軟體 URL** 畫面輸入下列網址。

```text
https://da.gd/cb-test
```

短網址只轉向本儲存庫的安裝檔。已使用與 comma 設定程式相同的請求標頭核對最終檔案與 SHA-256，確認直接下載正確安裝檔；這項下載驗證不代表實機安裝通過。第三方短網址服務若不可用，改輸入備用長網址：

```text
https://raw.githubusercontent.com/FANHAOHSIANG/Carrot-Bridge/main/install/c4-test
```

[直接安裝檔](https://raw.githubusercontent.com/FANHAOHSIANG/Carrot-Bridge/main/install/c4-test) · [SHA-256](../install/c4-test.sha256) · [安裝檔來源](../install/c4-test.json) · [短網址下載核對紀錄](../install/download-check.json)

用一般電腦瀏覽器打開會下載 ELF 安裝檔，不是說明網頁，不要在電腦執行。comma 的設定程式會下載它再啟動安裝。

**不要改用 `installer.comma.ai/FANHAOHSIANG/...` 猜安裝網址。** 一般入口預設找 `FANHAOHSIANG/openpilot`，你的 `openpilot` 與 `openpilot-carrot` 是不同儲存庫；本入口已明確指定後者及完整分支名。

## 全新安裝／重新安裝

1. 停妥車輛，保持穩定供電及可用 Wi-Fi。先保存重要紀錄、目前分支／提交與設定，準備原本版本的回復方法。解除安裝／重置可能移除資料。
2. 在 comma 的初始設定選 **Custom software／自訂軟體**，閱讀裝置顯示的警告後輸入上方網址。已安裝其他版本者，依裝置既有解除安裝／重新設定流程進入；不在行駛中操作。
3. 等候下載、複製及首次建置。此分支是原始碼分支，初次處理可能比預建置版久；系統更新以裝置實際提示為準。
4. 開機後核對儲存庫是 `FANHAOHSIANG/openpilot-carrot`、分支是 `test/carrot-wip-upstream-20261104`，並記錄實際提交。若目標不符或啟動有錯誤，先停止後續測試。
5. 確認 comma 原有車型／線束及必要設定，再依 [分支操作表](C4_BRANCHES_zh-TW.md#comma-設定與操作) 逐項確認功能。
6. Android 安裝 Carrot Bridge；先在停車狀態確認導航接收、來源切換、停止撤銷，再另行安排車輛驗收。

## 已在同一儲存庫上的使用者

已使用 `FANHAOHSIANG/openpilot-carrot` 時，可在現有 Carrot Web／軟體管理頁，使用該版本提供的分支選擇及更新功能，選完整的 `test/carrot-wip-upstream-20261104`。已在此分支者按原有更新流程即可，不必重裝。

若頁面不能切換儲存庫，不能只填同名分支就假設換成功。以更新後顯示的儲存庫、分支及提交為準。此文件不提供覆蓋現有工作目錄的破壞性終端指令。

## 回復與問題回報

- 僅想停止 OSM 彎速預覽，可先關 `OsmCurveSpeedEnabled`；它不等於停用全部導航功能。
- 需要完整回復時，停車回到原本已知可用的分支／版本；如果無法開機，依 comma 官方 [復原工具](https://flash.comma.ai/) 與裝置說明處理。重新安裝前保存能保存的資料。
- 不要假設「官方 carrot-wip」等於固定穩定版，它也持續更新。
- 回報時附 App 版本、地圖版本、comma 實際提交、錯誤畫面與發生時間；分享紀錄前檢查位置與路線資訊。

## 本次驗證到哪裡？

已核對 comma 設定程式接受 ELF、安裝檔為 AArch64、內含正確 Git URL／完整分支、既有錯誤來源快取不會按原 marker 被使用，以及下載檔案雜湊。僅改動四個常數字串，機器指令區段保持原樣。實機安裝、AGNOS 相容性、首次開機、車輛控制及短網址服務長期可用性仍需實際確認。
