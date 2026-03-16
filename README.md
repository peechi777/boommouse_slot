Python 開發的老虎機模擬。本專案模擬了現代電子遊戲中常見的「多線消除 (Ways to Win)」、「滾輪掉落 (Cascading Reels)」以及「黃金符號轉換 (Symbol Transformation)」等核心機制，並透過百萬次等級的蒙地卡羅模擬 (Monte Carlo Simulation) 來驗證遊戲的 RTP (Return to Player) 與機率分佈。

1. 消除與掉落演算法 (Cascading Mechanics)
動態計算： 實作 calc_base 函式，支援 243 Ways 以上的連線計算邏輯，並能精確處理 Wild 符號替代規則。

遞迴消除： 透過 del_combos 與 fill_score_combo 實現掉落補牌機制，模擬盤面消除後的連續中獎過程。

2. 多層級機率控制 (Dynamic Weight Tables)
狀態感應掉落： 系統會根據當前的 Combo 次數 自動切換掉落表 (combo1 ~ combo11)。這種設計能精確控制連擊後的爆發力，展現了對遊戲平衡性 (Volatility) 的細膩控制。

符號升級邏輯： 實作了「黃金老鼠」機制，當連擊達到門檻（如 2、5、10 Combo）時，特定符號（M1-M3）會自動轉化為 Wild，增加大獎機率。

3. 高性能模擬測試
蒙地卡羅方法： 支援百萬次 (N=1,000,000) 局數模擬，確保統計數據（RTP、觸發率、中獎率）符合大數法則。

詳細統計指標：

Base Game 與 Free Game 分別的 RTP 貢獻。

不同數量 Scatter (C1) 觸發的期望值 (Payback)。

Re-trigger (再次觸發) 的機率統計。

Hit Rate (中獎率) 與平均得分分析。
