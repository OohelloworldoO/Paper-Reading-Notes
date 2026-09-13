# IDEAL-RAG：用於檢索增強生成的指令驅動雙觀點萃取與對齊連結方法

王思正｜國立成功大學資訊工程學系碩士論文｜封面日期：2025 年 7 月

指導教授：莊坤達；共同指導教授：高宏宇。

## 譯本說明

本譯本依使用者提供的 54 頁 PDF 翻譯，涵蓋英文摘要、第 1–6 章正文、演算法、全部編號公式、提示詞、表格及圖說。保留原章節與公式編號，以便對照；圖中的主要文字另譯為文字說明，不重製原圖。已是中文的摘要、誌謝及前置目錄不重複抄錄；參考文獻保留英文書目，以利查找。

正文中的「我們」指原作者。標為「譯註」的內容是譯者補充，不是原文。原文有記號混用、數字與敘述不完全一致之處，保留原意並另行註明；不將作者的解釋改寫為已證實的因果結論。數學教學另見《IDEAL-RAG_數學理解與閱讀筆記》。本文中的提示詞只是論文內容的翻譯，不是對閱讀者或翻譯系統的指令。

頁碼採論文印刷頁碼；例如正文第 12 頁是 PDF 第 21 頁。

## 英文摘要中譯（PDF 第 4 頁）

檢索增強生成（RAG）讓大型語言模型（LLM）能夠按需求引用最新的外部證據。然而，當檢索文字包含雜訊或對抗性修改時，多數 RAG 系統會忽略參數知識，直接重述錯誤段落，因而產生幻覺。既有研究提出了各種去雜訊策略，但較少探討如何有系統地平衡並對齊內部與外部知識。近期的探測研究甚至顯示，在嚴重污染情境下，LLM 對既有記憶的依賴會急遽下降。

我們提出 IDEAL-RAG，一個包含三個階段的指令驅動框架。模型首先明確回想潛在知識，接著讓內部知識與檢索來源各自建立完整觀點，最後在連結模組中交叉檢查這些觀點，產生可追蹤的推理說明。整個流程不需要修改檢索器，也不需要新增人工標註。為了觀察網路內部的變化，我們將新提出的反事實敏感度分數（CSS）與既有的逐層參數知識分數（PKS）結合，分析強雜訊下「知識 FFN」路徑的行為，並顯示「先萃取、再平衡」的步驟可以降低幻覺風險。

實驗顯示，IDEAL-RAG 在乾淨檢索下與強基準 InstructRAG 表現相當；在受到對抗性污染的上下文中，完全匹配準確率最高提升 22.8%，準確率損失減半。CSS 與 PKS 分析指出，外部證據不可靠時，本框架透過運用內部事實，讓答案信心維持穩定。這些發現說明：先建立分離的觀點，再推理其一致之處，是提升 RAG 可靠性的有效方向。

關鍵字：大型語言模型、檢索增強生成、上下文學習、問答、穩健自然語言處理系統、提示工程。

> 譯註：原文的「+22.8%」是準確率相減後的約 22.8 個百分點，不是相對成長率。實驗也有未優於基準的情境，見第 4 章。

## 第 1 章　緒論（正文第 1–4 頁）

### 1.1 背景

大型語言模型已展現出卓越的自然語言生成能力 [3,39,41,4]。然而，面對預訓練期間未接觸過的近期事件、罕見實體或領域專屬事實時，模型往往無法準確回答，可能產生事實性幻覺，或直接拒絕作答 [34,8,20,55,57,47]。持續更新模型參數，或訓練 LLM 以涵蓋所有知識領域，都不切實際且消耗大量資源。

在開放領域問答（ODQA）[5] 中，檢索增強生成已成為主流解法 [10,11,18,23,26]，其流程如圖 1.1。系統先從大型語料庫檢索段落，再將段落放在輸入問題前方，希望語言模型以可驗證且最新的證據為回答基礎，同時運用其豐富的參數知識。

這個理想化設定建立在兩個重要假設上：第一，檢索文件準確、相關，而且彼此一致；第二，模型能理性地權衡外部資訊與內部知識。近期研究顯示，這兩個假設在真實環境中經常不成立。

### 1.2 研究動機

檢索流程經常傳回含有雜訊的內容，包括不相關片段、只符合部分條件的資料，甚至是對抗性植入的錯誤資訊。這些情況統稱為 RAG 雜訊 [9,52,54,27,7,46]。在此情境中，先進 RAG 系統呈現令人擔憂的失敗模式：LLM 過度依賴檢索上下文，卻忽略自身的參數知識 [42,38]。只要有一句話遭到竄改，模型就可能信心十足地給出錯誤答案。

圖 1.1：問答情境中典型的 RAG 流程，轉載自 [10]。圖中依序呈現文件建立索引、資料庫、使用者查詢、檢索相關文件、結合上下文與提示詞、LLM 生成回應。

為了處理上述問題，近期工作提出提升 RAG 抗雜訊能力的策略，協助模型抵抗誤導 [9,56]。但這些方法往往缺乏透明度或可解釋性，讓模型的決策過程難以追蹤。

另一條互補的研究路線探討何時應該使用檢索，以及是否需要使用檢索。當外部證據不可靠時，模型可以退回使用參數記憶，以提升抗雜訊能力。相關作法包括以觸發條件或信心為依據的控制器，在低可信情境中停用檢索 [52,45]；也包括混合策略，動態降低與高信心內部知識衝突之段落的權重，或直接拒絕使用這些段落 [54,48,1]。

平行研究也開始探討 RAG 流程中的內外知識衝突 [50,43]。研究發現，即使檢索內容與模型已記住的事實衝突，模型仍過度優先採用檢索內容。雖然一些方法試圖加強參數知識的影響力，但往往只使用淺層提示，例如：「如果文件資訊不足，就使用你自己的知識回答。」

這類提示沒有提供具體機制來偵測資訊不足、解決矛盾訊號，或建立對內部記憶的信任。實證結果持續顯示，LLM 仍會天真地重述表面合理卻不正確的證據。

### 1.3 本研究的工作

本領域仍缺少對核心問題的回答：當檢索內容不完整或具有誤導性時，如何利用模型已經「知道」的資訊來提升穩健性？

為填補此缺口，我們提出 IDEAL-RAG（指令驅動的雙觀點萃取與對齊連結）。此結構化框架系統性地處理三個核心部分：明確喚起參數知識；透過內部與外部觀點進行雙來源推理；將兩者穩定整合為最終統一的推理說明。

框架先指示模型生成自身的內部知識 [43,23]，再分別導出內部與外部觀點，最後執行審慎的整合。此流程鼓勵模型同時尊重檢索證據與自身記憶，見圖 1.2。

多個資料集的實驗顯示，IDEAL-RAG 在反事實或部分污染的檢索情境下更加穩健。當內外知識能互補時，本方法也更穩定，並在乾淨檢索下維持強勁表現。

本研究的結果與貢獻如下：

1. 提出指令引導框架，明確分離並協調參數證據與檢索證據，在無須訓練及微調設定下均可使用。
2. 在四個開放領域問答基準與兩種反事實雜訊情境中，相較標準 RAG，犧牲少量乾淨資料準確率，換取更強的穩健性。
3. 結果顯示，在 LLM 既有知識與新讀取資訊之間進行有理由的協調，是建立可靠 RAG 的合理方向。

圖 1.2：比較標準 RAG 與 IDEAL-RAG 在有雜訊檢索下的行為。基準模型受到誤導上下文影響，產生錯誤推理；IDEAL-RAG 運用內部知識，平衡衝突來源，得到穩定且正確的答案。

圖中案例中譯：問題為「誰贏得 2017 年 NCAA 女子籃球錦標賽？」正確檢索片段指出，2016–17 賽季最後由南卡羅來納大學奪冠；被竄改片段卻說聖母大學擊敗密西西比州立大學奪冠。基準回答選擇聖母大學；IDEAL-RAG 的說明則結合正確片段與內部知識，選擇南卡羅來納大學。圖中的文件 A／B 編號在不同說明區塊並不完全一致，此處保留其案例要旨。

## 第 2 章　相關研究（正文第 5–7 頁）

### 2.1 檢索增強生成對雜訊的敏感性

早期 RAG 系統隱含假設：檢索段落準確、互相一致，且充分支持目標答案。RAG 與 LLM 資訊檢索的綜述 [10,58] 很快推翻這項假設：即使極少量雜訊或對抗性修改，也能讓原本正確的答案變成信心十足的幻覺。此發現促成了抗雜訊 RAG 的研究方向。

多項研究分析不同雜訊類型如何破壞 LLM 行為 [9,56,6,54,7]。為減少這種退化，近期研究採取不同防禦策略：

- Yu 等人 [54] 要求模型在回答之前，先針對每個段落提出說明。
- Xiang 等人 [48] 聚合不同文件子集合產生的答案，以稀釋錯誤證據的影響。
- Asai 等人 [1] 將反思與 RLHF 評分 [36,31] 結合，生成多條推理鏈，再透過自我一致性投票排除矛盾路徑；其增益受推理鏈品質與投票門檻限制。
- 有關模型知識與 LLM 易受干擾性的研究 [40,37]，進一步凸顯此問題的嚴重性。
- Wei 等人 [45] 提出簡化的兩階段方法 InstructRAG。首先，在小規模的「答案可見」階段，透過少量人工設計的示例，教導凍結的 LLM 如何將檢索段落轉換成明確、逐步且能導向標準答案的推理說明；之後在「答案不可見」的測試階段使用相同提示模板。

InstructRAG 不需要額外監督訊號、重排序器或輔助模型，整個流程可以放進單一提示詞，並在資源相對有限的硬體上運行，因此被視為輕量方法。儘管設計簡單，它仍在多項問答基準取得接近最先進方法的完全匹配分數。

但後續分析揭露其弱點：即使只有一句檢索文字被對抗性修改，模型仍經常逐字重現污染內容，顯示僅靠指令，無法保證模型平衡運用檢索證據與參數記憶 [38]。

由於 InstructRAG 的基準準確率高、工程負擔小，且對雜訊檢索的脆弱性已有紀錄，我們將其作為主要比較對象。

### 2.2 對抗性與反事實基準

為了量化 RAG 的脆弱性，一系列受控基準會在人為設定下向檢索流程注入雜訊。

- Niu 等人 [47] 建立跨領域、用於 token 層級幻覺分析的語料庫。Yoran 等人 [52] 則將不相關或具誤導性的句子隨機插入 HotpotQA [51] 與 NQ [24]，並比較自然語言推論（NLI）過濾式防禦 [14,2]。
- Zhang 等人 [56] 提供段落替換、刪除與插入攻擊，甚至在檢索結果完全沒有標準證據時，仍要求模型回答。
- Fang 等人 [9] 定義三類雜訊：相關但不含答案的檢索雜訊、由隨機段落構成的不相關檢索雜訊，以及事實錯誤的反事實雜訊；並採用多個損失項進行自適應對抗訓練。

沿著此研究方向，我們建立反事實測試集，衡量模型對外部證據的依賴與抵抗污染上下文的能力。實驗顯示，整合內外知識後，模型在更複雜的檢索情境下仍能維持穩定。

### 2.3 RAG 中的參數知識

探討 LLM 參數記憶如何貢獻 RAG 的研究仍相對有限。條件式 RAG 工作 [49,30,19,1] 探討何時應啟用檢索，以免在模型記憶足夠時受到干擾，但沒有提供相互驗證的機制。

Wang 等人 [43] 先提示模型生成與問題有關的記憶，再將檢索證據與萃取知識分群，進行事後融合。但此方法仍是提示層級的啟發式策略，沒有可學習的衝突解決機制。

Sun 等人 [38] 提出參數知識分數（PKS）與外部上下文分數（ECS），探測內部機制，並發現主流 RAG 架構幾乎完全依賴檢索。

我們延伸 [38] 的分析：除了 PKS，也設計反事實敏感度分數（CSS），量化內部知識如何緩衝雜訊證據。結果指出，明確萃取參數知識，並透過雙來源審議加以整合，能顯著提升穩健性。

> 譯註：本章是原作者對文獻的描述，不表示譯者已逐篇確認每一項歸因。參考文獻 [38] 的 PKS 方法來源另於數學筆記提供原始論文連結。

## 第 3 章　研究方法（正文第 8–19 頁）

LLM 在少量監督下，已能遵循複雜指令、維持風格，並產生多步驟解釋。近期工作 [3,1,45] 顯示，只要仔細挑選示例，既有模型就能學會複雜行為，不必大量標註或設計專屬獎勵。基於這些發現，我們提出 IDEAL-RAG，一個以指令為核心的三階段流程：先顯露並對照模型的參數記憶與可能含有雜訊的檢索段落，再協調兩者。

為何需要三個階段？過去的 RAG 方法常把內部知識當成備援。然而，實務上很難決定何時該相信記憶、何時該相信檢索文字，現代 LLM 容易過度重視表面合理的段落，尤其在檢索不完整或受到攻擊時。有些方法抑制參數知識，幾乎完全依賴外部證據，但實際部署不能假設檢索完美。

我們採取相反觀點：主動呈現模型已知的內容，要求內部記憶與檢索上下文分別產生獨立觀點，再透過連結步驟明確協調。這種分離要求模型針對兩個來源進行推理，而非抓住最醒目的段落，讓最終答案的形成更透明、更穩健。

流程在兩種互相對應的情境中執行（圖 3.1）。在小型「答案可見」資料子集中，我們產生由標準答案引導的觀點與連結推理，形成精簡的示例庫，呈現理想推理軌跡。對於「答案不可見」的問題，模型取得問題、檢索段落及萃取的內部知識，僅以示例為引導，生成觀點與最終連結推理。連結步驟要求模型明確比較並協調觀點。

圖 3.1：IDEAL-RAG 的高層次概覽。先萃取參數知識，再在答案可見資料中生成雙觀點及連結推理，以建立示例庫；答案不可見資料則以這些示例為條件，執行相同階段，產生最終說明與答案。圖中 Demo 指示例，Answer-seen／Answer-unseen 分別指答案可見／不可見。

以下詳述三個模組：參數知識萃取 $E_{\mathrm{int}}$、雙來源觀點生成 $G$、連結推理生成 $L$。

上述三階段的生成都使用凍結骨幹 $\Theta_0$，不需要教師模型或外部驗證器。標準答案在建立示例庫 $B$ 時揭露，讓模型先觀察理想推理軌跡，再透過少樣本上下文學習（ICL）或輕量監督式微調（SFT）處理未見問題。

> 譯註：此處「凍結」適用於生成示例及 ICL 路徑。第 3.3.3 節的 SFT 路徑會更新模型的可訓練參數；不能將整篇理解為完全不訓練。原文在本章將 IDEAL-RAG 的英文展開寫作 Instruction-Driven Evidence Alignment and Linking，與封面不同；本譯本名稱統一依封面。

圖 3.2：IDEAL-RAG 詳細架構。內部記憶與檢索段落先各自形成觀點，作為參數知識與非參數知識之間的介面。模型審議兩個觀點，形成統一推理與最終答案；可透過上下文提示或輕量微調的預測模組實作。圖中 ICE 指上下文示例；Internal／External Knowledge 指內部／外部知識；Standpoint 指觀點；Final Linked Rationale 指最終連結推理說明。

### 演算法 1　IDEAL-RAG

輸入：包含訓練與測試資料的問答語料 $C=\{(q_i,a_i,D_i)\}$，以及凍結骨幹 $\Theta_0$。輸出：融合權重與測試時的融合推理；原文輸出標頭寫作 $\Theta_{\mathrm{fuse}}$、$\hat R_{\mathrm{fuse}}$，流程中主要使用 link 下標。

**觀點生成：**從語料選取很小的種子集。對每個種子問題，先只依問題萃取內部知識，再分別以「問題、答案、內部知識」及「問題、答案、檢索文件」生成內部與外部觀點，加入對應示例庫。對其餘訓練與測試問題，先萃取內部知識，再以兩個示例庫為上下文示例，在不提供該題答案的條件下，生成內部與外部觀點。

**連結推理生成：**對每個種子問題，提供問題、答案、檢索文件、內部知識與雙觀點，生成連結推理並建立連結示例庫。

- ICL 模式：將測試問題、檢索文件、內部知識、雙觀點，以及連結示例交給凍結模型，產生最終推理。
- 微調模式：對訓練問題揭露答案，以凍結模型生成連結推理作為訓練目標；更新連結模型權重。測試時使用更新後模型，但不提供測試答案，生成最終推理。

回傳最終連結推理 $\hat R_{\mathrm{link}}$。原圖的 $k\ll |C|$ 表示種子示例數遠小於資料量；這裡的 $k$ 不宜與檢索 top-$k$ 混淆。

### 3.1 問題定義

考慮一個開放領域語料庫：

$$C=\{(q_i,a_i,D_i)\}_{i=1}^{N}. \tag{3.1}$$

$q_i$ 是自然語言問題，$a_i$ 是標準答案，$D_i=\mathcal R(q_i)\subset T$ 是固定檢索器 $\mathcal R$ 從大型文字集合 $T$ 取回的段落集合。典型 RAG 將 $[q_i;D_i]$ 串接後送入 LLM，希望模型以 $D_i$ 為依據，同時運用互補的參數知識。

我們刻意固定檢索器，以單獨觀察生成端的穩健性。目標是最大化原文所稱的完全匹配準確率：

$$\mathrm{Acc}=\frac{1}{|C_{\mathrm{test}}|}\sum_{(q,a)\in C_{\mathrm{test}}}\mathbf 1\!\left[a\subseteq R,\ R=\mathrm{IDEAL}(q,D)\right].\tag{3.2}$$

$\mathrm{IDEAL}(\cdot)$ 表示以下完整流程。

> 譯註：這裡的 $a\subseteq R$ 依第 4.1.3 節，意指答案字串出現在最終答案區段中，不是一般集合運算，也不要求預測整串文字與參考答案完全相同。

### 3.2 雙來源觀點生成

我們主張，要求模型對答案表達獨立觀點，一個以內部記憶為基礎，另一個以檢索文字為基礎，可建立供後續協調使用的明確框架。

#### 3.2.1 答案可見觀點：建立種子示例

抽取小型種子集 $C_{\mathrm{seed}}$，並揭露答案 $a$，讓模型觀察「理想」推理目標。

第一，喚起內部知識。依循 [53,43]，使用嚴謹的結構化提示模板 3.1，從凍結模型萃取內部知識：

$$K_{\mathrm{int}}^\star=E_{\mathrm{int}}(q;\Theta_0).\tag{3.3}$$

第二，獨立建構觀點。為避免過早融合導致任一來源丟棄有用資訊，在已知標準答案的條件下，使用不同提示詞（3.2、3.3）產生分離的推理鏈：

$$S_{\mathrm{int}}^\star=G(q,a,K_{\mathrm{int}}^\star;\Theta_0),\qquad S_{\mathrm{ext}}^\star=G(q,a,D;\Theta_0).\tag{3.4}$$

要求每個來源在答案可見時，依自己的證據立論，便能取得兩條充分發展、互不干擾的推理線，留待之後協調。

第三，填入示例庫：

$$B_{\mathrm{int}}\leftarrow S_{\mathrm{int}}^\star,\qquad B_{\mathrm{ext}}\leftarrow S_{\mathrm{ext}}^\star.\tag{3.5}$$

這些高品質案例作為答案不可見階段的少樣本示範。箭頭在此表示將案例加入示例庫。

**提示詞 3.1：從凍結模型萃取內部知識**

> 生成一份文件，提供與給定問題相關且準確的背景知識。文件應資訊充實、結構清楚，如同知識來源中的節錄，但不要直接回答問題。避免不必要的評論、解釋或直接回應。如果沒有相關資訊，請回答「我不知道」，不要增加推測或背景內容。問題：{question}。文件：{K_int}。

**提示詞 3.2：答案可見時生成外部觀點**

> 閱讀以下與問題 {question} 有關的文件：{retrieved documents}。
>
> 請僅使用外部文件回答問題，不依賴內部或先前知識，並說明提出的答案 {answers} 如何獲得支持。
>
> 你的解釋應以提供的外部文件為基礎。若文件無法合理支持提出的答案，可改提出文件支持的更合理答案，並解釋原因。不要引用超出文件陳述或暗示範圍的內部知識或既有事實。
>
> 輸出應指出文件中的相關事實主張，並以符合邏輯且根據文件的方式，說明這些主張如何導向提出的答案，或支持更好的答案。問題可能包含多個組合條件，需要中間分析才能推導答案。請提供有依據且清楚的推理細節，最後給出簡潔結論。輸出：{S_ext*}。

**提示詞 3.3：答案可見時生成內部觀點**

> 閱讀以下與問題 {question} 有關的內部知識：{extracted internal knowledge}。
>
> 請僅使用內部知識回答問題，不參考任何外部文件，並說明提出的答案 {answers} 如何獲得支持。
>
> 主要根據提供的內部知識陳述解釋。若內部知識無法合理支持提出的答案，可改提出內部知識支持的更合理答案，並說明原因。
>
> 輸出應指出內部知識中已提供或已知的事實主張，並以邏輯健全且可驗證的方式，說明這些主張如何導向提出的答案，或支持更好的答案。問題可能具有組合性，需要中間分析。請提供有依據且清楚的推理細節，最後給出簡潔結論。輸出：{S_int*}。

#### 3.2.2 答案不可見觀點：少樣本推論

對其餘資料隱藏答案。如第 3.2.1 節，模型先萃取新的參數知識：

$$K_{\mathrm{int}}=E_{\mathrm{int}}(q;\Theta_0).\tag{3.6}$$

接著以示例庫為條件，使用提示詞 3.4 與 3.5，分別生成外部與內部觀點：

$$\hat S_{\mathrm{int}}=G(q,K_{\mathrm{int}};\Theta_0,\mathrm{ICE}=B_{\mathrm{int}}),\qquad \hat S_{\mathrm{ext}}=G(q,D;\Theta_0,\mathrm{ICE}=B_{\mathrm{ext}}).\tag{3.7}$$

每個觀點包含核心證據、簡潔推理鏈及不確定性說明，為後續融合奠定基礎。

**提示詞 3.4：答案不可見 ICL 任務的外部觀點**

> 主要任務是分析提供的外部文件，以回答問題。請評估文件相對於問題的相關性、準確性與完整性。若文件明確支持某個答案，說明其如何導向該答案。若文件不完整、模糊或互相衝突，請只依文件內容做出最佳判斷，不使用內部或既有知識。
>
> 以下是推理說明示例：{B_ext}。現在請分析以下文件並回答問題：{retrieved documents}。依據提供的資訊，回答 {question}。輸出：{S_ext_hat}。

**提示詞 3.5：答案不可見 ICL 任務的內部觀點**

> 主要任務是分析提供的內部知識，以回答問題。請檢查資訊是否足以支持明確答案。若足夠，解釋內部知識如何導向答案；若不足，請使用更廣泛的內部知識，提出你能提供的最合理答案，但不要使用外部來源或文件。
>
> 以下是推理說明示例：{B_int}。現在請分析以下內部知識並回答問題：{extracted internal knowledge}。依據內部知識與提供資訊，回答 {question}。輸出：{S_int_hat}。

### 3.3 連結推理生成

給定兩個觀點 $(\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}})$，任務變成產生一段連貫、能辨識衝突且支持答案的推理說明。我們以連結推理生成器 $L$ 完成，仍採「答案可見 → 答案不可見」模式，並提供可選的微調階段。

#### 3.3.1 答案可見的連結示例

對每個種子案例，指示模型交叉檢視內外觀點、指出一致或衝突之處、補足缺漏事實，並提出最終結論，詳見提示詞 3.6。模型輸出：

$$R_{\mathrm{link}}^\star=L(q,a,D,K_{\mathrm{int}}^\star,B_{\mathrm{int}},B_{\mathrm{ext}};\Theta_0).\tag{3.8}$$

結果存入第三個示例庫 $B_{\mathrm{link}}$。

> 譯註：式 3.8 使用 $B_{\mathrm{int}},B_{\mathrm{ext}}$；演算法 1 對應位置使用該題的 $S_{\mathrm{int}}^\star,S_{\mathrm{ext}}^\star$。原文記號並不統一；依提示詞語意，核心是提供該題的內外觀點。

**提示詞 3.6：答案可見時生成連結推理**

> 閱讀與問題有關的檢索文件及萃取的內部知識。已知問題 {question} 與正確答案 {answers}。
>
> 兩個獨立論證各自試圖支持其認為正確的答案：外部觀點 {B_ext}；內部觀點 {B_int}。
>
> 分析兩個論證，判斷內外資訊如何幫助推導正確答案。目標是整理雙方相關推理，找出哪些部分與正確答案一致，並說明結論如何獲得支持，而非單純選邊。
>
> 請指出雙方主要主張，將其與正確答案比較，接受邏輯上支持正確答案的主張；拒絕不一致、缺乏支持或與正確答案矛盾的主張，並說明原因。整合雙方有用資訊，建構連貫且逐步導向正確答案的解釋。
>
> 解釋只根據論證與已知正確答案。問題可能具有組合性，需要中間分析。請提供有根據且清楚的推理細節，最後給出簡潔結論。輸出：{R_link*}。

#### 3.3.2 測試時的少樣本連結

即使沒有額外訓練，生成器 $L$ 也能運用連結示例庫 $B_{\mathrm{link}}$，在未見測試資料上執行連結推理：

$$\hat R_{\mathrm{link}}=L\big((q,D,\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}})\in C_{\mathrm{test}};\Theta_0,\mathrm{ICE}=B_{\mathrm{link}}\big).\tag{3.9}$$

**提示詞 3.7：答案不可見 ICL 任務的連結推理**

> 主要任務是分析兩個相互競爭的論證，以回答問題。一方由外部文件支持，另一方由內部知識支持；每個論證都包含推理及來源內容。
>
> 仔細評估各論證如何使用其來源來支持答案。若其中一方有明顯更強的證據及更有效的推理，請說明為何更具說服力。若雙方都不完整、模糊或同樣有力，請只依提供資訊做出最佳判斷，不依賴額外或先前知識。
>
> 以下是推理說明示例：{B_link*}。現在請分析檢索文件、萃取的內部知識，以及兩個獨立論證：外部觀點 {S_ext_hat}，內部觀點 {S_int_hat}。依據論證及支持資料，回答問題 {question}。輸出：{R_link_hat}。

#### 3.3.3 以連結推理進行指令微調

SFT 版本將流程用於訓練資料，依第 3.3.1 節產生 $R_{\mathrm{train-link}}^\star$，再以這些連結推理微調骨幹：

$$\Theta_{\mathrm{link}}=\arg\min_\Theta\sum_{R^\star\in B_{\mathrm{train-link}}^\star}-\log p_\Theta\big(R^\star\mid(q,D,\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}})\in C_{\mathrm{train}}\big).\tag{3.10}$$

依循 [45]，以 $\Theta_{\mathrm{link}}$ 取代原模型權重後，無須加入上下文示例即可生成：

$$\hat R_{\mathrm{link}}=L\big((q,D,\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}})\in C_{\mathrm{test}};\Theta_{\mathrm{link}}\big).\tag{3.11}$$

實驗上，SFT 在大型語料可帶來額外改善，而只使用 ICL 也已能取得強勁表現。

> 譯註：式 3.9–3.11 的括號內「屬於資料集」是原文不夠嚴格的簡寫，不應理解為模型輸入一個布林值。公式中也省略了提示模板與演算法列出的部分輸入，例如 $K_{\mathrm{int}}$；實作時應連同完整提示一起確認。

## 第 4 章　實驗（正文第 20–32 頁）

本章介紹評估 IDEAL-RAG 所使用的資料集、評分指標、基準方法、訓練流程及實作設定。第 4.2–4.4 節報告主要結果，第 5 章則深入分析錯誤模式與消融研究。

### 4.1 實驗設定

#### 4.1.1 開放領域問答基準

我們使用四種常見資料集，涵蓋不同問題風格與推理深度：PopQA [29] 著重單一事實與名稱回憶；Natural Questions（NQ）[24] 包含網路與維基百科問題；TriviaQA [21] 包含知識問答；2WikiMultiHopQA [13] 包含維基百科雙跳推理鏈。

對每個問題保留前 $k$ 個檢索段落。原文此處稱使用結合 BM25 [35]、DPR [22] 與 Contriever [17] 的混合檢索器，在 [22] 使用的維基百科快照上檢索。設定遵循近期研究 [1,44,45] 的評估協定，以利公平一致地比較。表 4.1 的 Recall@$k$ 顯示，仍有相當比例的標準證據未被檢索到，構成實際的不完美檢索情境。

> 譯註：表 4.1 是依資料集列出單一檢索器，並未列出三者融合方法；重現時不能只依前述「混合檢索」文字推定具體實作。

#### 4.1.2 Counter-All 與 Counter-Mix 測試集

實際檢索流程傳回的前 $k$ 個文件幾乎不會完全乾淨，而可視為潛在雜訊算子 $\mathcal N$ 作用的結果。污染包括：與問題無關的段落；只提到部分答案面向的段落；以及刻意或非刻意使用誤導措辭的段落。

形式上，對每組標準文件 $D_i$，觀察到的是受擾動的集合：

$$\widetilde D_i=\mathcal N(D_i)=\{\text{不相關結果}\}\cup\{\text{部分符合結果}\}\cup\{\text{對抗性修改}\}.\tag{4.1}$$

多數公開基準僅含少量真正的對抗性段落，但真實環境更常遇到雜訊或誤導內容。為反映這些挑戰，我們依 [9] 建立兩組反事實測試，對問答系統施加更強污染壓力。

只要檢索段落含有與標準答案 $a$ 完全一致的字串，就將該字串替換成語意相近、但錯誤的實體；標記處理由 GPT-4o [16] 完成。例如將 Barack Obama（巴拉克・歐巴馬）替換為 Michelle Obama（蜜雪兒・歐巴馬）。

- Counter-All，記為 $\widetilde D_{c_a}$：修改所有含答案的段落。
- Counter-Mix，記為 $\widetilde D_{c_m}$：針對檢索上下文至少有兩個標準答案出現的問題，修改其中 50% 的含答案段落，其餘保持不變。

> 譯註：此處「至少兩個標準答案」的原文措辭有歧義，結合後文應理解為有足夠的含答案段落可進行半數替換；若要重現，仍須確認到底以答案出現次數、段落數或別名數篩選，以及奇數段落如何取整。Counter-All 也不是把每個檢索文件全文換掉，而是修改所有含答案段落中的答案片段。

表 4.1 列出每個資料集符合替換條件而納入兩種測試的題數。為確保可比較性，後續污染分析限定在對應子集合。

**表 4.1　資料集統計及檢索設定**

| 資料集 | 訓練題數 | 測試題數 | 檢索器 | Top-K | R@K（%） | Counter-Mix 題數 | Counter-All 題數 |
|---|---:|---:|---|---:|---:|---:|---:|
| PopQA | 12,868 | 1,399 | Contriever | 5 | 68.7 | 578 | 961 |
| Natural Questions | 79,168 | 3,610 | DPR | 5 | 68.8 | 1,634 | 2,482 |
| TriviaQA | 78,785 | 11,313 | Contriever | 5 | 73.5 | 6,548 | 8,313 |
| 2WikiMultiHopQA | 167,454 | 12,576 | BM25 | 10 | 40.7 | 3,645 | 5,122 |

#### 4.1.3 評估指標

為與既有工作 [45,1] 直接比較，使用式 3.2 的完全匹配準確率（EM）。只要參考答案集合中任一字串出現在模型最終答案區段，就計為正確。

**準確率衰減比例（ADR）。** 單看 EM 無法反映強污染檢索下的穩健性，因此定義：

$$\mathrm{ADR}_x=\frac{\mathrm{EM}_{\mathrm{clean}}-\mathrm{EM}_{\mathrm{cf}}}{\mathrm{EM}_{\mathrm{clean}}}\times100\%\quad\downarrow.\tag{4.2}$$

此指標表示段落改為反事實版本後，準確率損失的百分比，其中 cf 為 Counter-All 或 Counter-Mix；越低越好。

**反事實敏感度分數（CSS）。** 除了表面準確率，也檢查對抗性證據是否破壞模型內部決策的穩定性。我們衡量答案 token 的對數機率對反事實修改的反應：

$$\Delta\mathrm{CSS}=\sum_{t\in\mathrm{Ans}}\left|\log p_{\mathrm{clean}}(t)-\log p_{\mathrm{cf}}(t)\right|\quad\downarrow.\tag{4.3}$$

此分數加總乾淨與修改後上下文之間，答案 token 對數機率的變化。值越大，表示段落一被修改，模型對答案的信念就劇烈變動。

**參數知識分數（PKS）。** 依 [38]，每個 Transformer 區塊結合兩種資訊流：殘差流包含從提示累積的上下文資訊，包括檢索段落；前饋網路（FFN）則引入儲存在模型參數中的新證據。PKS 衡量 FFN 對殘差流原有 token logit 分布的改變程度。對第 $\ell$ 層及答案 token $t$：

$$\mathrm{PKS}_{\ell,t}=\mathrm{JSD}\!\left(\mathrm{softmax}(W_U\mathrm{LN}(h_{\ell,t}^{\mathrm{mid}})),\ \mathrm{softmax}(W_U\mathrm{LN}(h_{\ell,t}^{\mathrm{out}}))\right).\tag{4.4}$$

$h^{\mathrm{mid}}$ 是 FFN 前的隱藏狀態；$h^{\mathrm{out}}$ 是 FFN 輸出加回殘差路徑之後的隱藏狀態。

- PKS 小：FFN 幾乎不改變 logits，該區塊主要傳遞已由提示累積的上下文。
- PKS 大：FFN 大幅改變 logits，原文將其解讀為模型較多運用權重中的參數記憶，而非檢索文字。

為分析穩健性，報告每層在乾淨與雜訊上下文間的變化：

$$\Delta\mathrm{PKS}_{\ell}=\frac{1}{|\mathrm{Ans}|}\sum_{t\in\mathrm{Ans}}\left(\mathrm{PKS}_{\ell,t}^{\mathrm{cf}}-\mathrm{PKS}_{\ell,t}^{\mathrm{clean}}\right).\tag{4.5}$$

正值表示該層在檢索污染後必須透過注入更多儲存知識來補償；接近零則表示依賴模式維持穩定。繪製所有層的曲線，可逐層觀察雜訊如何改變內部記憶與外部證據的平衡。

所有顯著性檢定採配對雙尾 t 檢定，顯著水準設為 $p<0.05$。

> 譯註：PKS 直接量到的是分布改變，而非正確知識的含量；上面的知識使用說法屬作者的機制解釋。第 4.4 節與數學筆記另說明其限制。

#### 4.1.4 基準方法

RAG 的最先進表現高度取決於領域、資料量與運算預算，難以指定單一無爭議的冠軍。因此我們選擇在相近實驗條件下具代表性、表現良好的方法，涵蓋無須訓練及可訓練模式。

- 上下文檢索增強語言模型（RALM）[33]：無須訓練，直接在提示詞中串接前 $k$ 個段落及問題，所有推理由凍結模型執行。
- 一般監督式微調（vanilla SFT）：以檢索段落為輸入，微調模型以最大化答案對數似然，不加入特別提示或輔助推理目標。
- InstructRAG [45]：使用少樣本示例，教導模型將檢索證據組成明確推理說明；在公開 RAG 方法中，於開放領域問答基準具強勁去雜訊表現。

標有星號的成績，採原作者釋出結果或本研究忠實重現結果中較高者。原始 InstructRAG 模型採全參數微調，而本研究自行執行的實驗包含 IDEAL-RAG，採參數高效微調（PEFT）[12]。

> 譯註：表 4.2 圖說另將 InstructRAG* 指為原作者公開檢查點。兩邊並非完全相同訓練條件，評估時應保留此差異。

#### 4.1.5 實作細節

所有模型以 Llama-3-8B-Instruct 為基礎。微調採 LoRA [15]，rank 為 8、$\alpha=16$、dropout 為 0.05；訓練兩個 epoch，使用 AdamW [28] 與餘弦學習率衰減，學習率 $2.5\times10^{-5}$，warm-up 比例 3%。透過梯度累積達到全域批次一百萬個 token，使用兩張 A100 80GB GPU、DeepSpeed ZeRO-2 [32] 及 bf16。

由於損失很快趨於平穩，每個資料集僅隨機選取一萬道訓練問題。推論使用 vLLM [25] 的貪婪解碼模式；依 InstructRAG 設定，需要 ICL 時每個提示加入兩個示例。

### 4.2 主要結果

表 4.2 報告四個問答基準，在原始乾淨檢索與兩種反事實測試中的 EM。為方便閱讀，以下將原來寬表依資料集拆開，數值保持不變。所有數值皆為百分比；「未訓練」指僅使用提示，「已訓練」指使用微調版本。星號沿用原文。

**表 4.2a　PopQA**

| 設定 | 方法 | 原始 | Counter-Mix | Counter-All |
|---|---|---:|---:|---:|
| 未訓練 | RALM | 61.97 | 72.66 | 32.36 |
| 未訓練 | InstructRAG | 63.97 | 78.55 | 40.69 |
| 未訓練 | IDEAL-RAG | 62.76 | 81.14 | 46.51 |
| 已訓練 | vanilla* | 61.00 | — | — |
| 已訓練 | InstructRAG* | 65.90 | 89.45 | 49.32 |
| 已訓練 | IDEAL-RAG | 64.05 | 84.08 | 47.76 |

**表 4.2b　Natural Questions**

| 設定 | 方法 | 原始 | Counter-Mix | Counter-All |
|---|---|---:|---:|---:|
| 未訓練 | RALM | 56.37 | 69.34 | 25.38 |
| 未訓練 | InstructRAG | 62.52 | 77.36 | 25.10 |
| 未訓練 | IDEAL-RAG | 60.83 | 77.97 | 51.97 |
| 已訓練 | vanilla* | 56.60 | — | — |
| 已訓練 | InstructRAG* | 65.68 | 80.29 | 32.67 |
| 已訓練 | IDEAL-RAG | 63.71 | 80.97 | 55.48 |

**表 4.2c　TriviaQA**

| 設定 | 方法 | 原始 | Counter-Mix | Counter-All |
|---|---|---:|---:|---:|
| 未訓練 | RALM | 71.47 | 82.48 | 42.80 |
| 未訓練 | InstructRAG | 76.95 | 89.80 | 53.69 |
| 未訓練 | IDEAL-RAG | 76.82 | 91.95 | 78.73 |
| 已訓練 | vanilla* | 73.90 | — | — |
| 已訓練 | InstructRAG* | 78.70 | 90.79 | 57.80 |
| 已訓練 | IDEAL-RAG | 77.19 | 92.21 | 78.58 |

**表 4.2d　2WikiMultiHopQA（原表簡稱 MultiHopQA）**

| 設定 | 方法 | 原始 | Counter-Mix | Counter-All |
|---|---|---:|---:|---:|
| 未訓練 | RALM | 43.37 | 60.81 | 54.98 |
| 未訓練 | InstructRAG | 49.27 | 79.75 | 59.59 |
| 未訓練 | IDEAL-RAG | 47.60 | 76.76 | 60.82 |
| 已訓練 | vanilla* | 43.8 | — | — |
| 已訓練 | InstructRAG* | 57.19 | 87.02 | 66.26 |
| 已訓練 | IDEAL-RAG | 50.01 | 80.85 | 64.31 |

表 4.2 圖說中譯：各欄報告乾淨檢索及半數／全部含答案段落遭修改後的準確率。上半部為純提示模型，下半部為進一步微調的模型。vanilla* 來自 [45]，InstructRAG* 為該研究釋出的較強模型；原表以粗體標出最佳值。

#### 4.2.1 乾淨資料上的表現

首先評估原始未擾動資料。無論是純提示或 PEFT 設定，IDEAL-RAG 都略低於 InstructRAG。已訓練設定的最大差距出現在 2WikiMultiHopQA，約為 −7.2%；未訓練設定最大差距則在 NQ，為 −1.69%。

如第 5.1.2 節所述，IDEAL-RAG 的乾淨資料表現與基礎模型內是否有相關參數知識有關。因此，答案較少存在模型記憶中的資料集，例如 PopQA 與 2WikiMultiHopQA，對比 InstructRAG 時會出現較大的落差。

儘管有差異，整體表現仍然強勁。作者將表 4.1 的含答案段落 R@$k$ 視為檢索所限制的經驗上限，指出 IDEAL-RAG 經常接近此上限。R@$k$ 高時，與 InstructRAG 的差距縮小；R@$k$ 較低時，兩者都受缺漏證據限制。因 IDEAL-RAG 可退回參數記憶，EM 有時能達到或超過 R@$k$；作者認為純依賴檢索段落的方法無法達到此情境。這顯示本方法即使在乾淨資料下，仍有競爭力且符合實際檢索限制。

> 譯註：準確率差應稱「百分點」。另，字串式 R@$k$ 對能推理或使用參數知識的系統，不是嚴格的數學上界；即使答案字串未直接出現，也可能由證據推導答案。

#### 4.2.2 反事實雜訊下的穩健性

在 Counter-Mix 中，作者概括描述 IDEAL-RAG 與強基準相當或略勝，認為部分對抗性內容已足以暴露基準對檢索段落的過度依賴。所有含答案段落遭污染的 Counter-All 下，IDEAL-RAG 展現最大的穩健性：在 NQ 的已訓練設定最高改善約 22.8%，未訓練設定改善擴大至約 26.9%。PopQA、TriviaQA 及 2WikiMultiHopQA 也觀察到類似增益，但幅度不同。

一項重要限制出現在標準答案較少存在參數記憶的資料集，尤其是 PopQA 與 2WikiMultiHopQA。這些情境中，已訓練的 InstructRAG 在完全污染下有時優於 IDEAL-RAG。我們將此歸因於 IDEAL-RAG 刻意重視內部萃取證據：當參數記憶缺少相關資訊時，這種偏好反而可能成為負擔。第 5.1.2 節的答案包含分析支持此模式：答案存在內部或兩邊皆有時，本方法占優勢；答案僅在檢索文件時，則落後強基準。

綜合而言，結果支持主要主張：明確呈現並對齊內部知識，可增強對檢索雜訊的韌性；也說明在外部證據是唯一可靠來源的領域，參數知識覆蓋率具有實務重要性。

> 譯註：表 4.2 的 Counter-Mix 並非每項都持平或更好，例如已訓練 PopQA 為 84.08 對 89.45，MultiHopQA 為 80.85 對 87.02。NQ 的已訓練 Counter-All 增益為 $55.48-32.67=22.81$ 個百分點；未訓練為 $51.97-25.10=26.87$ 個百分點。

### 4.3 準確率衰減比例（ADR）

表 4.3 報告 ADR。原文此節又稱其為 Answer Degradation Rate，並文字描述為原本答對、但在檢索污染後無法維持正確的答案比例；越低表示越穩健。

原作者概括指出，四個基準中，IDEAL-RAG 在兩種污染下皆有最低 ADR，多數情境差距明顯。NQ 最突出：在未訓練的 Counter-All 中，InstructRAG 衰減 70.61%，IDEAL-RAG 為 35.22%，約減少一半。PopQA、TriviaQA 與 2WikiMultiHopQA 也有較小幅度改善，支持內外知識對齊能提升模型抗污染能力。

**表 4.3　ADR（%，越低越好）；每格依序為 Counter-Mix／Counter-All**

| 設定 | 方法 | PopQA | NQ | TriviaQA | MultiHopQA |
|---|---|---:|---:|---:|---:|
| 未訓練 | RALM | 20.46／63.33 | 18.83／67.83 | 13.11／53.16 | 4.49／21.47 |
| 未訓練 | InstructRAG | 16.84／54.95 | 15.05／70.61 | 8.26／43.60 | 6.26／22.71 |
| 未訓練 | IDEAL-RAG | 13.95／47.35 | 10.60／35.22 | 4.49／15.74 | 4.44／15.15 |
| 已訓練 | InstructRAG* | 11.53／50.68 | 14.64／63.15 | 7.34／39.77 | 4.03／21.84 |
| 已訓練 | IDEAL-RAG | 11.64／46.76 | 9.56／33.64 | 4.64／16.27 | 4.50／15.67 |

表 4.3 圖說：比較四個基準在部分及全部含答案段落污染下的準確率下降；原文稱 IDEAL-RAG 在有無微調時皆持續呈現最低衰減。

作者認為，IDEAL-RAG 不僅縮小雜訊情境的準確率差距，也保留更多乾淨資料上的能力，因而具備實務可靠性。

> 譯註：第一，「所有設定最低」有例外：已訓練 PopQA 與 MultiHopQA 的 Counter-Mix 都是 InstructRAG 較低。第二，式 4.2 是總準確率的「淨下降」，若存在原先答錯、污染後答對的題目，就不等於原先答對題目的失敗比例。第三，ADR 必須以相同題目子集的乾淨與污染結果計算。

### 4.4 內部機制分析

#### 4.4.1 反事實敏感度分數

對每個問答配對，測量將乾淨檢索替換成污染檢索後，答案分數的變化，見式 4.3。原文此處寫「answer logit 的下降」，但式 4.3 實際定義為對數機率差的絕對值。

我們以小提琴圖呈現 $\Delta\mathrm{CSS}$ 的經驗分布。作者將較胖、分散程度較大的小提琴解讀為檢索雜訊對信心的影響更強且變動更大。結果見圖 4.1：IDEAL-RAG 在 NQ 與 TriviaQA 的分布較集中，即使全部含答案段落受到對抗性修改，答案機率也較穩定；InstructRAG 的分布較寬且有較長尾部，反映其對檢索內容表面形式的依賴。

例如 NQ Counter-All 的平均 $\Delta\mathrm{CSS}$，IDEAL-RAG 為 0.830，InstructRAG 為 3.657。此差異與 ADR 分析的趨勢一致，作者據此認為 IDEAL-RAG 的決策邊界較穩定，較不易受誤導證據影響。

圖 4.1：比較乾淨與反事實檢索間答案 token 對數機率變化的小提琴圖。a、b 是 NQ／TriviaQA 的 Counter-Mix；c、d 是兩資料集的 Counter-All。藍色為 IDEAL-RAG，橘色為 InstructRAG。原圖說將較集中、中心較低的分布解釋為信心變化小。

> 譯註：小提琴在某一高度的寬度表示該分數附近的估計密度，不能單靠「寬」判斷變異量，應連同縱向範圍、分位數與中心位置閱讀。式 4.3 必定非負，圖 4.1 卻呈現延伸至負值的形狀；可能涉及帶正負號的實作或密度平滑延伸，僅憑圖無法確定，重現時需查程式。

#### 4.4.2 參數知識分數

當檢索不可靠時，我們衡量每個 Transformer 區塊必須注入多少參數知識，依式 4.5 計算逐層 $\Delta\mathrm{PKS}_{\ell}$，結果見圖 4.2。

圖 4.2：各 Transformer 層在檢索段落被反事實內容替換後的 PKS 變化。a、b 為 NQ／TriviaQA 的 Counter-Mix，c、d 為 Counter-All。作者指出 IDEAL-RAG 深層僅需較小額外參數輸入，而 InstructRAG 出現較大尖峰，顯示在檢索不可靠時才被動退回內部記憶。

> 譯註：圖 4.2 的圖說將橘色寫為 IDEAL-RAG、藍色寫為 InstructRAG；但圖內圖例相反，藍色是 IDEAL-RAG、橘色是 InstructRAG。讀圖應注意此標示矛盾。

**整體比較。** 在 NQ 與 TriviaQA 上，作者觀察到兩方法於雜訊下皆增加 PKS，並解讀為外部證據品質下降時，LLM 轉而使用儲存記憶。IDEAL-RAG 的 $\Delta\mathrm{PKS}$ 整體較低，作者解釋為它在早期萃取階段已呈現相關內部知識，減少之後透過知識 FFN 路徑追加資訊的需求。因此殘差流更穩定，降低幻覺風險；作者將此與 ReDeEP [38] 對後期過度活化及生成不穩定的觀察連結。

**依結果分組分析。** 為超越整體相關性，將 IDEAL-RAG 的預測分為正確與錯誤兩組。圖 4.3 中錯誤組的 $\Delta\mathrm{PKS}$ 較大。作者據此認為，剩餘錯誤往往發生在模型突然放大知識 FFN 貢獻，以補償誤導檢索的時候；相對地，較小的變化與可靠預測有關。

圖 4.3：綠色代表答對，紅色代表答錯。IDEAL-RAG 答錯時，後層 PKS 變化上升較劇烈，特別是最後兩個區塊；答對時增幅較小。作者因此將突然且大幅的參數 logits 變化視為幻覺警訊。子圖配置與圖 4.2 相同。

**InstructRAG 的結果分組分析。** 圖 4.4 中，InstructRAG 的正確及錯誤組沒有明確分離；深層曲線大幅重疊，兩組都出現尖峰。作者認為這符合被動且未校準的參數記憶回退：由於缺乏事先萃取與跨來源協調，當檢索不可靠時，模型會間歇性放大知識 FFN 路徑。這種後期放大是否有益，依個別案例的記憶是否正確、是否顯著而定，使變化幅度與準確率的關聯不穩定。

作者因此主張，只有像 IDEAL-RAG 一樣明確呈現並結構化參數證據時，$\Delta\mathrm{PKS}$ 才能作為可靠錯誤訊號；InstructRAG 的單次指令模式下，此分數主要反映不穩定的殘差競爭。作者認為這與 ReDeEP 的觀察及主要準確率結果一致。

圖 4.4：在 NQ 與 TriviaQA 的兩種污染設定下，正確及錯誤組皆有不規則後層尖峰，重疊很大，無穩定趨勢。此圖將 $\Delta\mathrm{PKS}$ 解讀為單次生成模式中的弱診斷訊號，配置與圖 4.2 相同。

作者總結：大型、突發的 $\Delta\mathrm{PKS}$ 尖峰是錯誤的重要指標；IDEAL-RAG 提前萃取內部知識，維持較平衡的殘差流並避免大幅尖峰，改善抗雜訊能力；InstructRAG 則以突然增加 FFN 貢獻的方式回應污染輸入。

> 譯註：依正誤分組的觀察支持相關性，尚不能單獨證明尖峰造成錯誤，也未建立能直接部署的警報門檻、偵測準確率或誤報率。PKS 是間接探測指標，不應等同「模型取出了多少正確事實」。

## 第 5 章　分析（正文第 33–38 頁）

本章從三個角度拆解 IDEAL-RAG：移除元件的消融實驗、改變訓練資料以區分架構與資料的影響，以及觀察模型面對反事實證據時注意位置的注意力探測。

### 5.1 消融研究

#### 5.1.1 框架消融

IDEAL-RAG 包含參數知識萃取 $E_{\mathrm{int}}$、雙來源觀點生成 $G_{\mathrm{int}},G_{\mathrm{ext}}$，及連結推理生成 $L$。我們評估兩種縮減版本。

**移除 $E_{\mathrm{int}}$ 與 $G$：** 仿照 InstructRAG 的單次生成方式，以單一提示（5.1）要求模型閱讀檢索段落、反思相關背景知識，再提出答案說明，但省略明確知識萃取與雙觀點階段。除此之外，指令風格、示例數、解碼設定及證據品質指引皆與 IDEAL-RAG 一致，使表現差異可歸因於被移除機制，而非提示設計。

**只移除 $G$：** 保留參數知識萃取，但跳過分別立論，將問題、檢索段落及萃取記憶直接交給融合提示（5.2）。

**提示詞 5.1：移除明確萃取與雙觀點**

> 主要任務是先反思有哪些可能相關的內部知識，再批判性分析提供的文件，以回答問題。請評估內外資訊相對於問題的相關性、準確性與充分性。
>
> 以下是推理示例：{B_inst*}。現在請分析文件 {retrieved documents}，依據內部知識與提供資訊回答問題 {question}。

提示詞 5.1 圖說：改良 InstructRAG 的答案不可見 ICL 提示；$B_{\mathrm{inst}}^\star$ 包含以 InstructRAG 在答案可見設定下生成的推理。

**提示詞 5.2：移除明確觀點生成**

> 主要任務是分析提供的外部文件與內部知識，以回答問題。評估各來源對回答問題的貢獻，以及是否支持一個或多個提出的答案標籤。
>
> 以下是推理示例：{B_one-step*}。現在請分析材料 {retrieved documents}，同時使用外部檢索文件與自己記憶中的文件資訊回答問題 {question}。

提示詞 5.2 圖說：在答案不可見 ICL 中，省略明確觀點 $G$，直接生成連結推理。

> 譯註：提示詞 5.2 的實際占位符沒有明確列出內部知識文件，雖然正文說有提供；「提出的答案標籤」也出現在聲稱答案不可見的提示中。這些都是需要實作釐清的細節，不能據此直接斷定測試洩漏。

**表 5.1　框架消融（EM，%）**

| 方法 | NQ 原始 | NQ Mix | NQ All | TriviaQA 原始 | TriviaQA Mix | TriviaQA All |
|---|---:|---:|---:|---:|---:|---:|
| 移除萃取及觀點 | 61.77 | 79.74 | 30.74 | 76.05 | 90.13 | 52.85 |
| 只移除觀點 | 60.86 | 76.99 | 48.71 | 76.07 | 92.20 | 76.68 |
| 完整模型 | 60.83 | 77.97 | 51.97 | 77.19 | 92.21 | 78.58 |

表 5.1 圖說：比較原始檢索、Counter-Mix 與 Counter-All，在同時移除知識萃取及觀點、只移除觀點，以及完整系統下的表現。

結果顯示：

- **參數萃取具有關鍵性。** 當系統縮減成不明確萃取知識、也不分離觀點的單次提示時，完全反事實污染下的表現大幅下降：NQ 從 51.97 降到 30.74，下降 21.23；TriviaQA 從 78.58 降到 52.85，下降 25.73。相較之下，乾淨與混合污染的變化大致在約 2% 內。作者認為，明確萃取參數知識及其搭配的雙觀點設計，是穩健性的核心來源；沒有它們，模型即使在較乾淨資料上表現相近，仍容易受到全面誤導。
- **觀點生成重要，但偏向互補。** 保留知識萃取、只移除觀點生成，作者描述為平均 EM 下降約 2–3%。這支持跨來源協調有益，但貢獻小於知識萃取。案例分析顯示，觀點生成有助於處理邊界情境、解決殘餘衝突、抑制錯誤線索，並產生一致且可解釋的理由；主要穩健性來源仍是事先喚起內部知識。因此深層分析著重知識萃取，將觀點生成視為輔助穩定機制。

> 譯註：表中差值以百分點計。六個欄位中，只移除觀點的平均下降約 1.18 個百分點，並非概括所稱的 2–3。另，表 5.1 完整模型的 NQ 數字對應表 4.2 未訓練版本，TriviaQA 數字卻對應已訓練版本，原文未說明此設定差異。消融也未獨立移除連結模組，不能據此說三個元件都被單獨驗證。

#### 5.1.2 答案包含分析

依照第 4.1.2 節的資料建構方式，將乾淨測試題依標準答案出現位置分類：

- inter_only，$D_{\mathrm{in}}$：標準答案出現在 $K_{\mathrm{int}}$，但不在檢索段落。
- exter_only，$D_{\mathrm{ex}}$：標準答案只在檢索段落。
- both_contained，$D_{\mathrm{both}}$：兩種來源都包含答案。

表 5.2 顯示，當模型已知道答案，或內外知識都包含答案時，IDEAL-RAG 持續優於 InstructRAG；只有答案僅存在檢索段落時表現下降。作者認為，明確使用參數記憶在本方法原本針對的情境中最有效。

**表 5.2　依答案位置分組的準確率（%）；每格依序為僅內部／僅外部／兩者皆有**

| 設定 | 方法 | PopQA | NQ | TriviaQA | MultiHopQA |
|---|---|---:|---:|---:|---:|
| 未訓練 | InstructRAG | 36.36／86.76／94.54 | 35.42／76.25／91.80 | 59.28／89.27／96.69 | 78.44／53.57／90.21 |
| 未訓練 | IDEAL-RAG | 54.55／82.34／95.45 | 71.88／70.07／93.03 | 81.01／78.66／97.21 | 86.11／36.88／91.06 |
| 已訓練 | InstructRAG* | 40.91／89.64／94.77 | 39.58／82.83／92.75 | 64.03／90.40／97.37 | 81.36／68.36／93.92 |
| 已訓練 | IDEAL-RAG | 63.64／86.69／96.82 | 71.88／70.07／93.03 | 83.23／78.19／97.83 | 90.29／44.41／94.01 |

表 5.2 圖說：對各資料集報告答案僅存在參數記憶、僅存在檢索段落，或兩者皆有時的準確率。

> 譯註：實際分類依據是生成文字 $K_{\mathrm{int}}$ 是否含答案字串，並非直接查看模型權重，因此「模型知道」只是操作性代理。表中沒有列出兩邊都不含答案的第四類，也未報告各分組題數。僅外部組的下降未必輕微，例如已訓練 MultiHopQA 為 68.36 對 44.41，相差 23.95 個百分點。

### 5.2 訓練資料分析

為驗證改善來自架構，而非僅來自資料，使用按第 4.1.2 節建立的 5,000 筆 NQ 反事實訓練案例，分別微調 IDEAL-RAG 與 InstructRAG，結果見表 5.3。

作者指出，加入雜訊訓練可提升 InstructRAG 的穩健性，但會降低乾淨資料準確率；相較之下，IDEAL-RAG 能在乾淨與雜訊資料上同時改善，且在雜訊下仍優於 InstructRAG，支持增益來自架構而非特定資料效果。

**表 5.3　NQ 不同訓練策略（EM 與 ADR，%）**

| 訓練資料 | 方法 | Mix 對應乾淨子集 | Mix | ADR Mix | All 對應乾淨子集 | All | ADR All |
|---|---|---:|---:|---:|---:|---:|---:|
| 一般資料 | InstructRAG* | 94.06 | 80.29 | 14.64 | 88.68 | 32.68 | 63.15 |
| 一般資料 | IDEAL-RAG | 89.53 | 80.97 | 9.56 | 83.6 | 55.48 | 33.64 |
| Counter-Mix | InstructRAG | 90.7 | 81.33 | 10.33 | 83.16 | 30.7 | 63.08 |
| Counter-Mix | IDEAL-RAG | 89.84 | 81.88 | 8.86 | 83.56 | 54.47 | 34.81 |
| Counter-All | InstructRAG | 90.7 | 83.11 | 8.37 | 83.48 | 37.27 | 55.35 |
| Counter-All | IDEAL-RAG | 90.02 | 82.86 | 7.95 | 83.96 | 55.56 | 33.83 |

表 5.3 圖說：在三種訓練條件下，比較符合反事實建構條件的乾淨子集、兩種污染測試及相應 ADR。InstructRAG* 是公開的全參數微調模型，其餘使用 PEFT。IDEAL-RAG 維持相近乾淨準確率，並在各訓練條件下得到較低 ADR。

> 譯註：原文「同時改善」不是每格成立。IDEAL-RAG 使用 Counter-Mix 訓練後，All 從 55.48 降至 54.47；Counter-All 訓練下的 Mix，InstructRAG 為 83.11，略高於 IDEAL-RAG 的 82.86。此外本表 InstructRAG* 的 All 32.68 與表 4.2 的 32.67 有 0.01 差異，本譯本保留各表原值。

### 5.3 注意力分布探測

為探測模型的決策焦點，聚合所有解碼層與注意力頭的 token 層級自注意力，再依檢索段落 $p_j$ 加總：

$$\mathrm{AttnScore}(p_j)=\sum_{\ell,h}\sum_{t\in p_j}\mathrm{softmax}(A_{\ell,h})_t.\tag{5.1}$$

$A_{\ell,h}$ 是第 $\ell$ 層、第 $h$ 個頭的原始注意力矩陣。

圖 5.1 展示一個 Counter-Mix 案例。InstructRAG 幾乎只關注一兩個段落，往往忽略真正含標準答案的段落；作者認為此模式解釋了它對污染的脆弱性。IDEAL-RAG 的注意力較平均，且對真正答案及反事實段落都給予較高權重，這兩種來源正是需要比較以支持或反駁主張的資訊。

圖 5.1：段落層級注意力熱圖。IDEAL-RAG 的關注分布於各段落，同時凸顯正確答案與反事實片段；InstructRAG 則集中於單一不相關段落。圖中 golden 表示正確答案段落，counterfactual 表示反事實段落，irrelevant 表示不相關段落。圖內橫向實際列為 Doc1–Doc5，縱向列為 L1–L32；原圖的座標軸標題疑有互換。

這種兼顧雙方的注意力模式符合連結推理模組的設計目的，並進一步支持 IDEAL-RAG 在雜訊檢索下的穩健性。

> 譯註：式 5.1 省略了注意力矩陣的查詢位置索引，無法只靠此式確定使用哪一個生成 token，或如何對多個位置聚合。注意力總和也可能受段落長度影響。單一案例中的熱圖與注意力大小，不能直接證明因果性或模型採信哪個來源。

### 5.4 分析總結

作者總結，各設計選擇，包括記憶萃取、雙觀點與連結式整合，都有助於抵抗誤導證據；即使改變訓練資料分布，IDEAL-RAG 的增益仍能持續。

## 第 6 章　結論（正文第 39 頁）

本研究從一個過去較少受到關注的角度重新檢視 RAG：語言模型自身的參數記憶。我們提出三階段 IDEAL-RAG：先讓模型呈現已知的問題相關資訊，再讓內外來源各自產生完整推理線，最後互相驗證雙方觀點、結合重疊線索、盡可能解決不一致，並綜合出獲得最一致支持的答案。

四個開放領域問答基準的實驗顯示，此分工在乾淨檢索下保留標準 RAG 的強勁表現，同時顯著減輕部分或完全反事實段落造成的準確率衰減。機制診斷亦支持此方向：較低 CSS 表示答案機率較不受雜訊擾動；逐層 PKS 分析呈現較穩定的內部記憶使用，依正誤分組觀察到的尖峰可作為錯誤警訊。消融分析凸顯各階段、尤其初始參數知識萃取的重要性。

IDEAL-RAG 顯示，明確建模並對齊內外證據，是提升 RAG 抗雜訊能力的有效途徑。研究發現指出，在 LLM 已知資訊與新讀資訊之間審慎協調，可為更可靠的 RAG 提供有原則的基礎。未來將把此協調框架延伸至更長上下文、自適應檢索，以及問答以外的多步驟推理任務。

> 譯註：原文結論有一句語意倒置，字面會變成「移除階段有助穩健性」；依上下文及消融數據，此處譯為「消融分析凸顯階段的重要性」。上述是作者結論，適用範圍仍受模型、資料集、污染建構方式、比較設定及前述數據例外限制。


## 參考文獻（保留原英文書目）

以下依原 PDF 保留 58 筆文獻，僅整理換行。作者、出版資訊與年份依原文，未逐項校訂；正文方括號編號對應此清單。

[1] Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, and Hannaneh Hajishirzi. Selfrag: Learning to retrieve, generate, and critique through self-reflection. In The Twelfth International Conference on Learning Representations , 2023.

[2] Bernd Bohnet, Vinh Q Tran, Pat V erga, Roee Aharoni, Daniel Andor, Livio Baldini Soares, Massimiliano Ciaramita, Jacob Eisenstein, Kuzman Ganchev, Jonathan Herzig, et al. Attributed question answering: Evaluation and modeling for attributed large language models. arXiv preprint arXiv:2212.08037, 2022.

[3] Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.

[4] Sébastien Bubeck, V arun Chadrasekaran, Ronen Eldan, Johannes Gehrke, Eric Horvitz, Ece Kamar, Peter Lee, Yin Tat Lee, Y uanzhi Li, Scott Lundberg, et al. Sparks of artificial general intelligence: Early experiments with gpt-4, 2023.

[5] Danqi Chen, Adam Fisch, Jason Weston, and Antoine Bordes. Reading wikipedia to answer open-domain questions. In 55th Annual Meeting of the Association for Computational Linguistics, ACL 2017 , pages 1870–1879. Association for Computational Linguistics (ACL), 2017.

[6] Jiawei Chen, Hongyu Lin, Xianpei Han, and Le Sun. Benchmarking large language models in retrieval-augmented generation. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 38, pages 17754–17762, 2024.

[7] Florin Cuconasu, Giovanni Trappolini, Federico Siciliano, Simone Filice, Cesare Campagnano, Y oelle Maarek, Nicola Tonellotto, and Fabrizio Silvestri. The power of noise: Redefining retrieval for rag systems. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval , pages 719– 729, 2024.

[8] Bhuwan Dhingra, Jeremy R Cole, Julian Martin Eisenschlos, Daniel Gillick, Jacob Eisenstein, and William W Cohen. Time-aware language models as temporal knowledge bases. Transactions of the Association for Computational Linguistics, 10:257–273, 2022.

[9] Feiteng Fang, Y uelin Bai, Shiwen Ni, Min Y ang, Xiaojun Chen, and Ruifeng Xu. Enhancing noise robustness of retrieval-augmented language models with adaptive adversarial training. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (V olume 1: Long Papers), pages 10028–10039, 2024.

[10] Y unfan Gao, Y un Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Y uxi Bi, Yi Dai, Jiawei Sun, Qianyu Guo, Meng Wang, et al. Retrieval-augmented generation for large language models: A survey. CoRR, 2023.

[11] Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. Retrieval augmented language model pre-training. In International conference on machine learning, pages 3929–3938. PMLR, 2020.

[12] Zeyu Han, Chao Gao, Jinyang Liu, Jeff Zhang, and Sai Qian Zhang. Parameterefficient fine-tuning for large models: A comprehensive survey. arXiv preprint arXiv:2403.14608, 2024.

[13] Xanh Ho, Anh-Khoa Duong Nguyen, Saku Sugawara, and Akiko Aizawa. Constructing a multi-hop qa dataset for comprehensive evaluation of reasoning steps. arXiv preprint arXiv:2011.01060, 2020.

[14] Or Honovich, Roee Aharoni, Jonathan Herzig, Hagai Taitelbaum, Doron Kukliansy, V ered Cohen, Thomas Scialom, Idan Szpektor, Avinatan Hassidim, and Y ossi Matias. True: Re-evaluating factual consistency evaluation. In Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pages 3905–3920, 2022.

[15] Edward J Hu, Y elong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Y uanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. Lora: Low-rank adaptation of large language models. arxiv 2021. arXiv preprint arXiv:2106.09685, 2021.

[16] Raisa Islam and Owana Marzia Moushi. Gpt-4o: The cutting-edge advancement in multimodal llm. Authorea Preprints, 2024.

[17] Gautier Izacard, Mathilde Caron, Lucas Hosseini, Sebastian Riedel, Piotr Bojanowski, Armand Joulin, and Edouard Grave. Unsupervised dense information retrieval with contrastive learning. Transactions on Machine Learning Research , 2023.

[18] Gautier Izacard, Patrick Lewis, Maria Lomeli, Lucas Hosseini, Fabio Petroni, Timo Schick, Jane Dwivedi-Y u, Armand Joulin, Sebastian Riedel, and Edouard Grave. Atlas: Few-shot learning with retrieval augmented language models. Journal of Machine Learning Research, 24(251):1–43, 2023.

[19] Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju Hwang, and Jong Park. Adaptiverag: Learning to adapt retrieval-augmented large language models through question complexity. In NAACL-HLT, 2024.

[20] Zhengbao Jiang, Frank F Xu, Luyu Gao, Zhiqing Sun, Qian Liu, Jane Dwivedi-Y u, Yiming Y ang, Jamie Callan, and Graham Neubig. Active retrieval augmented generation. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pages 7969–7992, 2023.

[21] Mandar Joshi, Eunsol Choi, Daniel S Weld, and Luke Zettlemoyer. Triviaqa: A large scale distantly supervised challenge dataset for reading comprehension. arXiv preprint arXiv:1705.03551, 2017.

[22] Vladimir Karpukhin, Barlas Oguz, Sewon Min, Patrick SH Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih. Dense passage retrieval for open-domain question answering. In EMNLP (1), pages 6769–6781, 2020.

[23] Urvashi Khandelwal, Omer Levy, Dan Jurafsky, Luke Zettlemoyer, and Mike Lewis. Generalization through memorization: Nearest neighbor language models. In Proceedings of ICLR, 2020.

[24] Tom Kwiatkowski, Jennimaria Palomaki, Olivia Redfield, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Kenton Lee, et al. Natural questions: a benchmark for question answering research. Transactions of the Association for Computational Linguistics , 7:453–466, 2019.

[25] Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Y u, Joseph Gonzalez, Hao Zhang, and Ion Stoica. Efficient memory management for large language model serving with pagedattention. In Proceedings of the 29th Symposium on Operating Systems Principles , pages 611–626, 2023.

[26] Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, et al. Retrieval-augmented generation for knowledge-intensive nlp tasks. Advances in neural information processing systems, 33:9459–9474, 2020.

[27] Daliang Li, Ankit Singh Rawat, Manzil Zaheer, Xin Wang, Michal Lukasik, Andreas V eit, Felix Y u, and Sanjiv Kumar. Large language models with controllable working memory. In Findings of the Association for Computational Linguistics: ACL 2023 , pages 1774–1793, 2023.

[28] Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. arXiv preprint arXiv:1711.05101, 2017.

[29] Alex Mallen, Akari Asai, Victor Zhong, Rajarshi Das, Hannaneh Hajishirzi, and Daniel Khashabi. When not to trust language models: Investigating effectiveness and limitations of parametric and non-parametric memories. arXiv preprint, 2022.

[30] Alex Mallen, Akari Asai, Victor Zhong, Rajarshi Das, Daniel Khashabi, and Hannaneh Hajishirzi. When not to trust language models: Investigating effectiveness of parametric and non-parametric memories. In ACL, 2023.

[31] Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. Training language models to follow instructions with human feedback. Advances in neural information processing systems, 35:27730–27744, 2022.

[32] Samyam Rajbhandari, Jeff Rasley, Olatunji Ruwase, and Y uxiong He. Zero: Memory optimizations toward training trillion parameter models. In SC20: International Conference for High Performance Computing, Networking, Storage and Analysis , pages 1–16. IEEE, 2020.

[33] Ori Ram, Y oav Levine, Itay Dalmedigos, Dor Muhlgay, Amnon Shashua, Kevin Leyton-Brown, and Y oav Shoham. In-context retrieval-augmented language models. Transactions of the Association for Computational Linguistics , 11:1316–1331, 2023.

[34] Adam Roberts, Colin Raffel, and Noam Shazeer. How much knowledge can you pack into the parameters of a language model? In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP) , pages 5418–5426, 2020.

[35] Stephen E Robertson and Steve Walker. Some simple effective approximations to the 2-poisson model for probabilistic weighted retrieval. In SIGIR＇94: Proceedings of the Seventeenth Annual International ACM-SIGIR Conference on Research and Development in Information Retrieval, organised by Dublin City University , pages 232–241. Springer, 1994.

[36] John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

[37] Freda Shi, Xinyun Chen, Kanishka Misra, Nathan Scales, David Dohan, Ed H Chi, Nathanael Schärli, and Denny Zhou. Large language models can be easily distracted by irrelevant context. In International Conference on Machine Learning, pages 31210– 31227. PMLR, 2023.

[38] ZhongXiang Sun, Xiaoxue Zang, Kai Zheng, Jun Xu, Xiao Zhang, Weijie Y u, Y ang Song, and Han Li. Redeep: Detecting hallucination in retrieval-augmented generation via mechanistic interpretability. In The Thirteenth International Conference on Learning Representations, 2025.

[39] Gemini Team, Rohan Anil, Sebastian Borgeaud, Jean-Baptiste Alayrac, Jiahui Y u, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, Katie Millican, et al. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805, 2023.

[40] Nandan Thakur, Luiz Bonifacio, Xinyu Zhang, Odunayo Ogundepo, Ehsan Kamalloo, David Alfonso-Hermelo, Xiaoguang Li, Qun Liu, Boxing Chen, Mehdi Rezagholizadeh, et al. Nomiracl: Knowing when you don’t know for robust multilingual retrieval-augmented generation. CoRR, 2023.

[41] Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Y asmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023.

[42] Hitesh Wadhwa, Rahul Seetharaman, Somyaa Aggarwal, Reshmi Ghosh, Samyadeep Basu, Soundararajan Srinivasan, Wenlong Zhao, Shreyas Chaudhari, and Ehsan Aghazadeh. From rags to rich parameters: Probing how language models utilize external knowledge over parametric information for factual queries. CoRR, 2024.

[43] Fei Wang, Xingchen Wan, Ruoxi Sun, Jiefeng Chen, and Sercan Ö Arık. Astute rag: Overcoming imperfect retrieval augmentation and knowledge conflicts for large language models. arXiv preprint arXiv:2410.07176, 2024.

[44] Zihao Wang, Anji Liu, Haowei Lin, Jiaqi Li, Xiaojian Ma, and Yitao Liang. Rat: Retrieval augmented thoughts elicit context-aware reasoning in long-horizon generation. CoRR, 2024.

[45] Zhepei Wei, Wei-Lin Chen, and Y u Meng. Instructrag: Instructing retrieval-augmented generation via self-synthesized rationales. In The Thirteenth International Conference on Learning Representations, 2025.

[46] Siye Wu, Jian Xie, Jiangjie Chen, Tinghui Zhu, Kai Zhang, and Y anghua Xiao. How easily do irrelevant inputs skew the responses of large language models? CoRR, 2024.

[47] Y uanhao Wu, Juno Zhu, Siliang Xu, Kashun Shum, Cheng Niu, Randy Zhong, Juntong Song, and Tong Zhang. Ragtruth: A hallucination corpus for developing trustworthy retrieval-augmented language models. CoRR, 2024.

[48] Chong Xiang, Tong Wu, Zexuan Zhong, David Wagner, Danqi Chen, and Prateek Mittal. Certifiably robust rag against retrieval corruption. In ICML 2024 Next Generation of AI Safety Workshop, 2024.

[49] Peng Xu, Wei Ping, Xianchao Wu, Lawrence McAfee, Chen Zhu, Zihan Liu, Sandeep Subramanian, Evelina Bakhturina, Mohammad Shoeybi, and Bryan Catanzaro. Retrieval meets long context large language models. In The Twelfth International Conference on Learning Representations , 2023.

[50] Rongwu Xu, Zehan Qi, Zhijiang Guo, Cunxiang Wang, Hongru Wang, Y ue Zhang, and Wei Xu. Knowledge conflicts for llms: A survey. In Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, pages 8541–8565, 2024.

[51] Zhilin Y ang, Peng Qi, Saizheng Zhang, Y oshua Bengio, William W Cohen, Ruslan Salakhutdinov, and Christopher D Manning. Hotpotqa: A dataset for diverse, explainable multi-hop question answering. arXiv preprint arXiv:1809.09600, 2018.

[52] Ori Y oran, Tomer Wolfson, Ori Ram, and Jonathan Berant. Making retrieval-augmented language models robust to irrelevant context. In ICLR 2024 Workshop on Large Language Model (LLM) Agents , 2024.

[53] Wenhao Y u, Dan Iter, Shuohang Wang, Yichong Xu, Mingxuan Ju, S Sanyal, Chenguang Zhu, Michael Zeng, and Meng Jiang. Generate rather than retrieve: Large language models are strong context generators. In International Conference on Learning Representations, 2023.

[54] Wenhao Y u, Hongming Zhang, Xiaoman Pan, Peixin Cao, Kaixin Ma, Jian Li, Hongwei Wang, and Dong Y u. Chain-of-note: Enhancing robustness in retrieval-augmented language models. In Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, pages 14672–14685, 2024.

[55] Wenhao Y u, Zhihan Zhang, Zhenwen Liang, Meng Jiang, and Ashish Sabharwal. Improving language models via plug-and-play retrieval feedback. arXiv preprint arXiv:2305.14002, 2023.

[56] Tianjun Zhang, Shishir G Patil, Naman Jain, Sheng Shen, Matei Zaharia, Ion Stoica, and Joseph E Gonzalez. Raft: Adapting language model to domain specific rag. In First Conference on Language Modeling , 2024.

[57] Ruochen Zhao, Xingxuan Li, Shafiq Joty, Chengwei Qin, and Lidong Bing. V erify-andedit: A knowledge-enhanced chain-of-thought framework. In The 61st Annual Meeting Of The Association For Computational Linguistics , 2023.

[58] Y utao Zhu, Huaying Y uan, Shuting Wang, Jiongnan Liu, Wenhan Liu, Chenlong Deng, Haonan Chen, Zheng Liu, Zhicheng Dou, and Ji-Rong Wen. Large language models for information retrieval: A survey. arXiv preprint arXiv:2308.07107, 2023.
