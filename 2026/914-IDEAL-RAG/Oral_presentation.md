## 此論文想解決的問題

想解決 LLM 過度依賴檢索上下文，忽略自身已有的知識，而信心十足地給出錯誤答案
實務上很難決定何時該相信記憶、何時相信檢索資訊。  
有些方法抑制參數知識，幾乎完全依賴外部證據，但實際檢索情況不一定正確。

## Introduction

分兩步驟進行:

1. Dual-Standpoint Generation 分別對內部(模型已知的內容)與外部資訊(檢索上下文)產生各別獨立觀點
2. 用連結步驟協調，讓最終答案更透明且穩健

## Methodology

![](./images/Parametric%20Knowledge.png)

Parametric knowledge Extraction就是儲存在模型參數中的知識，可以理解成模型訓練時能夠回想起的內容。  
而萃取(Extraction)的實際做法就是先讓模型以每一步來回問答生的一段背景文字，還不讓它根據檢所文件立論，避免錯誤文件先影響它。

_模型記得，不代表「事實正確」_

並建立範例引導分析，在不知道新問題答案的情況下可以參考示範分析。  
取得新問題後，針對新問題回想初內部知識，以及檢索文件，再參考範例，減少跟著檢索文件回答錯誤情況。

1. 各自立論:「依我原本知道的內容，答案是甚麼?」、「依文件內容，答案是甚麼?」
2. 比較整合: 「兩邊是否一致?哪些理由支持?」

<<<<<<< HEAD:2026/01-IDEAL-RAG/images/Oral_presentation.md
##
=======
### Dual-Source Standpoint Generation

### Linked Rationale Generation

## Algorithm

## Experiments

## Analysis

## Conclusion
>>>>>>> 38622dae10c953170e0047f1d9db3249c42431cf:2026/914-IDEAL-RAG/Oral_presentation.md
