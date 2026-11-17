## 三導航共用轉彎預調（測試版，請小心使用）

高德車機版、高德一般版、Google NOO 都已接入共用轉彎預調；使用有效的左右轉／急轉及距離，由 comma 既有轉彎速度與減速度設定計算。保留高德車機版原生匝道預調，以及 wide.77 的日夜切換、分區與測速紅光修正。

**必須同時更新 comma 並重新啟動：**
- `test/carrot-wip-upstream-20261104`
- 或 `test/tony-carrot-wip-integrated-20261117`

App 開啟「智慧／預調速」；Carrot Web 的 `AutoNaviSpeedCtrlMode` 大於 0。共用預調使用 `AutoTurnControlSpeedTurn`（10–80 km/h）、`AutoTurnControlTurnEnd` 與 `AutoNaviSpeedDecelRate`。這是獨立減速候選，**即使 AutoTurnControl 關閉，App 預調仍可減速**；不會因此啟用轉向或方向燈。要停用本項請關閉 App 預調或導航減速主開關。

不改道路速限，不強制提高巡航設定，較低測速／彎道限制優先。停止、偏離、切換、過期撤銷。僅出口提示不猜測目標速度；高德一般版／Google 缺少主線限速時，沒有高德車機版等效的匯入恢復功能。

原簽章可覆蓋 wide.77。App 19 項原生預調＋25 項三來源檢查通過，車端 106 項離線協議與服務測試通過，APK 組裝及重建校驗通過。尚未實車驗收，正式 Latest 仍是 wide.77。

[完整說明](https://github.com/FANHAOHSIANG/Carrot-Bridge/blob/main/variants/wide79/README.md)
