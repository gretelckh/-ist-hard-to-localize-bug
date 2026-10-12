# 【恢复入口】IST 论文工作区 —— 闪退恢复指南

> 目的：如果本会话闪退/重开，让 AI **只读本文件**就能恢复：
> 在做什么、做到哪、历史记录在哪、下一步做什么、有哪些权威数字。

> ## 🧭【文件职责 · 自动更新规则 · 每次必做】（2026-10-11 制定，长期有效）
> **问题**：之前进度散落在太多文件（TASK/QHISTORY/docs/根目录），导致不知道哪是最新、该看哪个。
> **规则**：按下列"唯一权威"划分，**以后所有更新都写进固定位置，不要新开文件、不要散落**。
>
> | 文件 | 职责（唯一） | 何时更新 |
> |---|---|---|
> | **`RECOVERY_README.md`** | **"现在在做什么/做到哪/下一步"的唯一权威**（重开第一眼读这个） | 每次工作结束，改 `§0 一句话现状` + `§2 顶部提示` + 相关小节 |
> | **`QHISTORY.md`** | **时间线日志（只追加、不修改旧条目）**，记录每轮的来龙去脉 | 每次工作结束，**在末尾追加**本轮日志（带日期+序号） |
> | **`TASK.md`** | 数据重构/复现线的"进度细节+待办清单" | 只在该线有实质进展时更新 |
> | **`MCP-Fault-Benchmark\docs\numbers.md`** | **所有权威数字**（写论文/核对用） | 数字变化时更新 |
> | **`MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md`** | **49-bug 实证线的详细接续指引**（代码地图/运行顺序/交接） | 49-bug 实验有进展时更新 |
> | **`MCP-Fault-Benchmark\docs\ANALYSIS_PROGRESS.md`** | 分析进度交接（已完成勿重跑） | 分析完成时更新 |
> | **`MCP-Fault-Benchmark\docs\REPRO_49_ANALYSIS_DRAFT.md`** | 49 条三通道论文草稿（表格+正文） | 分析数字定稿时同步 |
> | `docs/` 其余（DATA_REBUILD / REPRO_PROGRESS / FUNNEL_TABLE / HARD_TO_LOCALIZE / FAULT_NATURE_293 / taxonomy / real_*） | **阶段产物/参考草稿**，非当前状态来源 | 只读参考，不追最新 |
>
> **执行准则**：
> 1. **恢复时**：读 `RECOVERY_README.md` → `docs\EXPERIMENTS_49.md` + `docs\ANALYSIS_PROGRESS.md`（49-bug 线）→ `TASK.md`（数据重构线）→ `QHISTORY.md` 末尾（最近一次）。
> 2. **遇到"哪个是最新"冲突时**：一律以 **`RECOVERY_README.md` 的 `§0 一句话现状` + `§2 顶部提示`** 为准，其次 `docs\numbers.md`。
> 3. **不要新建 .md 记录文件**；已有 `docs\` 草稿就更新它，不要另起炉灶。
> 4. **每轮结束必做**：追加 `QHISTORY.md` + 更新 `RECOVERY_README.md` §0/§2（+ 数字变则更新 `docs\numbers.md`）。

> ## ⚠️【永久性操作约定 · 每次必做】
> **每次完成一轮工作后，必须立即更新记录文件**：`QHISTORY.md` 末尾追加本轮日志；若改动影响
> 权威数字/进度/待办，同步更新 `RECOVERY_README.md`（§0/§2）与 `docs\numbers.md`（数字）。此约定长期有效，不得遗漏。

> ## ⚠️【语言约定 · 长期有效，每次必做】
> **与用户沟通一律使用中文**（对话、解释、汇报、提问、进度说明都用中文）。
> 代码、文件名、变量名、LaTeX 正文保持英文。此约定长期有效，不得用英文与用户交流。

> ## ⚠️【Token 上限约定 · 防闪退】
> 用户在 2026-09-30 观察到自己每次到 **260,000 token** 就会闪退。
> **当本轮累计 token 临近 250,000 时，必须立即停止继续工作**，先把当前所有已做改动完整保存到
> 记录文件（`QHISTORY.md` 追加日志 + 同步 `TASK.md` / `RECOVERY_README.md`），用一条简短消息确认
> 已保存、并说明"刚完成到哪、还剩什么"后，再结束本轮。**切勿拖到 260,000 因闪退丢失进度。**

---

## 0. 一句话现状

把已发表的 **QRS 会议版**（纯访谈）扩展重写成 **IST 期刊版**。
核心主题：**为什么 MCP 的 bug 这么难定位**（fault localization / 故障定位根因实证研究）。

> ## ⭐【2026-10-11 最新工作区 · 用户在改「IST_Right_merged」这套 · 最近 zip 见下】
> **用户指定的主工作区 = `C:\Users\kehuichen2\Desktop\IST\IST_Right_merged`**（`main.tex` + `sec_*.tex`
> 按章节拆分，格式用户认为"比较对"）。这一套已全部统一到 49-bug/真实 bug 口径，且**额外加了**：
> - **数据层表格**：`tab:funnel`（数据集漏斗表，已按用户要求**删掉 439 行**，只留 1343→398→−56→342→49/293；
>   "49 Reproduced at runtime" 行已加粗）、`tab:notrepro`（293 无法复现原因分类表，reason 列靠左）。
> - **主图** `fig_main_alluvial_with_ids`（Figure 3，跨双栏 `figure*` 放大，标题已精简为一句）。
> - **已删**旧三通道图 `fig:causal_graph`（Figure 4，与 Figure 3 功能重复，用户确认删除）。
> - **所有表/图标题已全部压成一句话**（caption 单句）。
> ⚠️ **【最近 zip = `C:\Users\kehuichen2\Desktop\IST\IST_Right_merged_49bug_v2.zip`】**（27 个文件，自包含可编译；
>   `main.tex` 直接 `\input{sec_*.tex}`，同目录 cas-* 文件 + `figs/`）。已含本轮全部改动。
> ⚠️ **【本轮已完成（2026-10-11 续26）】**：
> - **Table 4（`tab:repro49`）两项已改**：① 分组 `\multicolumn` 行 → **单独一列 Channel**（表变 4 列：
>   Channel|Issue|Origin|Exposure）；② Exposure 列改**两端对齐**（`>{\centering\arraybackslash}X`→默认 `X`）。
> - **删 Research highlights 环境**（main.tex，用户要求不逐条 item）。
> - **Figure 6（`fig:topk`）改为白话表格 `tab:topk`**：表头"大层+小层"结构（`Number of attempts to localise`
>   横跨3列 + `\cmidrule`，子列 `1st/2nd/3rd`）；正文改白话"定位 bug 所在层需几次"，引用改为 `tab:topk`。
> - **Figure 4 caption 精简**为 `Silent failures account for 22.4% (11/49) of the reproduced real bugs.`
> - **去全文箭头 `\rightarrow`**（6 处，改 from X to Y）；**Alluvial caption 已还原**。
> ⚠️ **【本轮未完成】**：英文版**长破折号 `---` 仍有残留**（sec_setup/sec_results/sec_intro/sec_discussion/main.tex
>   约 17 处，用户要求删，本轮只处理了中文版）；`--` 数字范围保留。
> - **另外两套也改过但非当前主工作区**：`main_review/`（投稿版，zip=`IST_Right_updated_v4.zip`）、
>   `paper/main_body.tex`（已标记废弃）。
> - **中文版交付物**：`C:\Users\kehuichen2\Desktop\IST\中文版审阅.md` + `中文版审阅.pdf`（全部章节中文翻译，
>   pandoc md→html + Chrome headless --print-to-pdf）。

> ## 🆕【2026-10-11 晚 · 论文已统一到 49-bug 口径 + 投稿 zip v4 已打包】
> **投稿版 `main_review/`（01-08，RQ1-4）已全部统一到 49-bug/真实 bug 口径**，旧合成 MCP-Fault-20
> 章节已彻底移除（intro/method/setup/results/discussion/conclusion 全部改齐）。5 张被引用图
> （fig_layer_distribution / fig_causal_graph / fig_silent_failure / fig_diag_clues / fig_topk）
> 已用 49-bug 权威数据重画（脚本 `MCP-Fault-Benchmark/analysis/make_49_figs.py`，输出到
> `MCP-Fault-Benchmark/figs/` 与 `paper/figs/`）。
> **投稿 zip 已打包 = `C:\Users\kehuichen2\Desktop\IST\IST_Right_updated_v4.zip`**（自包含可编译：
> `paper/`(main_review.tex/main.tex/main_body.tex/cas-*/figs) + `main_review/01..08`；
> `main_review.tex` 用 `\input{../main_review/01..08}`，zip 内路径自洽）。
> ⚠️ **`main_body.tex`（旧 RQ1-3 整稿）已标记为废弃**（被 main_review/ 取代），其内
> "MCP-Fault-20 合成数据集构建"章节为旧体系，勿当作当前口径。**投稿打包一律以 main_review/ 为准。**
> 剩余待办：① 数据集匿名 repo/DOI（正文红 TODO 未填）；② Phase C 修复实验（已决策延后）；
> ③ 293 未复现 bug 分析（最后决定）。

> ## ⭐【2026-10-11 最新 · 项目已推进到"49-bug 实证分析"主线】
> **数据集已彻底改为真实 bug 单一集（不再用合成 MCP-Fault-20）。** 当前状态（详细见 §2 顶部提示 + docs/）：
> - 漏斗：**1343 → 439 → 398 → 剔除56(2.2.0已修复) → 342 有效 → 49 复现 / 293 未复现**。
> - 49-bug 三通道实证：**mismatch 76.9%（10/13）、silent 22.4%（11/49）、genericised 34.7%（17/49）**。
> - **LLM 诊断基线（49 条真实 bug）：整体 77.6%（38/49），但【非Server源仅 15.4%（2/13）】——诚实硬核数字**。
> - **Top-K 已跑（2026-10-11）：整体 Top-1 79.6%/Top-2 87.8%/Top-3 95.9%；非Server源 Top-1 23.1%/Top-2 53.8%/Top-3 84.6%**（见 `docs/TopK_49_RESULTS.md`）。
> - **诊断线索干预 Phase B 已跑（2026-10-11）：基线 77.6%/15.4% → 诚实线索 79.6%/23.1%（非Server源 +7.7pp）→ 裸标签负对照 73.5%/0.0%**（见 `docs/CLUES_49_RESULTS.md`，证明提升来自指引内容非泄漏标签）。
> - **49-bug 实验未完：修复实验（Phase C，需决策自动可验证性）未跑**；然后把 49-bug 叙事写进论文 .tex（草稿在 `docs/REPRO_49_ANALYSIS_DRAFT.md`）。
> - ⚠️ **恢复时 FIRST 读 `MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md` + `docs\ANALYSIS_PROGRESS.md`**（详见 §2）。
> - **旧口径（合成 MCP-Fault-20 / 80 runs / 70.8%）已废弃，勿当成最新。**

> ## 🆕【2026-10-08 数据口径重构进行中】
> 用户决定把论文从「合成 MCP-Fault-20(80 runs, in-memory) + 真实集(28 runs)」改为「**只保留一个真实数据集，全部真实 bug，统一 Streamable-HTTP 传输**」。
> 正在重建官方 issue 全量库（python-sdk，1,343 条纯 issue，只研究这一个库）。
> **详细进度见 `TASK.md` §8 与 `MCP-Fault-Benchmark\docs\DATA_REBUILD_PROGRESS.md`。**
>
> ## ✅【2026-10-10 数据口径变更：398 → 350（剔除已修复）】
> 用户决定：**凡是已在 mcp 2.2.0 修复的 bug（fixed-in-current，48 条）从数据集剔除**，因为它们对当前研究版本
> 不再是有效缺陷。数据集从 **398 → 350**。剔除清单在 `data/full_pool/fixed_removed.json`（48 条 issue 号）；
> `make_all_bugs_excel.py` / `assess_reproducibility.py` 已读它过滤，产物自动变 350。原始 398 普查池保留在
> `confirmed_bugs.json`（作调查全池）。层分布（350，origin 4 层）= Server 93 / Client 121 / Transport 87 / Host 49；
> open/closed = 94 / 256；复现 48（18 verified + 30 batch）。**论文 sec:sampling 已按"398 确认 → 剔除 48 已修复 →
> 350 有效"叙事改写**（main_body + main_review/04_setup 双份）。**这些 350 数字用 `analysis/dataset_stats.py` 复现**
> （→ `data/full_pool/dataset_stats.json`），勿手算。
> ⚠️ **【2026-10-10 更晚】数据集已进一步缩到 342**（batch12 真跑剔除 192/594/838/753/3493/212/1363/1577 共 8 条；
> fixed_removed.json 现 56 条）。当前分布（342）：Server 91 / Client 118 / Transport 85 / Host 48；open/closed 93/249；
> 复现仍 48。**论文 sec:sampling 旧写 350，第④步改写时须同步为 342 的新分布。**
>
> ## ✅【初筛+人工复核已完成，下次不要重复跑！】
> **全池已拉齐 = 官方全部 1,343 条纯 issue**（补拉 200 条后）。初筛关键词分类：
> **BUG 439 / OTHER 457 / QUESTION 277 / FEATURE 88 / CI-REFACTOR 47 / DOC 35**。
> **人工复核 439 条关键词-BUG → 保留真 bug 398 条**（只要是 bug 就保留，含功能缺失/规格不符型；仅排除 41 条真非 bug：使用疑问19/纯功能请求4/非SDK 2/环境-依赖-打包7/CI-测试-重构5/重复3/无法验证1）。
> **筛选漏斗：1,343 → 439 → 398**。
> **结果已持久化，下次直接读这几个文件，不要重新拉取/初筛/复核：**
> - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\full_pool_screened.json`（**1,343 条**，每条带初筛 label）
> - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\bug_review_verdicts.json`（439 条复核 verdict(BUG/NOT_BUG)+原因）
> - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\bug_review_full.xlsx`（439 条复核 Excel）
> - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\confirmed_bugs.json`（**398 条**真 bug，含 state/created/url/body_head）
> - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\confirmed_bugs.xlsx`（**398 条**真 bug Excel）
> 复现脚本：`analysis/pull_remaining_issues.py`、`analysis/screen_issues.py`、`analysis/review_bugs.py`、`analysis/make_review_excel.py`。
>
> ## ✅【最新标记：数据集建立过程这一段是最新的】
> 论文里 **"Dataset Construction and Sampling Rationale"（sec:sampling）** 这一节 = 最新、已定稿，
> 描述 **398 真 bug 普查**（1,343→439→398）。**别被论文其余部分旧口径（MCP-Fault-20/80 runs/18 复现）误导**。
> 位置：工作版 `paper/main_body.tex`（约 L600）、审阅版 `main_review/04_setup.tex`（约 L173）。
> 全文其余部分暂未改，等 398 实验重跑后统一改写（清单见 `TASK.md` §9.4）。
> **改完看全文是否统一：** 全局搜 `MCP-Fault-20`/`80 runs`/`18 issues`/`4 variants`/`in-memory` 应全替换。
>
> ## 📌【待办 · 完成后发布 GitHub】
> 数据重构全部完成后，需把所有实验代码、数据、脚本、Excel、结果**统一整理发布到 GitHub 仓库**（含 README + 可复现说明）。匿名 repo/DOI 是正文红 TODO，待填。

---

## 1. 关键文件路径

| 作用 | 路径 |
|---|---|
| **恢复入口（本文件）** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\RECOVERY_README.md` |
| **单一事实来源（权威进度）** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\TASK.md` |
| **对话/问答时间线** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\QHISTORY.md` |
| **论文中文版** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\paper_chinese.md` |
| **论文数据/脚本基准** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\` |
| **投稿正文稿（最新zip = v3）** | `C:\Users\kehuichen2\Desktop\IST\IST_Right_updated_v3.zip`（2026-10-08 20:39，含阶段A.5/B/C） |
| **数据重构详细记录** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\docs\DATA_REBUILD_PROGRESS.md` |
| **数据重构权威进度** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\TASK.md` §8 |
| **【49-bug 实验 · 接续指引（最重要）】** | `...MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md`（代码地图+运行顺序+交接） |
| **【分析进度 · 交接】** | `...MCP-Fault-Benchmark\docs\ANALYSIS_PROGRESS.md`（已完成勿重跑） |
| **49-bug 论文草稿（表格+正文）** | `...MCP-Fault-Benchmark\docs\REPRO_49_ANALYSIS_DRAFT.md`（tab:repro49 + Results prose） |
| **数据集漏斗表 + prose** | `...MCP-Fault-Benchmark\docs\FUNNEL_TABLE.md` |
| **49 条难定位原因表** | `...MCP-Fault-Benchmark\docs\HARD_TO_LOCALIZE_49.md` |
| **293 未复现·故障性质分类** | `...MCP-Fault-Benchmark\docs\FAULT_NATURE_293.md` |
| **按章节拆分审阅稿（zip）** | `C:\Users\kehuichen2\Desktop\IST\main_review.zip` |
| **按章节拆分审阅稿（目录）** | `C:\Users\kehuichen2\Desktop\IST\main_review\`（01_intro … 08_ack） |
| 作者原始zip | `C:\Users\kehuichen2\Desktop\IST\IST__Right.zip`（旧，未改） |
| QRS 会议版 | `C:\Users\kehuichen2\Desktop\IST\QRS_R181_CAMERA_READY.zip` |

> ⚠️ `MCP_IST_Project\paper\` 下也有 `main.tex`/`main_body.tex`（项目内"工作版"，非投稿包）。
> 投稿包以桌面 `IST_Right_updated.zip` 为准。两处可能不同步，注意核对。

---

## 2. 恢复步骤（闪退后让 AI 这样做）

> ## ⚠️⚠️【2026-10-11 最新修正 · 恢复时 FIRST 必读，之前漏读了！】
> **本文件 + `TASK.md` 只描述了"数据重构/复现"这条线的进度，但项目其实已经推进到了
> "**49-bug 实证分析**"这条独立主线，它的最详细、手把手的接续指引在
> `MCP-Fault-Benchmark\docs\` 目录下。重开后【除读本文件外】必须优先读这几个文档，
> 否则会像之前那样漏掉已完成/未完成的实验清单：**
>
> 1. **`MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md`** —— 49-bug 实验的【代码地图 + 运行顺序 + 交接】。
>    明确写了目标：*"FINISH every experiment on the 49 genuinely reproduced real bugs, then write the
>    49-bug narrative into the paper. The 293 not-reproduced bugs are DECIDED LAST."*
>    每节注明：代码做什么、数据源、怎么跑、输出什么。**重开先读它，照此接续。**
> 2. **`MCP-Fault-Benchmark\docs\ANALYSIS_PROGRESS.md`** —— 分析进度与交接。读它恢复分析状态；
>    明示**已完成的分析不要重跑**。它又指向 `EXPERIMENTS_49.md`（更细）。
> 3. **`MCP-Fault-Benchmark\docs\REPRO_49_ANALYSIS_DRAFT.md`** —— 49 条三通道分析的【论文 LaTeX 表格 + 正文】草稿，
>    可直接接入正文（含 `tab:repro49` + Results prose + 中文注释）。
> 4. **`MCP-Fault-Benchmark\docs\FUNNEL_TABLE.md`** —— 数据集漏斗（1343→439→398→剔除56→342→49/293）+ prose。
> 5. **`MCP-Fault-Benchmark\docs\HARD_TO_LOCALIZE_49.md`** —— 49 条"难定位原因"逐条表 + 分布（genericised 28/silent-ok 11/…）。
> 6. **`MCP-Fault-Benchmark\docs\FAULT_NATURE_293.md`** —— 293 条未复现 bug 的故障性质分类（描述型，非三通道）。
> 7. 其他 `docs/`（DATA_REBUILD_PROGRESS / REPRO_PROGRESS / numbers / taxonomy / real_*）视需要读。
>
> **关键现状（2026-10-11，以 docs/ 为准）：**
> - 数据集漏斗：**1343 → 439 → 398 → 剔除56(fixed-in-2.2.0) → 342 有效 → 49 复现 / 293 未复现**。
> - **49-bug 已完成**：①三通道分析（mismatch 76.9%、silent 22.4%、genericised 34.7%）；
>   ②硬定位原因分析；③**LLM 诊断基线已跑：整体 77.6%（38/49），但【非Server源仅 15.4%（2/13）】——这才是诚实硬核数字**；
>   ④漏斗表+prose；⑤主图 `fig_main_alluvial_with_ids`；⑥**Top-K 已跑（整体 Top-1 79.6%/Top-2 87.8%/Top-3 95.9%；非Server源 Top-1 23.1%/Top-2 53.8%/Top-3 84.6%）**；
>   ⑦**诊断线索干预 Phase B 已跑（基线 77.6%/15.4% → 诚实线索 79.6%/23.1% → 裸标签负对照 73.5%/0.0%）**。
> - **49-bug 实验：诊断线全部完成**（三通道 / 硬定位原因 / 诊断基线 / Top-K / 线索 Phase B）。**修复实验（Phase C）已决策延后**：
>   用户要求修复实验也针对 49 条真实 bug，但真实 issue 的"修复后正确性"难自动验证；已评估分三类（有明确判据 ~20 / 报错类 ~15 / 静默规格并发 ~14），
>   方案=跑"可自动验证子集"（~20-25 条）+ 如实标注排除。**当前先写诊断实验进论文，Phase C 之后再做**。
> - **当前下一步**：把已完成的 49-bug 诊断实验写进论文 `.tex`。
> - **⚠️ 论文有两套 tex，用户要求【两套都同步更新】到 49-bug 口径（49=唯一数据口径，合成集/28真实集/6合成硬bug 全废弃）**：
>   - ① 桌面 `main_review/` 拆分稿（01_intro..08_ack，RQ1-4 + 灯泡 Finding 框 + minipage 图）＝ **投稿主文件**（被 `paper/main_review.tex` 用 `\input{../main_review/01_..08_}` 引入）
>   - ② 项目 `paper/main_body.tex`（RQ1-3 整稿，非投稿）
>   - **✅ 已改到 49-bug**：投稿版 `main_review/05_results.tex`（RQ1/RQ2/RQ3/RQ4 全部）+ `main_review.tex` 的 abstract/highlights + `main.tex` 的 abstract/highlights；`main_body.tex` 的 RQ1、RQ2 的 pushed/silent/caller 三小节、RQ3 诊断部分。
>   - **✅ 已删 2 个旧子节**（投稿版 05_results）："External validation with real production-grade faults"（6合成硬bug）+"External validation over the real Streamable-HTTP transport"（28真实集/18issue），相关表图 label 已清理。
>   - **⏳ 待做**：① 删 `main_body.tex` 里对应的 2 个旧子节（RQ2 的 "Real production-style hidden faults" + "External validation"）；② 两套 intro/discussion/conclusion 旧数字；③ 两套 sec:sampling 350→342（91/118/85/48，复现49）；④ 重画图（fig_diag_clues/fig_topk 用49-bug；fig_layer/fig_causal/fig_silent/fig_mismatch/fig_repair 旧数据待重画或替换）。
> - **⚠️ main_body.tex 目前还有残留旧数字**（6/6×5、18/80、22.5×6、47/48、23/48、11/48、18 distinct），主要来自待删的 2 个旧子节，begin/end 仍 33/33 配平。
> - 关键产物：`data/full_pool/active_dataset_analysis.json`、`hard_to_localize_49.json`、`diag_dataset_49.json`、
>   `llm_answers_49.json`（**已跑**）、`llm_answers_49_clues.json` / `llm_answers_49_leaky.json`（**已跑**）、
>   `diag_clues_49.json`（**已建**）、`funnel_table.json`、`reproduced_49_channels.csv/xlsx`。
>   结果文档：`docs/TopK_49_RESULTS.md`、`docs/CLUES_49_RESULTS.md`、`docs/REPRO_49_ANALYSIS_DRAFT.md`、`docs/FUNNEL_TABLE.md`。
> - **诚实口径**：三通道/静默/错位只在 49 条上算（需报错证据）；342 只做描述统计；293 只做描述型性质分类。
> - **Taraghi taxonomy 不要用于分类**，只在 Related Work 解释为何不采用。

1. 读本 `RECOVERY_README.md`（快速了解全局）。
2. **读 `MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md` + `docs\ANALYSIS_PROGRESS.md`**（49-bug 实证主线的详细接续指引，最重要）。
3. 读 `TASK.md` §0-§3 + §9 + §12（数据重构/复现线的权威数字 + 最新进度）。
4. 读 `QHISTORY.md` 最后几条（最近做了什么/未做什么）。
5. 需要改正文就解压 `IST_Right_updated.zip` 到工作目录再编辑；改完重新打包。

> ## 🚀【开新端口 · 立刻直接做这一步】（无需跳转）
> **当前主任务 = 第③步：复现 398 条。** ⚠️ **详细作战图/逐条方案见
> `MCP-Fault-Benchmark\docs\REPRO_PROGRESS.md`，重开后先读它！**
> 第①②步已完成（补 body + 分类 398 原始层：Server 130/Client 128/Transport 90/Host 50）。
> **复现框架已建好**（可断点续跑）：`runner/repro_cases.py` + `repro_framework.py` + `data/repro_progress.json`。
> **已复现 49 条**（18 verified #3549–#3646 + 31 batch1/2/3/4/5/6/7/8/14：#234/#348/#2114/#2422/#3266/#1702/#3342/#3385/#3656/#3099/#3067/#3341/#2770/#2057/#2618/#2539/#110/#698/#743/#1060/#1361/#2153/#3351/#244/#1974/#891/#2386/#2431/#1579/#2741/#417）。
> ✅ 第1类10条已攻克、第2批(序列化/校验)12条已跑、第3批(协议/raw_post)5条已跑。
> ✅ **batch '10'（15条，2026-10-10）已跑，0 新复现，全部 limited**（见 REPRO_PROGRESS §四·J）。
> ✅ **框架已扩展支持 SSE/断开/并发（2026-10-10）**：`repro_framework.py` 加 `transport='sse'`、`disconnect`/`concurrency`/`reconnect`、
> `exc()` 递归展开 ExceptionGroup；11 条 SSE 场景 bug（batch '11'）改用 SSE 真跑，**0 新复现**（#491 证实为 fixed-in-current）。
> ✅ **batch '13'（49 条，2026-10-10）已跑，0 新复现，全部 limited**（见 REPRO_PROGRESS §四·L）。
> ✅ **batch '14'（139 条，2026-10-10）已跑**（用户要求"除需登录/认证外全部真跑"）：补齐**全部非认证未追踪 bug**
> （`runner/repro_cases_b14.py`，接 `BATCHES['14']`），**1 新复现（#417）+ 138 limited**（见 REPRO_PROGRESS §四·M）。
> **至此全部非认证 bug 已真跑**：342 有效 = **49 已复现 + 301 已如实记录 limited + 48 认证类跳过**（认证类需 OAuth/凭证，用户确认跳过）。
> **累计已复现 48 → 49，数据集仍 342**（无新剔除）。每条均按真实缺陷性质写诚实原因，未造假。
> **第①步(补body)完成**：398 条 body 已齐（396 完整 + 2 真·空 #469/#753）。
> **第②步完成**：专家逐条审阅 398 原始层（不加 Taraghi 类别列）。**报告层/暴露通道列留待复现后填。**
> **已完成**：①补拉全池 1,343 纯 issue；②初筛 439 关键词-BUG；③人工复核 → **398 真 bug**；
> ④**论文"数据集建立过程"节（sec:sampling）已重写定稿**；⑤补 body（第①步）；⑥分类 398 原始层（第②步）；
> ⑦复现框架 + 第一批(5 done)。
> **下一步**：**进入第④步**——更新论文 sec:sampling（350→342 新分布，复现 48→49）+ 重算三通道/静默/错位
> + 重画图 + LLM 诊断重跑（用户跑 DeepSeek-V4）。**详细行动计划见 `TASK.md` §12 末尾 + §9.4**，重开先读它。
> → ⑤更新论文和结论（§9.4 按行号）→ ⑥打包 zip（§9.5）→ ⑦发布 GitHub。**全文其余部分仍是旧口径，勿当成最新。**
> ⚠️ 全池仅新拉 200 条有完整 body，旧 1143 条只有 body_head（319 条前 300 字）；分类/复现前需先补 body（现已补完）。
>
> **最新数据在哪里看**（`MCP-Fault-Benchmark\data\full_pool\`）：
> - 全池初筛：`full_pool_screened.json`（1,343 条，含 label）
> - 复核 verdict：`bug_review_verdicts.json`（439 条 BUG/NOT_BUG + 原因）
> - 复核 Excel：`bug_review_full.xlsx`
> - **确认真 bug（398）**：`confirmed_bugs.json` + **`confirmed_bugs.xlsx`**
> - **原始层分类（第②步产物）**：`data/full_pool/origin_labels.json` + **`origin_labels.xlsx`**（398 条，
>   Server 130/Client 128/Transport 90/Host 50）；源脚本 `analysis/author_origin_labels.py` + `apply_origin_labels.py`
> - **【主产出】全部 bug 分析表**：`data/full_pool/all_bugs_analysis.xlsx`（**342 行，20 列**，**已复现 49 条标绿**，
>   每次复现后跑 `analysis/make_all_bugs_excel.py` 回填）；详细见 `docs/REPRO_PROGRESS.md` §七
> - **【可复现性分层表】**：`data/full_pool/repro_tiers.xlsx`（**342 条分层**：T1 49=真实已复现 / T2 174 / T3 47 / T4 72 / T5 0；
>   **T1-fixed 56 已从数据集剔除**，见 §数据口径变更）；
>   **自动读 repro_progress.json，重跑 `assess_reproducibility.py` 即同步，勿重分析**）；
>   详见 `docs/REPRO_PROGRESS.md` §二·D。**⚠️ 口径：已复现=49**；有效数据集=342（fixed-in-current 56 条已剔除）。
> - **复现进度/作战图**：`docs/REPRO_PROGRESS.md` + `data/repro_progress.json` + `runner/repro_framework.py`
> **最新论文段落（数据集建立过程，已定稿）**：`paper\main_body.tex`（sec:sampling，约 L600）
> + `main_review\04_setup.tex`（同名节）。**最新脚本**：`MCP-Fault-Benchmark\analysis\`
> `pull_remaining_issues.py` / `screen_issues.py` / `review_bugs.py` / `make_review_excel.py` /
> **`make_confirmed_excel.py`**（生成 398 真 bug 的 `confirmed_bugs.xlsx`，并给 confirmed_bugs.json 补字段）。

---

## 3. 权威数字（写论文/核对用，来源 `MCP-Fault-Benchmark\docs\numbers.md`）

> ## 🆕【2026-10-11 两层数据集分析完成 · 342 描述 + 49 实证】
> 用户确认：**数据集写成两层**——342 是「分析/普查数据集」，49 是「实证复现子集」（呈金字塔 1343→439→398→342→49）。
> 重跑分析已完成（`analysis/analyze_active_dataset.py` → `data/full_pool/active_dataset_analysis.json`）：
> - **TIER A（342 描述统计，无需复现）**：漏斗 1343→439→398→342（剔 56 已修复）；层分布 Server 91/Client 118/Transport 85/Host 48；open/closed 93/249；复现 49/受限 245/认证跳过 48；受限原因分类（env/transport 94、not-exercised 62、auth 48、观察型 29、clean-success 25、example 10、observation-only 9、spec-gap 6 等）。
> - **TIER B（49 实证三通道，基于运行时证据）**：推到Server 7 / 静默 11 / 调用方裸抛 3 / 单层掩蔽 17 / 单层正确 8 / 注册期错误 3。
>   **非Server错位 10/13 = 76.9%**（7 推到Server + 3 调用方）；**静默 11/49 = 22.4%**；**通用掩蔽 17/49 = 34.7%**（最强机制）。
> - 新图：`figs/fig_funnel.png` / `fig_exposure_channels.png` / `fig_repro_reasons.png`；`all_bugs_analysis.xlsx` 列19 已回填 49 条三通道分类。
> - ⚠️ **三通道只能算 49（要报错证据），342 只能算描述统计**。LLM 诊断/修复需用户本地跑 DeepSeek-V4（旧 45%/52.5%/69.6% 仍基于旧 80 合成集）。

**三通道暴露模型（非Server 48 运行）——【当前主结论】**
- 推到 Server 层：**23**（Host 15 + Client 8）
- 调用方裸抛异常：**11**（Transport 11）
- 静默：**13**（Host 1 + Client 8 + Transport 4）
- 无证据：**1**
- **广义错位（报告≠起源，排除静默）= 34/48 = 70.8%**（23 + 11）
- **47/48 非Server运行未被正确定位到真实起源层**
- Server 源 32：单层正确定位 4 / 静默 5 / 重报 23
- **静默总计（含Server）= 18/80 = 22.5%**（c1,c4,s7,t3 结构静默；h4,s6 输入依赖）

**真 LLM 诊断基线（DeepSeek，temp=0，去除层名泄漏）**
- 诚实版：**45%**（Host 0 / Client 0 / Server 100 / Transport 25）
- Top-K：**Top-1 45% → Top-2 65% → Top-3 85%**（Transport 恒定 25%）
- 泄漏负对照：**55%**（证明 45% 非捷径）
- 干预 `actual_fault_source`：理想 **100% (+55.0pp)** / 现实(90%信任) **93.8% (+48.8pp)**
  ⚠️ 这是 **upper-bound 分析**，非因果结论；字段生成本身未评估（正文已加 caveat 段）。

**真实生产级硬bug子集（6例）**
- 6/6 = **100% 静默**（并发竞态/无超时/重复注册/状态泄漏/流中断/并发修改），远超合成集 22.5%。

> ⚠️ **废弃口径（勿再用）**：旧"非Server故障 47/48 = 97.9% 被推到Server"已废弃，因把 Transport 的
> 调用方裸抛异常误算进"推到Server"，且"静默"应独立成通道。全文已改为 70.8%。

---

## 4. 当前进度（截至 2026-09-30）

### 正文已完成
- 全部三通道改写：RQ1（无人被正确定位）、RQ2（三通道70.8%）、RQ3（静默22.5%）、RQ3b（真实硬bug 100%）、RQ4（LLM 45% + Top-K + 泄漏对照 + 干预 caveat）。
- 摘要/高亮/贡献/结论：全部同步 70.8% 与 45%。
- 术语：Resource → Transport 统一；novelty 软化；删企业名只报行业；Grant 号统一 4 个 CityU 号。
- 图：`fig_causal_graph`（三通道，取代旧 fig_mismatch）、`fig_topk`、`fig_advanced_silent`、`fig_diag_accuracy`(45%) 等，均用权威数据重建。
- 旧 `fig_mismatch.png`（97.9%）已移出。

### 格式/审阅稿进度
- `main_review\` 已按章节拆 8 个文件；05_results 已转成 minipage+captionof / tabularx / 灯泡框格式；新增段落标红 + 中文注释。
- `main.tex` 已补宏包：booktabs, tabularx, array, ragged2e, caption, fontawesome5。

### 4.1 最新进展（2026-09-30 夜）—— Taraghi 定位 + 真实传输层（新方向，已验证）
- **引用了 Taraghi（arXiv:2603.05637）**：正文曾只提其名无引用无 bib（悬空引用硬伤），现已补 bib 条目 `taraghi2026real`，并重写 02_related/main_body 定位段（论证为何需四层起源分类；Taraghi 停在推荐 observability，我们用基准测量）。Taraghi= MCP 首个大规模故障分类（5 大类，Server/Tool 31.74% 最高；最频繁 Tool Response Handling 66.67%、最严重 Host Connection Mismatch 0.42、最耗时 Tool Authentication 0.41）。
- **真实传输层已打通**（用户选路径甲=真实传输+故障源自真实 issue）：
  - `runner/run_real_http.py`：用 `MCPServer.run_streamable_http_async(host=,port=)`(内置 uvicorn) 起 server，`Client(url,mode=..)` 连接，捕获真实返回 → 落盘 `data/real_raw/`+`data/real_index.json`。
  - **（2026-10-08）真实集已扩到 28 运行 / 18 去重真实 issue**：新增 `runner/run_real_http2.py`（8 个独立 issue：#3549/#3637/#3643/#3556/#3640/#3557/#3644/#3646，bespoke 捕获）。`repro_kind`：genuine 14 / variant 14。
  - 28 条分类（`data/real_summary.json`，v28）：**pushed-server 7 / silent 10 / caller-exception 5 / registration 1 / single-layer 5**；静默 **35.7%**；非Server 错位 **11/13=84.6%**；**13/13 非Server未正确定位**。
  - `docs/real_issue_mining.md`（真实 issue 记录）、`docs/real_highfreq_design.md`（设计草案）、`docs/real_dataset_rationale.md`（选型理由+证据统计）。
- 入口避坑：不要 `uvicorn.run(MCPServer)`(报 not callable)；`run_streamable_http_async` 在 mcp2.2.0 **必须关键字参数**(host=,port=)；`Client.list_tools()` 返回 `ListToolsResult`。
- **分析管线已打通**：`analysis/parse_real_runs.py`（读 real_raw → 分类 + repro_kind → `data/real_summary.json`）、`analysis/fig_real_transport.py`（28 条版+真实性/静默率）、`analysis/fig_real_taraghi.py`、`analysis/make_real_excel.py`（3 张 Excel 到 `data/excel/`）。
- ✅ Excel 3 张已生成（`data/excel/`：Excel1 abcd↔real / Excel2 real 28 条 / Excel3 合并=48 条），已注"Taraghi 人工归类"。
- ✅ tex 已接入（双语注释+标红）：桌面 `main_review/05_results.tex` + 项目 `paper/main_body.tex`（`subsubsection{External validation over the real Streamable-HTTP transport}` + 表`tab:real_issues` + 图`fig:realtransport`/`fig:realtaraghi`）。
- ⚠️ 诚实边界：用户要"凑满 20 独立真实 issue"，但本机 mcp 2.2.0 能干净复现的独立真实 issue 只有 **18** 个；剩余候选（#3588/#3596/#3551/#3595/#3616/#3586/#3592/#3594/#3562/#3563/#3656/#3649/#3639/#3546/#3621/#3651/#3641/#3589/#3565）受 auth/security/stdio/版本限制无法复现，已如实标注 repro-limited，未造假。
- ✅ **阶段A.5 已完成（2026-10-08）**：新增独立子节 `Data Collection and Sampling Rationale`（`sec:sampling`），
  用数据驱动证据（issue 池 33 vs 复现18、覆盖率6/6、56%落Taraghi最频繁/最严重/最耗时）回应审稿人"为什么选这些数据"。
  已双语注释+标红接入 `paper/main_body.tex` 与 `main_review/04_setup.tex`，图 `fig_sample_frequency.png` 已复制到 `paper/figs/`。
  Taraghi 桶=作者人工归类（非原始计数），已注明诚实边界。
- ✅ **阶段B 已完成（2026-10-08 续6）—— 作弊式干预升级为"可运行诊断线索工具"**：
  新建 `metrics/diagnostic_clues.py`（读 SDK 文本→判定暴露通道→给方向性提示，**绝不点名根因层**，
  sanity check 防泄露）+ `metrics/analyze_clues.py`；`predict_llm.py` 加 `--clues`/`--clues-leaky` 模式。
  **真实 LLM 结果（80 次，同会话）**：基线 45.0% → +诚实线索 **52.5%(+7.5pp)**，Host/Client 0%→19%，
  Top-K 45/65/85→52/74/94；**裸通道标签负对照 41.2%（不升反降）**→提升来自指引内容而非泄露标签，
  坐实诚实线索未泄露答案（替代旧 100%/93.8% 上界）。产物：`data/diagnostic_clues.json`/
  `llm_answers_clues.json`/`llm_answers_clues_leaky.json`/`diag_clues_results.txt`/`diag_clues_metrics.json`/
  `figs/fig_diag_clues.png`。tex 已改（`main_body.tex`/`main.tex`/`main_review.tex`/桌面`main_review/01..07`/
  `paper_chinese.md`/`docs/numbers.md`），双语注释+红标，fig:diag 换 fig_diag_clues。
- ✅ **阶段C 已完成（2026-10-08 续7）—— 修复实验**：`metrics/repair_harness.py` + `analyze_repair.py`。
  对象集=23 个可自动判定用例（合成 17 剔除 c4/t3/s7 + advanced 6；真实 Streamable-HTTP 16 未纳入）。
  真实 LLM：合成 64.7%、advanced 83.3%、合计 **69.6%**；两档（无线索 vs +线索）完全一致。
  **关键诚实结论（用户确认写进论文）**：线索不改变修复成功率（因给了完整源码 LLM 能直接读源码定位），
  反证瓶颈是**定位**（+7.5pp）而非**修复**。产物：`data/repair_results*.json`(4个)、`repair_summary.txt`、
  `figs/fig_repair.png`。tex 已更新（main_body/main/main_review/桌面 main_review 01,05,07/paper_chinese.md/docs/numbers.md）。
- ✅ **阶段D 已完成（2026-10-08 续8）**：已打包当前工作版 `paper/` 为
  `C:\Users\kehuichen2\Desktop\IST\IST_Right_updated_v3.zip`（含阶段A.5 选型子节 + 阶段B 线索工具 +
  阶段C 修复实验；覆盖了旧的 v3 快照）。校验 label/ref/cite 全配平。
- ✅ **数据重构：数据集建立过程节已写（2026-10-08 续13）**：`sec:sampling` 已重写为
  "Dataset Construction and Sampling Rationale"（main_body + main_review/04_setup 双份），讲清
  全量普查 1,343→439→**398 真 bug** 的 dataset size / collection criteria / 代表性保证 / 单库 vs
  Taraghi 权衡。**用户确认 398 = 新建数据集，旧的 MCP-Fault-20(80 runs)+18 复现真实 issue 不要了**；
  全文其余旧口径位置暂不动，等实验在 398 上重跑后统一改（**清单见 TASK.md §9**）。
- 🆕 待办：数据集匿名 repo/DOI（唯一硬阻塞，正文红 TODO）；本机无 LaTeX tex 未编译；**全文仍用旧
  口径(MCP-Fault-20/80/18)，需按 TASK.md §9.4 重写**。

---

## 5. 未完成 / 待办（按重要性）

1. **数据集匿名仓库链接** —— 正文有红 TODO 未填（用户需提供匿名 repo/DOI）。
   ⚠️ `cas-refs.bib` 里的 figshare(`Anonymity2026`)只是**访谈提纲**，不是 MCP-Fault-20 数据集。
2. ✅ ~~`main_review\03_method.tex` methodology 图~~ 已转 minipage+\captionof（并标红 voluntary/kappa/saturation 段）。
3. ✅ ~~`main_review\04_setup.tex` tab:cases 表~~ 已转 tabularx；保留"Scope(cross/single)"列（唯一
   per-case 权威维度），Note 已说明运行级三通道暴露(pushed/silent/caller)在 RQ2 小节量化分析。
   ⚠️ 不再用 per-case 伪造"Exposure channel"值（因 32 个 Server 运行只有 4 个 single-layer，无法逐 case 溯源）。
4. ✅ ~~06_discussion / 07_conclusion~~ 已核对：讨论无残留旧数字；结论按三通道(70.8%/45%)更新并标红。
5. ✅ ~~main_review 未接入 main~~ 新增 `paper\main_review.tex`（review build 主文件），通过
   `\input{../main_review/01_..08_}` 正式接入这 8 个拆分文件（替换整体 main_body.tex）。
   `paper\main.tex`（原整稿）保留不动，作为对照。宏包已补齐（booktabs/tabularx/array/ragged2e/caption/fontawesome5/makecell/url/xcolor）。
6. **本机无 LaTeX**，未编译验证；minipage+captionof / tabularx 宏包已加（本机无法编译）。
7. **访谈饱和度/kappa 等细节**：用户名言无 IRB，正文用"自愿参与+匿名化"诚实表述（无审批号）。
8. ✅ 真实传输层：已扩到 **28 个真实用例 / 18 去重 issue**（绑真实 issue，新增 #3549/#3637/#3643/#3556/#3640/#3557/#3644/#3646）、`analysis/parse_real_runs.py` 已写（含 repro_kind）、numbers.md 已同步。
   ✅ 已产出：3 张 Excel（`data/excel/`，Excel2=28 条 / Excel3=48 条）、`docs/real_dataset_rationale.md`、图 `fig_real_transport`(28条)+`fig_real_taraghi`、tex 接入
   （桌面 `main_review/05_results.tex` + 项目 `paper/main_body.tex`，双语注释+标红+表+图）。
   ⏳ 仍欠：① 数据集匿名 repo/DOI（唯一硬阻塞，正文红 TODO）；② "凑满 20 独立真实 issue" 未达成（本机只能复现 18 个），未造假。
9. ✅ ~~阶段B（作弊式干预→可运行诊断线索工具）~~ 已完成（2026-10-08 续6，见 §4.1）。基线45%→有线索52.5%(+7.5pp)，负对照41.2%。
   ✅ ~~阶段C（修复实验）~~ 已完成（2026-10-08 续7，见 §4.1）。合成64.7%、advanced83.3%、合计69.6%，两档一致（线索不改变修复，定位才是瓶颈）。
   ✅ ~~阶段D（重打包 v3）~~ 已完成（2026-10-08 续8）。`IST_Right_updated_v3.zip` 含阶段A.5/B/C 全部改动。
10. 可选后续：跨 SDK 扩展、学会 LLM 诊断模型。
10. 可选后续：跨 SDK 扩展、学会 LLM 诊断模型。

---

## 6. 关键脚本（在 `MCP-Fault-Benchmark\`）

- `runner/run_all.py` → 跑 20×4=80 用例到 `data/raw/`
- `analysis/exposure_model.py` → 三通道暴露模型权威数字
- `analysis/make_figs.py` → fig_layer_distribution / fig_mismatch(三通道版) / fig_silent_failure
- `analysis/causal_graph.py` → fig_causal_graph.png
- `metrics/predict_llm.py` → 真 LLM 诊断（DeepSeek，含 --topk / --keep-leak）→ `llm_answers.json`
- `metrics/diagnose.py` → 基线+Top-K+干预 → fig_diag_accuracy / fig_topk
- `analysis/analyze_advanced.py` → fig_advanced_silent.png
- **运行只用 `analysis/`、`metrics/` 里的；`scripts/`（根目录）是早期产物，老旧勿依赖。**

### 6.1 第③步复现 398 条（本次主任务）关键脚本
- `runner/repro_framework.py` → 复现引擎（起 MCPServer+uvicorn → Client 连接 → 触发 → 捕获真实返回/异常）。`--batch N` / `--only a,b` / `--all`（断点续跑）。
- `runner/repro_cases.py` → 每条 bug 的 `Case`（builder + method + target + args + origin）。**本次新增 batch '4'–'9'（78 case）**。
- `data/repro_progress.json` → 逐条 {status: done/limited, reason, message, file}，断点续跑依据。
- `analysis/make_all_bugs_excel.py` → `data/full_pool/all_bugs_analysis.xlsx`（**主产出，350 行 18 列，已复现 48 条标绿**；
  读 fixed_removed.json 过滤，数据集=350）。
- `analysis/assess_reproducibility.py` → `data/full_pool/repro_tiers.xlsx`（**T1 48 / T2 130 / T3 130 / T4 32 / T5 10**；
  T1-fixed 48 已剔除；读 fixed_removed.json 过滤）。
- `analysis/dataset_stats.py` → `data/full_pool/dataset_stats.json`（**350 数据集权威统计**：层分布 Server 93/Client 121/Transport 87/Host 49、
  open/closed 94/256。论文 sec:sampling 数字用它复现，勿手算）。
- **关键发现/已复现 bug 清单**：`TASK.md` §10（三通道证据 + 每批发现 + 可复用代码清单）——第④步分析直接引用，勿再翻散落记录。

---

## 7. 环境备忘

- Python 3.13.9；已装官方 MCP SDK v2.2.0（`from mcp.server.mcpserver import MCPServer` 即官方接口）。
- 无 LaTeX 编译器 → 无法本地编译，需 Overleaf（pdfLaTeX + BibTeX）。
- LLM 诊断 key 存 `MCP-Fault-Benchmark\.env`（已 gitignore，勿提交）；模型 `CS/DeepSeek-V4-Flash-FP8`。