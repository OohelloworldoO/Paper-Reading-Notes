# Compare

| 符號      | 意義                         |
| :-------- | :--------------------------- |
| $q$       | 問題                         |
| $D$       | 檢索文件                     |
| $a$       | 已知標準答案                 |
| $K_{int}$ | 模型依問題產生的內部背景文字 |
| $S_{int}$ | 根據內部知識形成的觀點       |
| $E_{int}$ | 根據外部文件形成的觀點       |
| $G_{int}$ | 內部觀點生成                 |
| $G_{ext}$ | 外部觀點生成                 |
| $S_{ext}$ | 根據外部文件形成的觀點       |
| $B$       | 其他題目構成的示範庫         |

不能將差異簡化為「只有 IDEAL-RAG 擁有內部知識」。IDEAL-RAG 的設計特色，是將獨立回想、雙觀點生成與連結整合明確拆開

| Type             | 簡要                                                           | Algorithm                                                                                                                                                                                                                                                                                                                             |
| :--------------- | :------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Basic RAG        | 提供相關檢索文件，讓模型生成答案；不排除模型使用自身知識       | user -> $q$ -> 檢索 $D$ -> $q$ + $D$ 交給語言模型 -> response                                                                                                                                                                                                                                                                         |
| InstructRAG(ICL) | 用 answer-seen 自生成 rationale 建立示範，引導新題的去雜訊回答 | 建立示範(那些文件有助於得到答案?如何支持答案?如果文件都沒有幫助，是否能由自身知識說明?) -> 回答新題目(ICL、SFT/FT)                                                                                                                                                                                                                    |
| IDEAL-RAG (ICL)  | 獨立回想、分開內外觀點，再比較整合                             | $K_{\mathrm{int}}\leftarrow E_{\mathrm{int}}(q);\quad(\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}})\leftarrow(G(q,K_{\mathrm{int}};\mathcal B_{\mathrm{int}}),G(q,D;\mathcal B_{\mathrm{ext}}));\quad\hat R_{\mathrm{link}}\leftarrow L(q,D,K_{\mathrm{int}},\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}};\mathcal B_{\mathrm{link}})$$ |

![](./images/Dual-Source%20Standpoint%20Generation%20&%20Linked%20Rationale%20Generation.png)

$$
\begin{aligned}
K_{\mathrm{int},i}^{\star}
&\leftarrow E_{\mathrm{int}}(q_i;\Theta_0),\\
S_{\mathrm{int},i}^{\star}
&\leftarrow G(q_i,a_i,K_{\mathrm{int},i}^{\star};\Theta_0),\\
S_{\mathrm{ext},i}^{\star}
&\leftarrow G(q_i,a_i,D_i;\Theta_0),\\
R_{\mathrm{link},i}^{\star}
&\leftarrow L(q_i,a_i,D_i,K_{\mathrm{int},i}^{\star},
S_{\mathrm{int},i}^{\star},S_{\mathrm{ext},i}^{\star};\Theta_0).
\end{aligned}
$$

## 補充

# ICL & SFT/FT

- ICL(In-Context Learning 上下文學習): 模型不修改權重，僅透過在輸入 Prompt 中提供幾個範例(Examples/Shots)，就能讓模型根據上下文直接進行推理和預測
- SFT(Supervised Fine-Tuning 監督式微調): 模型根據透過標註數據及進行參數更新(梯度下降與權重調整)，學習特定任務的輸出風格與專業知識
- FT(Fine-Tuning)

| 特點 | ICL                                                                |                          SFT                           | FT  |
| :--: | :----------------------------------------------------------------- | :----------------------------------------------------: | :-: |
|  1.  | 受限於模型上下文長度(Context Window)且每次推理都需要消耗更多 Token | 模型內部權重會被修改，使其永久記住特定的輸出格式與風格 |     |
|  2.  | _零參數更新_ 模型沒有真正學到新知識，只是在當前對話模仿犯例        |                                                        |     |
|  3.  | _即時性_ 換一個提示詞，模型就切換到另一個任務                      |                                                        |     |

_`SFT`、`FT`差別在 SFT 必須有明確的問題與標準答案， FT 是用來學習內容_

### e.g.

- 做完 `FT` 後的模型：像是一個「剛讀完醫學院、滿腹經綸但沒實習過學生」。你給他看一個醫學名詞，他可以滔滔不絕地把課本接龍背下去，但如果你問他：「醫生，我頭痛該怎麼辦？」，他可能不知道該用醫生的語氣安慰你並開處方，反而會繼續接龍背誦頭痛的學術定義。 
- 再做完 `SFT` 的模型：像是一個「經過臨床實習、知道怎麼看診的醫生」。他學會了「病人問診(Prompt) -> 醫生給予診斷與處方（Response）」的互動模式，能夠用專業、有禮貌的格式回答問題。
