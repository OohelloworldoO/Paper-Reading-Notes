# 從這裡開始

## 你現在只要開一個檔案

先用 VS Code 開啟 `開始學RAG.code-workspace`，再點 `從零理解RAG.ipynb`。

**不要執行 README，也不用找其他舊版 Notebook。**

1. Notebook 右上角選取 Python 核心：下方的 `python.exe`。
2. 如果先前的 Notebook 核心還在執行，先按「重新啟動核心」。
3. 用 **Shift+Enter** 從第一格往下執行，先不要 Run All。

```text
D:\Project\Codex\2026-09-19\new-chat\work\jupyter-env\Scripts\python.exe
```

## VS Code 主要畫面只有三份檔案

| 檔案 | 用途 |
|---|---|
| README.md | 這份開始說明 |
| 從零理解RAG.ipynb | **實際執行、逐步學習的入口** |
| documents.json | 可修改的四條虛構規定 |

第一輪只做：「投影機可以借幾天？」
觀察 **關鍵字 → 文件分數 → 選中文件 → 完整提示 → 模型回答**。

## 其他檔案在哪裡？

- `mini_rag.py`、`local_model.py`、`logs` 仍保留，工作區暫時隱藏，減少干擾。完整檢索與組提示程式已直接寫在 Notebook。
- 想看模型連線程式，可在 Notebook 的 `generate` 函式按 Ctrl+點擊；或在檔案總管開啟 `local_model.py`。
- 舊 IDEAL-RAG 實驗與簡報已封存在 `../封存/`，目前不需使用。
- 大型模型移到 `../../work/rag-runtime`；Python環境在 `../../work/jupyter-env`。這兩個資料夾是執行所需，請勿刪除。

修改問題後，向下重新執行檢索、組提示與生成；只執行最後一格會沿用舊提示。這裡沒有訓練模型，也沒有把答案寫死。
