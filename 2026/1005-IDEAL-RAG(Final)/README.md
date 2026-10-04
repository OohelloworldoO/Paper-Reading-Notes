![](./Images/Keywords.png)

normal RAG

```mermaid
flowchart TD
    A[user query] --> B[keywords search in documents]
    B --> C[選出命中最多 keywords 的參考文件用於外部檢索]
    C --> D[將 query + 參考文件 + 規則]
    D --> E[LLM 運用已知資訊讀取文件，此時內部知識也會參與]
    E --> F[產生答案]
```
