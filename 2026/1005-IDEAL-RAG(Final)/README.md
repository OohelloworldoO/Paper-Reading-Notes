# RAG

```mermaid
flowchart TD
    DB["外部文件庫"] --> R
    Q["使用者問題 query"] --> R["檢索相關文件"]
    R --> D["取得參考文件"]
    Q --> P["組合問題、參考文件與回答規則"]
    D --> P
    P --> M["LLM 讀取提示並生成回答"]
    M --> A["最終答案"]
```

# InstructRAG

```mermaid
flowchart TD
    subgraph SEEN["製作示範：answer-seen"]
        S["示範問題、檢索文件、已知答案"] --> G["LLM 生成辨別雜訊與說明答案依據的 rationale"]
        G --> B["保存示範問題與 rationale"]
    end

    subgraph UNSEEN["回答新問題：answer-unseen"]
        Q["新問題"] --> R["檢索文件"]
        Q --> P["組合示範、新問題與檢索文件"]
        R --> P
        P --> M["LLM 生成新題的 rationale 與答案"]
    end

    B --> P
```

# IDEAL-RAG

```mermaid
flowchart TB
    subgraph SEEN["① Answer-seen：建立示範"]
        direction TB
        SQ["示範問題"] --> SK["獨立回想內部知識"]
        SK --> SG["分別生成內部觀點與外部觀點"]
        SD["檢索文件＋已知答案"] --> SG
        SG --> SL["生成 linked rationale"]
        SL --> B["保存三類示範"]
    end

    subgraph UNSEEN["② Answer-unseen：回答新問題"]
        direction TB
        Q["新問題"] --> K["獨立回想內部知識"]
        K --> SI["生成內部觀點"]

        Q --> D["檢索外部文件"]
        D --> SE["生成外部觀點"]

        SI --> L["比較與整合"]
        SE --> L
        L --> A["Linked rationale 與答案"]
    end

    B -.-> UNSEEN
```

## conclusion

三者都能使用模型原有知識與外部文件。基本 RAG 將檢索文件提供給模型回答；InstructRAG 透過生成的 rationale 示範或微調，引導模型辨別雜訊；IDEAL-RAG 進一步明確拆開內部知識回想、內外觀點生成，以及最後的連結整合。差異在於如何組織與引導知識使用，不是有沒有參數知識。
