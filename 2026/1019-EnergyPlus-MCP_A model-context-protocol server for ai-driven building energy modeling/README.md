# EnergyPlus-MCP

# Implementation of EnergyPlus-MCP in Author's Github

https://github.com/LBNL-ETA/EnergyPlus-MCP

## 工具架構圖:

| 原圖區塊                             | 區塊內部元件                                                                                                 |
| :----------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| MCP Client                           | IDEs(開發環境)、AI 助手、新的 BEM 應用程式                                                                   |
| MCP Protocol layer(協定層)           | FastMCP 伺服器、MCP 工具                                                                                     |
| Orchestration Layer(協調層)          | EnergyPlus Manager、核心設定模組                                                                             |
| Tools Layer (工具層)                 | 模型設定與載入（9 個工具）；模型檢查（9 個）；模型修改（8 個）；模擬與結果（4 個）；伺服器管理與日誌（5 個） |
| EnergyPlus Integration Layer(整合層) | 模擬引擎：EnergyPlus；檔案系統：IDF 檔、氣象檔                                                               |
