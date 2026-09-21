# Compare

| 符號                                                                             | 意義                                         |
| :------------------------------------------------------------------------------- | :------------------------------------------- |
| $q$                                                                              | 一個問題                                     |
| $D=\mathcal{R}(q)$                                                               | 檢索器 $\mathcal{R}$ 回傳的文件集合          |
| $a$                                                                              | 標準答案；seed 建庫可見，測試推論不可見      |
| $\Theta_0$                                                                       | 固定的 backbone 模型參數                     |
| $E_{\mathrm{int}}$                                                               | 內部知識回想／萃取模組                       |
| $K_{\mathrm{int}}$                                                               | 回想模組產生的背景文字，不保證事實正確       |
| $G$                                                                              | 觀點生成模組；內外分支使用不同提示與來源     |
| $S_{\mathrm{int}},S_{\mathrm{ext}}$                                              | 內部、外部觀點，包含答案主張與支持說明       |
| $L$                                                                              | 連結與整合生成模組                           |
| $R_{\mathrm{link}}$                                                              | 最後連結說明，包含最終答案                   |
| $\hat a$                                                                         | 從最後輸出取出的預測答案；本筆記另加的記號   |
| $\mathcal B_{\mathrm{int}},\mathcal B_{\mathrm{ext}},\mathcal B_{\mathrm{link}}$ | 三個 few-shot 示範庫，實作包含示範輸入與輸出 |

不能將差異簡化為「只有 IDEAL-RAG 擁有內部知識」。IDEAL-RAG 的設計特色，是將獨立回想、雙觀點生成與連結整合明確拆開

| Type             | 簡要                                                           | Algorithm                                                                                                                                                                                                                                                                                                                            |
| :--------------- | :------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Basic RAG        | 提供相關檢索文件，讓模型生成答案；不排除模型使用自身知識       | user -> $q$ -> 檢索 $D$ -> $q$ + $D$ 交給語言模型 -> response                                                                                                                                                                                                                                                                        |
| InstructRAG(ICL) | 用 answer-seen 自生成 rationale 建立示範，引導新題的去雜訊回答 | 建立示範(那些文件有助於得到答案?如何支持答案?如果文件都沒有幫助，是否能由自身知識說明?) -> 回答新題目(ICL、SFT/FT)                                                                                                                                                                                                                   |
| IDEAL-RAG (ICL)  | 獨立回想、分開內外觀點，再比較整合                             | $K_{\mathrm{int}}\leftarrow E_{\mathrm{int}}(q);\quad(\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}})\leftarrow(G(q,K_{\mathrm{int}};\mathcal B_{\mathrm{int}}),G(q,D;\mathcal B_{\mathrm{ext}}));\quad\hat R_{\mathrm{link}}\leftarrow L(q,D,K_{\mathrm{int}},\hat S_{\mathrm{int}},\hat S_{\mathrm{ext}};\mathcal B_{\mathrm{link}})$ |

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

| 特點 | ICL                                                                |                                   SFT                                    |
| :--: | :----------------------------------------------------------------- | :----------------------------------------------------------------------: |
|  1.  | 受限於模型上下文長度(Context Window)且每次推理都需要消耗更多 Token | 模型內部權重會被修改，使其記住特定的輸出格式與風格，但仍會遺忘或泛化失敗 |
|  2.  | _零參數更新_ 模型不更新權重與參數，只是在當前對話模仿犯例          |                                                                          |
|  3.  | _即時性_ 換一個提示詞，模型就切換到另一個任務                      |                                                                          |

_`SFT`、`FT`差別在 SFT 必須有明確的問題與標準答案， FT 是用來學習內容_

### e.g.

- 做完 `FT` 後的模型：像是一個「剛讀完醫學院、滿腹經綸但沒實習過學生」。你給他看一個醫學名詞，他可以滔滔不絕地把課本接龍背下去，但如果你問他：「醫生，我頭痛該怎麼辦？」，他可能不知道該用醫生的語氣安慰你並開處方，反而會繼續接龍背誦頭痛的學術定義。 
- 再做完 `SFT` 的模型：像是一個「經過臨床實習、知道怎麼看診的醫生」。他學會了「病人問診(Prompt) -> 醫生給予診斷與處方（Response）」的互動模式，能夠用專業、有禮貌的格式回答問題。
