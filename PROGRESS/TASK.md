# MCP故障定位研究 —— 项目任务与进度记录（IST期刊扩展）

> ## ⚠️⚠️【2026-10-11 恢复 FIRST 必读 · 之前漏读了，重要！】
> **本文件（TASK.md）只记录了"数据重构/复现"这条线的进度。项目其实已推进到"**49-bug 实证分析**"主线，
> 它的最详细、手把手的接续指引在 `MCP-Fault-Benchmark\docs\` 目录下。重开后【除读本文件外】必须优先读：**
> - **`MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md`** —— 49-bug 实验代码地图 + 运行顺序 + 交接（**最重要，先读**）。
> - **`MCP-Fault-Benchmark\docs\ANALYSIS_PROGRESS.md`** —— 分析进度交接，已完成勿重跑。
> - **`MCP-Fault-Benchmark\docs\REPRO_49_ANALYSIS_DRAFT.md`** —— 49 条三通道论文表格 + 正文草稿（可直接接入 .tex）。
> - **`MCP-Fault-Benchmark\docs\FUNNEL_TABLE.md`** / **`HARD_TO_LOCALIZE_49.md`** / **`FAULT_NATURE_293.md`**。
> - 关键现状：漏斗 **1343→439→398→剔除56→342→49复现/293未复现**；LLM 诊断基线**整体 77.6% / 非Server源 15.4%**；
>   49-bug 未完成：**Top-K、诊断线索干预(--clues)、修复实验(Phase C)**；再把 49-bug 叙事写进论文 .tex。
> - 完整恢复指引见 `RECOVERY_README.md` §0/§1/§2 顶部（已更新）。

> ## ⚠️【双语注释约定 · 每次必做】（2026-09-30 新增）
> **每次往任何 tex 文件新增/修改内容，必须加【中英双语】注释**：
> 中文一条 + 英文一条。例如：
> `% ★【中文说明】这是新增段的说明…`
> `% ★[English] This explains the newly added paragraph…`
> 已有的旧注释（目前多为纯中文）**保持不动**，只对新加内容用双语。

> **本文件用途**：数据重构/复现线的"进度细节 + 待办清单"（§8/§9/§10/§12）。⚠️ **不是"当前状态"的唯一权威**。
> **"现在在做什么/做到哪/下一步"的唯一权威 = `RECOVERY_README.md`（§0 一句话现状 + §2 顶部提示）**。
> **49-bug 实证线的详细接续指引 = `MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md` + `docs\ANALYSIS_PROGRESS.md`**。
> 重开后按 `RECOVERY_README.md` §2 顶部"文件职责"规则读，勿重复询问。

> ## ⚠️【文件职责 + 自动更新规则 · 每次必做】（2026-10-11 制定，见 `RECOVERY_README.md` 顶部）
> **不要散落、不要新开 .md 记录文件。** 更新固定写到：
> - `RECOVERY_README.md`（§0 现状 + §2 顶部）← **现在在做什么的唯一权威**
> - `QHISTORY.md`（末尾追加，只追加不修改）← 时间线
> - `MCP-Fault-Benchmark\docs\numbers.md` ← 权威数字
> - `MCP-Fault-Benchmark\docs\EXPERIMENTS_49.md` ← 49-bug 实验接续指引
> - `MCP-Fault-Benchmark\docs\ANALYSIS_PROGRESS.md` ← 分析进度（已完成勿重跑）
> 冲突时以 `RECOVERY_README.md` §0 + `docs\numbers.md` 为准。

> ## ⚠️【全部 bug 分析表 · 每次复现必回填】
> **`MCP-Fault-Benchmark\data\full_pool\all_bugs_analysis.xlsx` 是全部有效 bug 的最终分析情况表（主产出）。**
> ⚠️【2026-10-10 数据集口径：398 确认 → 剔除已修复 → 当前 **342 有效**】。剔除清单 `fixed_removed.json`（现 56 条，含 batch12 8条）。
> 表里 342 行（48 绿=已复现）。论文 sec:sampling 旧写 350，**第④步改写时须同步为 342**。
> **每复现/分析完一条 bug，必须跑 `python analysis/make_all_bugs_excel.py` 重新生成该表**，
> 把该条的 复现状态/故障描述/触发代码片段/异常类型/完整报错文本/故障范围标记（及后来的报告层/暴露通道）回填。
> 生成脚本会自动读 confirmed_bugs + origin_labels + _verified_repro_info + repro_progress + **repro_cases.py** 合并。
> 此约定长期有效，重开后照做（详细见 `MCP-Fault-Benchmark\docs\REPRO_PROGRESS.md` §七）。

> ## ⚠️【可溯源规则 · 每次复现必须能溯源】
> **每次复现必须让下一个人能知道：做了什么、在哪看代码、数据在哪、怎么复现。**
> ① 每条已复现 bug 必须在 `runner/repro_cases.py` 有 Case 定义（builder + method/target/args），能直接跑；
> ② `data/real_raw/real_{n}.txt` 有原始捕获文本；③ `all_bugs_analysis.xlsx` 该行 复现状态=已复现、
> 脚本文件名=repro_cases.py::<builder>、触发代码片段=method(target,args)；④ `docs/REPRO_PROGRESS.md`
> 记录该条归属。**新增 builder 一律写进 `repro_cases.py`**，勿散落临时脚本（18 条 verified 已迁移进来，
> 其【溯源索引】见 `repro_cases.py` VERIFIED 段上方注释 —— 每条 verified 都标了 文件::函数 + 证据文件）。
> 详细见 `MCP-Fault-Benchmark\docs\REPRO_PROGRESS.md` §七。

> ## ⚠️【每批复现完成即整合 · 防代码/数据散落】（2026-10-10 新增，长期有效）
> **每完成一批（batch）复现，必须立刻把该批的【代码 + Excel + 进度】整合到一起，绝不允许散落、不许下次找不到前面的代码。**
> 具体做到（按序，跑完即做，勿拖到下次）：
> 1. **代码**：该批所有 builder/case 必须**写进 `runner/repro_cases.py`**（不是临时脚本），并在 BATCHES 里注册 batch 号。
>    每条 builder 上方用注释写清 `# <issue> <origin> <缺陷描述>`。**禁止用一次性 `_tmp_*.py` 跑复现后不迁移。**
> 2. **进度**：跑完 `python runner/repro_framework.py --batch N` 后，结果已自动写入 `data/repro_progress.json`
>    （含 done/limited + reason + message + file）。**核对每条 status 与真实结果一致，不许偷懒不核对。**
> 3. **Excel**：跑 `python analysis/make_all_bugs_excel.py` 回填 `all_bugs_analysis.xlsx`（主产出，必须更新）；
>    跑 `python analysis/assess_reproducibility.py` 同步 `repro_tiers.xlsx`；
>    跑 `python analysis/dataset_stats.py` 同步 `dataset_stats.json`（350 权威统计）。
> 4. **文档**：把该批结果写进 `docs/REPRO_PROGRESS.md`（新增 §四·X batch 小节：issue/缺陷/结果/触发四列表），
>    并把累计"已复现 N 条"更新到 `TASK.md` §10 + `RECOVERY_README.md`。
> 5. **自检**：确认 该批每条在 repro_cases.py 有 case、在 repro_progress.json 有记录、在 all_bugs_analysis.xlsx 有行、
>    在 REPRO_PROGRESS.md 有表格 —— **四处一致才算完成**。漏任何一处 = 下次必然找不到。

> ## ⚠️【Token 上限约定 · 防闪退】
> 用户在 2026-09-30 观察到每次到 **260,000 token** 就闪退。当累计 token 临近 **250,000** 时，
> **立即停止继续工作**，先把当前改动完整保存进记录文件（QHISTORY + TASK + RECOVERY），用简短
> 消息确认已保存、说明"做到哪/剩什么"后再结束。切勿拖到 260,000 闪退丢进度。

---

## 0. 一句话背景

把已发表在 **QRS会议** 的 MCP 论文，扩展重写成 **IST期刊（Elsevier, Information and Software Technology）** 版本。
核心主题聚焦 **"为什么 MCP 的 bug 这么难定位（fault localization / fault diagnosis）"**。
要求 **新增内容 ≥ 50-60%**，且**不能**是"把 QRS 复制过来 + 追加内容"——这是导师/学姐明确批评过的旧写法 `IST 6.pdf` 的问题。

---

## 1. 素材清单（路径与状态）

| 素材 | 路径 | 说明 | 状态 |
|---|---|---|---|
| QRS 全文 tex | `C:\Users\KEHUIC~1\AppData\Local\Temp\opencode\qrs\` | 1_Introduction ... 7_ACK、main.tex、ref.bib（LNCS 格式，4 RQ，8 Finding，纯访谈） | ✅已读 |
| IST 模板 | `C:\Users\KEHUIC~1\AppData\Local\Temp\opencode\ist_tpl\paper_content.tex` | Elsevier cas-dc 双栏模板（Context/Objective/Methods/Results/Conclusion 结构化摘要） | ✅已读 |
| 学姐否决的旧版 | `C:\Users\KEHUIC~1\AppData\Local\Temp\opencode\ist6.txt` | 导自 `IST 6.pdf`。问题：访谈=QRS 原样，实验后加、两张皮、7 RQ 太散 | ✅已读 |
| **论文核心数据 xlsx** | `C:\Users\kehuichen2\Desktop\IST\abcd 记录_3.xlsx` | 20 用例 × 4 变体 = 80 次运行，四层故障注入 | ✅已统计 |
| **fault 源码仓库** | `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-research\` | **用户提供的 GitHub 源码**（xxyyzz417/MCP-research），含 80 个 .py 用例、4 个 results.txt、核查修订版 xlsx | ✅已 clone 并解析 |
| 解析出的数据集 | `...MCP_IST_Project\dataset_runs.json` | 从 4 个 results.txt 解析的 80 条运行记录（含报错原文、层、范围） | ✅已生成 |

> 注意：`IST 6.pdf` 本模型不能直接读 PDF，已用 python 转成 `ist6.txt` 阅读。
> **两版 xlsx**：桌面版 `abcd 记录_3.xlsx`（sheet a 有 1000 行残留）与仓库版 `abcd 记录_3_核查修订版.xlsx`（每 sheet 21 行，更干净，Taraghi 标注为 `Server-Host` 等）。内容基本一致，**以仓库"核查修订版"为权威**，但统计结果两版几乎相同。

---

## 2. 已与用户确认的关键决定

1. **核心方向** = MCP **故障定位根因实证研究**（用户选定了"故障定位根因研究（推荐）"）。
2. 访谈部分 → 压缩为"需求侧证据/引子"；xlsx 实验 → 提升为**主贡献**；二者围绕一条因果链深度耦合。
3. 用户希望 AI 作为 CS 专家给出"还需要加哪些内容让文章更饱满"，并**希望 AI 帮他把这些实验都做了**。
4. 用户明确要求：把所有问答记录/任务进度持久化保存，闪退后可仅凭文件夹恢复，无需重复说明。

---

## 3. 权威量化结论（务必用于论文 —— 最强论据）

来源：逐 variant × case 解析 `abcd 记录_3_核查修订版.xlsx` + 4 个 `*results.txt`（脚本 `scripts/05_parse_runs.py` → `dataset_runs.json`）。

**总量**：20 唯一根因用例 × 4 参数变体 = **80 次运行**。

**按层分布**：Host 16，Client 16，Server 32，Transport 16。

**按范围（scope）**：
- 跨 Host-Server 跨组件故障：**47/80 (58.75%)**
- 单层故障：33/80 (41.25%)

**核心证据——错位（manifestation-root-cause mismatch）——【2026-09-28 观察驱动重建，三通道模型】**
> ⚠️ **重要修正**：此前"错位 47/48=97.9%、100%"是**基于 xlsx 硬编码 cross 标签自证**，不是观察结果。
> 逐条读 80 条 raw 报文后，真实情况更复杂也更有层次，应采用**三通道暴露模型**（见 docs/numbers.md、
> `analysis/exposure_model.py`、`data/exposure_model.json`）：
> - **广义错位（报告层≠起源层）= 34/48 = 70.8%**，拆成两条独立通道：
>   - **① 推到 Server（23/48）**：Host(h1,h2,h3)+Client(c2,c3) 故障 → `Error executing tool X` + `is_error=True` 在 Server 调度层暴露。
>   - **② 调用方抛 Python 异常（11/48）**：Transport(t1,t2,t4) 故障 → `CancelledError` / `RuntimeError: Client must be used within an async context manager`，在调用方暴露，**不是** Server（旧稿把 Transport 算进"推到 Server"是错的）。
> - **③ 静默（13/48 非Server + 5 Server = 18/80 = 22.5%）**：`is_error=False`，逻辑错误被无声吞掉（c1,c4,t3 结构静默，h4,s6 输入依赖，s7 结构静默）。
> - 结论：MCP 故障通过**三种不同方式躲开定位**（推到错层 / 无声吞掉 / 调用方裸抛），三者都掩盖真实病灶。
>   **旧稿"非Server故障几乎全部错位到Server层"过度简化，已废弃。**

**Silent failure（is_error=False 但逻辑错误）** —— 判定依据 xlsx"异常类型"列（人工核实），比正则更可靠：
- **结构静默（4/4 变体全静默，4 用例）**：`c1_extra_param`、`c4_wrong_method`、`s7_duplicate_tool_registration`、`t3_invalid_message`
- **输入依赖静默（仅特定输入静默，2 用例）**：`h4_wrong_param_type`（字符串"5"被SDK自动转int→静默；None→显式）、`s6_pydantic_serialize_error`（返回对象被字符串化→静默；缺age→显式 TypeError）
- 其余 14 用例：4/4 全显式报错。
- **静默运行总次数 = 4×4 + 2×1 = 18/80 (22.5%)**，跨 **6 个根因用例**。
- **研究亮点**：区分 *结构性静默*（SDK 总吞掉该类错误）vs *输入依赖静默*（同根因不同输入，有时静默有时显式）。比旧版"13/80 波动"更有深度。
- ⚠️ **提示**：用 5 号脚本从 results.txt 正则判 silent 会失败（=0），因 results.txt 只有 meta 行，显式/静默判定需用 **xlsx 的"异常类型"列**。最终统计以"异常类型列判定"为准（即上述 18/80）。脚本 `scripts/01_analyze_cases.py` 的判定正确。

**与已有故障分类文献对齐**：xlsx 第 8 列 Taraghi 大类（`Server/Host Configuration`、`General Programming`、`Server/Tool Configuration`）→ 把 MCP 四层 taxonomy 与已有日志/故障分类文献（Taraghi 等）挂钩。旧版完全没用，**应新增此讨论**。

---

## 3.9 ★★ 最高优先执行指南：真实传输层"完整闭环"（按要求写好，读这节从头做到尾）

> 用户需求原话：**"把所有的实验跑完然后分析出来原因，画图加文字都更新上 tex 保存，这样一个闭环"**。
> 即：真实传输层（Streamable HTTP+uvicorn + 源自真实 issue 的故障）从挖掘 → 跑用例 → 分析 → 画图 → 更新 tex → 存档，一次闭环。以下为逐步执行步骤。

### 0) 目标与范围
- **新增一层证据（不是替换 in-memory 的 MCP-Fault-20）**：真实传输 + 真实 issue 故障，作为外部效度验证，
  回应论文 Threats 里"仅 in-memory、无法完全复现 stdio 部署"的弱点。
- 产出：`data/real_raw/` 原始报文 + `data/real_summary.json` 统计 + 新图 + tex 新增小节"Real-transport validation"。
- **来源原则**：每个用例必须标注真实 issue 出处（`modelcontextprotocol/python-sdk#NNN`），**禁止自造无出处用例**。

### 1) 挖真实 issue（作为用例来源证据库）
- 用 GitHub API 拉取并筛选：`https://api.github.com/repos/modelcontextprotocol/python-sdk/issues?state=all&per_page=100`。
- 目标：挑出能在本机(uvicorn+HTTP)复现、且对应 Taraghi 高频/严重类别的真实 bug，逐条记录
  仓库名 + issue 号 + 链接 + 类别 + 是否可复现，写入 `docs/real_issue_mining.md`。
- 已挖到：#3585(MIME,静默)、#3588(协议/连接错配,auto vs legacy)、#3596(stdio挂起,静默)、
  #3586(非ToolError后无应答,静默)、#3592(401/403/405重试,认证静默)、#3594(DNS rebinding,安全)。
  继续补 10+ 条。

### 2) 写/跑用例（真实传输）
- 参考已跑通的 `runner/run_real_http.py`（起 `MCPServer.run_streamable_http_async` → `Client(url,mode=..)`
  连接 → 捕获真实返回对象 → 落盘 `data/real_raw/` + `data/real_index.json`）。
- 入口避坑：**不用** `uvicorn.run(MCPServer)`(报 not callable)；`run_streamable_http_async` 无 log_level；
  传输函数是 `streamable_http_client`；`Client(mode='auto'/'legacy')`。
- 批量扩到 10+ 用例，每个绑定真实 issue 出处。

### 3) 解析（新脚本 `analysis/parse_real_runs.py`）
- 读 `data/real_raw/*.txt` + `real_index.json`（含 case/layer/issue_src），
  复用 `exposure_model.py` 的 `exposure_channel()`/SILENT/ORIGIN 逻辑，
  判定每条真实运行属于 静默/推到Server/调用方异常/单层，写入 `data/real_summary.json`。

### 4) 分析原因（结合 Taraghi 类别 + 四层）
- 统计真实传输集的：静默率、错位率、按四层分布、对应 Taraghi 类别分布。
- **分析"真实故障为何难定位"**：真实故障多属 响应处理/连接错配/认证/生命周期 类，
  暴露形态=静默或推到Server 或调用方异常；对比 in-memory 集(22.5% 静默)，看真实传输集是否更严重。
- 结论写成"为什么真实传输下更隐蔽"的论证段。

### 5) 画图（新图，进 `figs/` + `paper/figs/`）
- `fig_real_transport.png`：真实传输集的三通道/静默 vs in-memory 对照。
- `fig_real_vs_taraghi.png`（可选）：真实故障的 Taraghi 类别频次条形图。
- 复用 `make_figs.py` 风格（matplotlib, dpi=200, 网格, 配色一致）。

### 6) 更新 tex（main_review/05_results.tex + paper/main_body.tex + paper_chinese.md）
- 新增小节（如 `\subsection{Real-transport validation}` 或 RQ3 延伸）：
  写明"真实传输 + 真实 issue 故障"结论（静默率/错位率），并与 in-memory 对照。
- 用 minipage+captionof 插入新图（见 05_results 现有格式）；新增段落标红 + 中文注释。
- 同步 04_setup 加一段"为什么加真实传输层"；同步数字到 docs/numbers.md。
- 保持 label/ref/宏包齐全（booktabs/tabularx/caption/fontawesome5 已加）。

### 7) 存档
- 重跑分析管线，把新数字写入 `docs/numbers.md`、`RECOVERY_README.md` §4.1、`QHISTORY.md`(续8)。
- 可用 GitHub API 提取 issue 链接作论文 footnote 素材。

### 8) 注意
- 目标规模：10+ 真实用例即可，**不要**追求穷尽（Taraghi 已做过全量分类，本层是"机制化验证+真实传输佐证"）。
- 本机无 LaTeX，tex 不编译；只做静态校验（label/ref/宏包/引用键）。
- 数据集匿名 repo/DOI 仍是唯一硬阻塞（正文红 TODO）。

---

## 4. 环境与硬性限制（诚实的边界，决定能做什么）

本机检测结果：
- Python 3.13.9；有 pydantic 2.12.4、pandas 2.3.3、matplotlib 3.10.6、scikit-learn 1.7.2、openpyxl 3.1.5、pypdf。
- **没有 MCP SDK**：`import mcp` 报错；无 `D:\Research\python-sdk`（xlsx 里指向的本地 SDK）。
  → 用例源码用的 SDK 是自定义的 `mcp.server.mcpserver.MCPServer` / `mcp.client.client.Client`（非官方 PyPI 包）。**本地无法重新跑 fault-injection**。
- **没有 openai / anthropic / litellm**；也**无任何 API key** → **无法真正调用商用 LLM（GPT/Claude）做诊断实验**。

**因此确实能做**：
- ✅ 解析 80 次真实运行（已做），统计、交叉分析、生成所有论文表格与图（matplotlib / tikz 数据）。
- ✅ 构建"错位/静默/分层"量化矩阵。
- ✅ 用 scikit-learn / 规则，搭建**离线可运行的诊断 agent**（用 xlsx 真实报错文本做层级归因），作为 LLM 诊断的**离线近似基线**。
- ⚠️ 真正的商用 LLM 诊断实验（P1 核心）：**缺 API key，必须由用户提供 key / LF key，或让用户确认改用离线近似替代**。

**卡点（需用户拍板，见第 7 节）**：
① 商用 LLM 诊断需 API key；② 复现 SDK 实验需 `D:\Research\python-sdk` 或该自定义 SDK 的公开仓库/安装方式。

---

## 5. 需要新增的实验/内容（P0/P1/P2 优先级，面向 IST 饱满度）

### P0 —— 从已有数据重述（零/低成本，立刻变强）
- [x] 已确认 silent=18/80、错位 47/48 (97.9%)、Taraghi 对齐的想法
- [ ] 用强结论替换旧版"13/80 波动"；突出"结构静默 vs 输入依赖静默"
- [ ] 压缩访谈为"一页需求侧证据"（只留 Finding 2/7/8，其余进 Appendix），主线聚焦"难找 bug"
- [ ] 新增"与 Taraghi 等已有故障分类对齐"讨论

### P1 —— 关键新实验（最大加分，但卡 API key 或需替代方案）
- [ ] **LLM 故障诊断基线**：把 80 次运行的原始报错+日志喂给 LLM，让它输出"root-cause 在哪一层"，与真实根因对比 → 诊断准确率（预期被 Server 层错位误导，准确率可能 20-40%）。
- [ ] **干预实验**：在报错中加入根因元数据标注（actual_fault_source = Host/Client/Server/Transport）后，再测诊断准确率 → 量化提升，证明建议可复现。

### P2 —— 规模与多样性扩展
- [ ] 增加网络抖动、并发竞态、超时、插件打包/依赖错误等真实生产故障。
- [ ] 跨 SDK 实现（Python + TypeScript/Node）。
- [ ] 开源 MCP 仓库 issue/commit 挖掘，与合成用例交叉验证（提升外部效度）。

---

## 6. 当前进度（截至 2026-09-23）

**已完成**：
1. ✅ 读 QRS 全部 tex、IST 模板、IST 6 旧版文本。
2. ✅ 与用户确认核心方向 = MCP 故障定位根因研究。
3. ✅ 梳理并交叉统计 xlsx（分层×范围、silent、mismatch）。
4. ✅ clone 用户提供的源码仓库 `MCP-research`（xxyyzz417/MCP-research）。
5. ✅ 解析 4 个 `*results.txt` → `dataset_runs.json`（80 条运行，含报错原文）。
6. ✅ 提取/确认权威量化结论（第 3 节）。
7. ✅ 建立本 TASK.md 单一事实来源文件 + 脚本/目录结构。
8. ✅ 生成论文图表（`figs/` 三张图：fig_layer_distribution / fig_mismatch / fig_silent_failure）+ 表数据（`tables_data.txt` + `scripts/07_make_tables.py`）。
9. ✅ P0 完成：IST 结构设计 + 访谈压缩草稿 + 关键数字（存 `IST_STRUCTURE_DRAFT.md`）。
10. ✅ P1 离线部分完成：诊断基线 + 干预实验（无需 LLM key，脚本 08/09/10）：
    - 基线(无元数据)：总体定位准确率 **40%**；Host/Client/Transport 层根因**全部 0%**（48次全误判为Server）；Server层100%。
    - 干预(加 actual_fault_source 元数据)：理想可观测 **100%** (+60pp)、90%采信标签 **93.8%** (+53.8pp)。
    - 产出：`diag_results.txt` + 图 `figs/fig_diag_accuracy.png`。
    - 结论：把"难找bug"从主观痛点转化为可量化的可观测性缺陷 + 可复现改进路径。
11. ✅ 组合成 IST cas-dc 格式完整 tex：`paper\main.tex`（frontmatter+abstract+highlights+keywords）`+ \input{main_body}`（全部正文）。
    - 标题已聚焦：*Why Is It So Hard to Localize Bugs in Model Context Protocol (MCP) Pipelines? An Empirical Study with a Reproducible Fault-Injection Benchmark*
    - 5 张图已复制到 `paper\figs\`（含 methodology.png 用 QRS 方法图）；cas-refs.bib（用 QRS ref.bib，24 引用键全部存在）。
    - 已静态校验：label/ref 全部匹配（15 个 label 无缺失引用）、figure 引用全部存在、环境闭合、引用键齐全。
    - **注意：本机无 LaTeX 编译器（pdflatex/xelatex/latexmk 不在 PATH）**，无法本地编译；需在装有 LaTeX 的环境（如 Overleaf）编译。
12. ✅ 完整论文核心链条闭环：访谈"难找bug" → 实验证明错位97.9%+静默22.5% → 诊断基线40% → 干预+60pp。
13. ✅ 已打包 `paper\` → `MCP_IST_paper.zip`（含 main.tex / main_body.tex / cas-refs.bib / cas 模板文件 / 5 张图）。
    上传 Overleaf 用 pdfLaTeX+BibTeX 编译即可。本机无 LaTeX 编译器。
14. ⏳ （需 key/无 LaTeX）真 LLM 诊断实验；跨SDK扩展；本地/在线编译出 PDF。

**P0 已全部完成**（可交付）：图(3张)、表(3张数据+1指标)、IST 结构设计、访谈压缩改写草稿。
**P1 离线部分已完成**（可交付）：诊断基线40% + 干预+60pp，图4 + 结果表。

**已创建的脚本**（在 `...MCP_IST_Project\scripts\`）：
- `01_analyze_cases.py` → 逐用例 silent 判定，输出 `cases_analysis.json`（判定正确，silent 结果可靠）
- `02_make_figs.py` → 生成 3 张图：分层分布(fig_layer_distribution)、错位(fig_mismatch)、静默(fig_silent_failure)。**注意：23 用例数可能需按 18/80 修正**
- `03_compare.py` → 对比两版 xlsx
- `04_inspect.py` → 读 results.txt、server 样例
- `05_parse_runs.py` → 解析 80 运行 → `dataset_runs.json`（**silent 判定需改用 xlsx 异常类型列，勿用正则**）
- `00_ls.py` → 列目录真实文件名

---

## 7. 关键转折：环境已打通（2026-09-27/28，重大更新！）

> ⚠️ **重要**：此前 TASK.md 认为"无 MCP SDK、无 key、无法跑实验"。**这条已被推翻！**

- 已 `pip install mcp`（装上官方 **MCP Python SDK v2.2.0**）。
- 已验证：现有用例用的 `from mcp.server.mcpserver import MCPServer` 和 `from mcp.client.client import Client`
  **正是官方 mcp v2 接口**（之前误以为是自定义 SDK）。已成功实跑 `h1_tool_not_exist`，输出与 xlsx 完全一致
  （`Unknown tool: subtract, is_error=True`）。
- **结论：可以真实复现全部 80 用例、添加新用例、重跑统计/图/指标，无需任何 API key。**
- 真 LLM 诊断基线的"真 LLM/agent"= **本 opencode(DeepSeek) 自己作为诊断者**读报错判断根因层（用户确认："你不就是 llm 吗，你是 deepseek 呀"）。

## 7.1 新增"真实难 bug"用例（已跑通并产生有价值发现）

新增 6 个"真实难 bug"（`experiments\advanced\`，也复制到 `MCP-Fault-Benchmark\faultcases\advanced\`）：
- a1 并发竞态（无锁共享状态）、a2 慢工具超时、a3 同名工具重复注册、a4 跨调用状态泄漏、
  a5 流式/多步中断、a6 并发共享变量递增。

**已验证的关键发现（增强论文说服力）**：
- **a3 同名工具重复注册** → SDK 仅输出 WARNING（`Tool already exists: calc`），**静默采用第一个版本**，第二个被忽略。
- **a1/a6 并发竞态** → 返回正常数值，`is_error=False`，SDK 层面完全静默。
- **a4 状态泄漏** → record 前 content=[]、record 后含 99，`is_error=False`（静默泄漏）。
- **a2 慢工具** → 真正触发超时（ExceptionGroup），Transport 层确有超时风险。
- 结论：现有 20 用例的"合成脚本错误"之外，**真实生产级隐蔽故障（竞态/覆盖/泄漏）几乎全是静默失效**，
  这正是"最难 debug"的 bug。新增这些可让论文从"合成脚本错误"升级到"真实隐蔽故障+静默失效"。

## 7.2 正在做：整理成可发布的 GitHub 仓库（进行中）

目标目录：`C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\`
结构：
- `README.md`（已建，含说明/复现/指标/引用）
- `faultcases/original/{host,client,server,transport}/`（已复制 20 个用例 + 00_normal_example.py 基线）
- `faultcases/advanced/`（已复制 run_advanced.py / verify_hardbugs.py）
- `requirements.txt`、`.gitignore`（待建）
- `runner/run_all.py`、`runner/run_advanced.py`（待写）
- `data/raw/` + `analysis/{parse_runs.py,analyze.py,make_figs.py}`（待写/整理）
- `metrics/diagnose.py`（Top-K/混淆矩阵/PR/三档对比图，待写）
- `docs/taxonomy.md`（待写）

## 7.3 下一步（按序，用户在等）

1. 完成 GitHub 仓库整理：把 4 个变体（a/b/c/d 共 80 用例）复制进 repos；写 run_all.py / run_advanced.py /
   requirements.txt / .gitignore / analysis / metrics / docs/taxonomy.md。
2. 真实重跑全部 80 + 新增 6 用例，统一生成完整数据集（20旧+6新，或作为独立"真实难bug"集）。
3. 重新统计（错位/静默，含新增）→ 重画图（分层×范围、错位、静默、诊断准确率）+ 指标
   （Top-K、4×4 混淆矩阵、Precision/Recall、三档对比图）。
4. 本 opencode(DeepSeek) 作为诊断者，真实读取每条报错判断根因层，与真实根因对比 → 真实诊断准确率
   （替代手写规则 40%）。
5. 用新数据/新图更新论文 tex（main_body.tex）与中文版 paper_chinese.md。
6. 更新 TASK.md/README 反映最终结果。

> 用户明确要求：**把实验代码都保存好，将来统一放 GitHub**。因此所有实验代码/数据/脚本应落入
> `MCP-Fault-Benchmark\`，且要可复现、带 README、带注释。

---

## 旧后续（大部分已被上文取代，仅保留仍相关项）
- 生成 figs/ + 表格：已由 02/07 完成，但**新增用例后需重跑并重画**（见 7.3）。
- 离线诊断 agent 已跑（08/09），但**要用本 opencode(DeepSeek) 真实诊断替代手写规则**（见 7.3 第 4 步）。
- IST 完整 tex + 中文版已完成（paper/ 与 paper_chinese.md），**新增数据后需同步更新**。

---

## 8.【数据口径重构 · 2026-10-08 续9】只保留一个真实数据集（闭环规划 + 已做进度）

> 背景与详细记录见 `MCP-Fault-Benchmark\docs\DATA_REBUILD_PROGRESS.md`。

### 为什么重跑（数据口径变更）
- 原论文用两套数据：合成 MCP-Fault-20(80 runs, in-memory) + 真实集(28 runs, Streamable-HTTP)，口径混乱。
- **用户决定**：只保留一个实验，全部用真实 bug，统一真实 Streamable-HTTP 传输，不纠结 in-memory。
- 建立完整官方 issue 库，写清"为什么选这些 case"（带占比证据）。
- 私下对比（20合成 vs 20真实）：结论方向不变（三通道模型成立），仅 3 个 case（s6/s8/t3）通道分类不同。

### 数据源
- 官方仓库 `modelcontextprotocol/python-sdk`（约 24.5k stars）。
- 官方**纯 issue 总数：1,343**（search API `is:issue` 查得，排除 PR）。
- 只研究这一个库，不跨库（论证待写）。

### 已做进度
1. **拉取（✅ 已完成 2026-10-08 晚）**：已补拉 200 条，**全池共 1,343 条纯 issue**（= search API 确认的官方总数）。
   - 用 `analysis/pull_remaining_issues.py`（REST `/issues?state=all` 按 created desc 分页）补拉 #2803–#3656。
   - 缺失区间其余全是 **PR**（已正确过滤）；18 个可复现 bug（#3549–#3646）全部在池内。
2. **初筛（✅ 已完成，已持久化，下次不用重跑）**：对全池 1,343 条做关键词分类 → **BUG 439 / OTHER 457 / QUESTION 277 / FEATURE 88 / CI-REFACTOR 47 / DOC 35**。
   - ⚠️ 初筛是关键词自动分类，有误判/漏判。
   - 数据文件（绝对路径）：
     - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\full_pool_screened.json`（**1,343 条**，含 label + 旧 label_old）
     - `C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\MCP-Fault-Benchmark\data\full_pool\full_bugs_screen_439.xlsx`（**439 条**初筛 bug，表头齐全，字段留空待填）
     - 备份：`full_pool_screened_backup_1143.json`（旧 1143 条版）
   - 复现脚本：`analysis/screen_issues.py`（初筛）、`analysis/make_bug_excel.py`（Excel）、`analysis/pull_remaining_issues.py`（拉取）。
3. **人工复核（✅ 已完成，已持久化）**：对 439 条关键词-BUG 逐条复核 → **保留真 bug 398 条**，排除 41 条真非 bug。
   - **筛选标准（用户确认）：只要是 bug 就保留**，含"功能缺失/规格不符"型缺陷（这些也是真实缺陷）。
   - 保留 398 = 运行时故障 + 功能缺失型 + 规格不符型；排除 41 真非 bug = 使用疑问 19 / 纯功能请求 4 / 非Python-SDK 2 / 环境-依赖-打包 7 / CI-测试-重构 5 / 重复 3 / 无法验证 1。
   - **筛选漏斗：1,343 纯 issue → 439 关键词-BUG → 398 真 bug**。
   - **18 个已知可复现 bug 已强制标 BUG**（`review_bugs.py` 的 `KNOWN_REPRO_BUGS`，非造假）。
   - 数据文件：
     - `...\data\full_pool\bug_review_verdicts.json`（439 条复核 verdict + 原因）
     - `...\data\full_pool\bug_review_full.xlsx`（439 条复核 Excel）
     - `...\data\full_pool\confirmed_bugs.json`（**398 条**真 bug，含 state/created/url/body_head）
     - `...\data\full_pool\confirmed_bugs.xlsx`（**398 条**真 bug Excel）
   - 复现脚本：`analysis/review_bugs.py`（人工复核）、`analysis/make_review_excel.py`（复核 Excel）、`analysis/make_confirmed_excel.py`（确认 Excel）。

### 完整闭环（后续步骤）
1. ✅ 补拉剩余 issue —— **已完成**（全池 1,343 条，18 个复现 bug 全在）。
2. ✅ 从全量 bug 里只筛真 bug（人工复核 439 条初筛 → **保留 398 真 bug**；只要是 bug 就保留，含功能缺失/规格不符型；仅排除 41 条真非 bug）。
3. 分类：层 + Taraghi 类别 + 可复现性分层。
4. 建单一真实数据集（替代 MCP-Fault-20 + 28真实集）。
5. 重跑分析（真实 Streamable-HTTP）：三通道分布、静默率、错位率。
6. 重画图（fig_layer_distribution/fig_mismatch/fig_silent_failure/fig_causal_graph/fig_sample_frequency 等；fig_real_* 可能合并删除；fig_diag_clues/fig_topk/fig_repair 需重跑 LLM）。
7. 重算全部关键数字（总runs/静默率/三通道/错位率/LLM诊断45→52.5/修复69.6/采样占比）。LLM诊断/修复需用户在真实集重跑 DeepSeek-V4。
8. 重写正文（摘要+高亮/Intro/Related Work加"为什么只选一个库"论证/Methodology/Setup重写采样理由/Results所有Finding数字+图引用/Discussion+Conclusion）。
9. 产出全量 bug 分类 Excel（只含bug行）：类别|序号|Case ID|层|GitHub Issue|Issue链接|Taraghi类别(人工)|暴露通道|真实性|描述|完整报错文本。
10. 另建新文件夹 `IST_Right_REAL_merged`（已建，保留现有 merged 不动），放改好的 .tex+新图+模板+数据说明，打包新 zip。
11. **最后更新到 GitHub**：把所有实验代码、数据、脚本、Excel、结果统一整理进 GitHub 仓库（含 README、可复现说明），供审稿人/读者复现。用户明确要求数据重构完成后**发布到 GitHub**（匿名 repo/DOI，正文红 TODO 待填）。

> ## ⚠️【2026-10-10 数据口径收紧 · 用户最终意图（重要，覆盖旧"350有效"口径的理解）】
> **用户决定**：凡是**已在 mcp 2.2.0 里被修复**的 bug（跑出来行为正确 = fixed-in-current）**不是 bug**，
> **必须从数据集里删掉**。**最终活跃数据集 = 只保留当前还没修复的真 bug**。
> - **删除标准**：只有"能跑出来、行为正确（fixed-in-current）"才删。
> - **保留标准**：① 能跑出来且确实报错（真缺陷）；② 跑不出的（需 OAuth/特定环境/并发/SSE/规范缺口）
>   一律**保留**，记为"复现受限 + 原因"。原因本身（如"需OAuth""需并发"）就是"这类 bug 难定位"的证据。
> - **规范缺口（代码审查发现）= 算 MCP bug**：表现为"不崩溃但行为不符合规范"，是"难定位"的一类（如
>   #1415/#1420/#1458 取消通知缺失、#2883 URL规范化错、#3174 OTel状态错）。
> - **用户真实目的**：收集每条 bug 的**报错文本/受限原因**，分析"到底是什么原因导致难定位"。
>   所以"复现受限"不是废数据，而是"难定位原因"的证据。
> - ⚠️ **需用户最终拍板**：跑不出的（需账号/环境/并发/规范缺口）是"保留标待定"（推荐，符合上述目的），
>   还是"也从活跃数据集剔除，只留能确认真实存在的"？用户已倾向"只删已确认修复的"（2026-10-10 已答）。

### 下次进来第一步
**全池已拉齐（1,343 条）、初筛已完成（BUG 439）、人工复核已完成（保留真 bug 398）**。
下次直接读 `data\full_pool\full_pool_screened.json` + `bug_review_verdicts.json` +
`confirmed_bugs.json`（**+ confirmed_bugs.xlsx**），**不要重复拉取/初筛/复核**。
下一步 = 从 **398 条真 bug** 中按标准（可复现/属普通运行时故障/排除 SDK 内部 bug）筛选，
建**单一真实数据集**（替代 MCP-Fault-20 + 28真实集）。

---

## 9.【数据集建立过程 · 论文改写状态 + 重跑/重写清单】（2026-10-08 晚）

> ## ✅【总览 · 整条数据重构链（勾选式）】
> 用户心智模型 = **订好数据集 → 重跑所有实验 → 更新论文和结论 → 打包 zip → 发布 GitHub**。
> - [x] **订好数据集**：全池 1,343 → 初筛 439 → **398 真 bug** → **剔除 56 条 2.2.0 已修复（fixed_removed.json）→ 342 有效**（2026-10-10 更新；batch12 剔除 8 条）
> - [x] ① **补全 398 完整 body**（✅ 已完成 2026-10-10 续16：`analysis/backfill_bodies.py` 本地补 396/398；
>   #469/#753 经 GitHub API 直查确认**本就空 body**（信息全在标题，非数据缺口），已写回空 body。
>   398 条 body 已齐：396 完整 + 2 真·空。无需再补。）
> - [x] ② **分类 398 的原始层**（✅ 已完成 2026-10-10 续17：**用户决定不加 Taraghi 类别(人工)列，只按 4 层**。
>   **专家逐条审阅 398 条**（非关键词自动）→ `analysis/author_origin_labels.py` + `apply_origin_labels.py`
>   → `data/full_pool/origin_labels.json/.xlsx`。结果：**Server 130 / Client 128 / Transport 90 / Host 50**；
>   18 verified（实测）+ 380 expert。**报告层/暴露通道列留待复现实验(第④步)填**。）
> - [ ] ③ **复现 398 条**（⚠️ **详细作战图见 `MCP-Fault-Benchmark\docs\REPRO_PROGRESS.md`**，重开后先读它。
>   框架 `runner/repro_cases.py`+`repro_framework.py`+`data/repro_progress.json` 已建好（可断点续跑）。
>   ✅ **已复现 48 条**（18 verified #3549–#3646 + 30 batch1/2/3/4/5/6/7/8：#234/#348/#2114/#2422/#3266/#1702/#3342/#3385/#3656/#3099/#3067/#3341/#2770/#2057/#2618/#2539/#110/#698/#743/#1060/#1361/#2153/#3351/#244/#1974/#891/#2386/#2431/#1579）。
>   ✅ 第1类10条已攻克（6 fixed-in-current、2 观察型、2 reproduced）；第2批序列化/校验 12 条已跑（6 reproduced）；第3批协议类 5 条已跑（3 reproduced）；第4批错误掩蔽/序列化 19 条已跑（7 reproduced）；第5批资源/ctx/类型校验 15 条已跑（3 reproduced）；第6批杂项 Server 17 条已跑（2 reproduced）；第7批资源未找到错误路径 7 条已跑（1 reproduced）。
>   剩余 ~351 条按 `_remaining354_classified.txt` 分类逐批真跑（大量为 SDK 内部 bug / 认证 / 环境 / SSE-stdio /
>   规格合规）。详见 REPRO_PROGRESS.md §四·B/§五/§六/§八。
>   用户要求全做、没环境装环境；诚实原则：能复现记 done，不能如实 limited+原因，不造假。
>   ✅ **全部 bug 分析表已建**：`analysis/make_all_bugs_excel.py` → `data/full_pool/all_bugs_analysis.xlsx`
>   （350 行，18 列合并表头，**已复现 48 条已标绿**，脚本文件名/触发代码片段已填，故障范围标记留空）。
>   ⚠️ **2026-10-10：数据集从 398 → 350**（剔除 48 条 mcp 2.2.0 已修复）。`make_all_bugs_excel.py` /
>   `assess_reproducibility.py` 已读 `data/full_pool/fixed_removed.json`（48 条剔除清单）过滤，产物自动变 350。
>   **论文 sec:sampling 已按"398 确认 → 剔除 48 已修复 → 350 有效"改写**（main_body.tex + main_review/04_setup.tex 双份）；
>   层分布改用 origin 4 层（Server 93/Client 121/Transport 87/Host 49）、open/closed 94/256、复现数 18→48，
>   并新增 `analysis/dataset_stats.py` 精确复现这些数字（→ `data/full_pool/dataset_stats.json`）。
>   ⚠️ 注意 `dataset_stats.py` 的 reproduced 统计=30（只算 repro_progress 里 done 的）；论文的 48 = 18 verified + 30 batch，两者口径不同。
>   ✅ **可复现性分层表已建**：`analysis/assess_reproducibility.py` → `data/full_pool/repro_tiers.xlsx`
>   （350 条分层：**T1 48=真实已复现** / T2 130 / T3 130 / T4 32 / T5 10；**T1-fixed 48 已从数据集剔除**。
>   **脚本自动读 repro_progress.json 实际结果，每次复现后重跑即同步，勿重分析。** 详见 REPRO_PROGRESS.md §二·D）
>   ⚠️ **口径：已复现=48**；有效数据集=350（fixed-in-current 48 条已剔除，不算复现）。
> - [ ] ④ **重跑实验**：三通道/静默/错位 + 重画图 + LLM 诊断/修复（§9.3 第3-6步）
> - [ ] ⑤ **更新论文和结论**：全文旧口径(80/18/合成)改 398（§9.4，含 Conclusion）
> - [ ] ⑥ **打包 zip**（§9.5）+ ⑦ **发布 GitHub**（匿名 repo/DOI）
>
> ⚠️ 注意：全池数据只有新拉的 200 条存了完整 body；旧 1143 条仅存 body_head。
> 原始完整 body 在临时 `C:\Users\KEHUIC~1\AppData\Local\Temp\opencode\ist_work\all_issues.json`（仅旧 1143 条）。
> 若要高质量分类/复现 398，需先用 GitHub API 补全 body（约 398 次请求，分几批）。

> ## ✅【最新标记：数据集建立过程这一段是最新的，且已按 350 口径改写（2026-10-10）】
> **论文里"数据集建立过程"这一节 = 最新的、已定稿的内容**（描述 **398 确认 → 剔除 48 已修复 → 350 有效** 普查），
> **别被论文其余部分的旧口径（MCP-Fault-20/80 runs/18 复现）误导**。
> **这一节的位置/文件名：**
> - 工作版：`C:\Users\kehuichen2\Desktop\IST\MCP_IST_Project\paper\main_body.tex`
>   → 小节 `\subsection{Dataset Construction and Sampling Rationale}`（`\label{sec:sampling}`，
>   约 L600 起，在 Experimental Setup 节内）。
> - 桌面审阅版：`C:\Users\kehuichen2\Desktop\IST\main_review\04_setup.tex` → 同名小节（约 L173 起）。
> **⭐ 2026-10-10 关键变更：数据集 398 → 350**（剔除 48 条 mcp 2.2.0 已修复）。sec:sampling 已改写为
> "398 确认 → 剔除 48 已修复 → 350 有效"；层分布改用 origin 4 层（Server 93/Client 121/Transport 87/Host 49）、
> open/closed 94/256、复现数 18→48。剔除清单 `data/full_pool/fixed_removed.json`；复现脚本
> ⚠️ **【2026-10-10 更晚】数据集已进一步缩到 342**（batch12 真跑剔除 192/594/838/753/3493/212/1363/1577 共 8 条）。
> **论文里 sec:sampling 的 350/Server93/Client121 等数字已过期，第④步改写时须同步为 342 的新分布**（当前 Server 91/Client 118/Transport 85/Host 48，open/closed 93/249）。
> `analysis/dataset_stats.py`（→ dataset_stats.json）。详见 §9 总览 + REPRO_PROGRESS.md §二·D。
> **全文其余部分暂未改**（还是旧口径），等 350 实验重跑后按 §9.4 统一改写。
> **改完后怎么看全文是否统一：** 全局搜 `MCP-Fault-20` / `80 runs` / `18 issues` / `4 variants` /
> `in-memory`，应全部替换为新口径；`sec:sampling` 是唯一已定稿的"数据集建立"段落。

### 9.1 已完成的论文改动（这一段）
- **`paper/main_body.tex` + `main_review/04_setup.tex` 的 `sec:sampling` 已重写为
  "Dataset Construction and Sampling Rationale"**：把"为什么选这些数据"升级为完整可复现的数据集
  建立管线。核心 = 对官方 python-sdk 一个库做**全量普查**（1,343 纯 issue → 439 初筛 bug →
  **398 确认真 bug**），讲清 **dataset size / collection criteria / 代表性如何保证**，并解释
  **为何只收集一个库就够了**（与 Taraghi 跨库 13,555 repos/3,282 bugs 的权衡：深 vs 广）。
- 已删旧"33/18 复现采样"表述与 `fig:samplefreq`（label/ref 已清理，无悬空）。
- 双语注释 + CHANGELOG 已更新；begin/end 配平（main_body 34/34、04_setup 5/5），无重复 label。

### 9.2 ⚠️ 全文仍自相矛盾（用户确认：先只写这一段，其余跑完实验再改）
新写的 sec:sampling 描述 398 真 bug 普查，但论文其余部分仍用旧口径 **MCP-Fault-20(80 runs)+18 复现真实 issue**。**这些暂不动**，等实验在 398 数据集上重跑后再统一改写。

### 9.3 还需要重新跑什么（实验，按序）
1. **分类 398 真 bug**：逐条标 层(Host/Client/Server/Transport) + Taraghi 类别 + 可复现性分层（平台/认证/示例/通用可复现）。产出：全量 bug 分类 Excel（类别|序号|Case ID|层|GitHub Issue|Issue链接|Taraghi类别(人工)|暴露通道|真实性|描述|完整报错文本）。
2. **选可复现子集**：从 398 里挑能在本机(mcp 2.2.0 + Streamable-HTTP)干净复现的真实 bug（现已知 18 个；尽力扩）。
3. **重跑分析**（真实 Streamable-HTTP）：对选定的真实 bug 跑 三通道分布、静默率、错位率。重算关键数字。
4. **重画图**：fig_layer_distribution / fig_mismatch(三通道) / fig_silent_failure / fig_causal_graph 等全部用新数据重建；fig_real_* 可能合并删除。
5. **重跑 LLM 诊断 + 修复实验**（需用户跑 DeepSeek-V4）：诊断基线/Top-K/线索工具(45→52.5?)/修复(69.6?) 全部在真实集重算。
6. **算采样占比**：选定 case 占 398 比例、类别覆盖率、Taraghi 最痛类别覆盖。

### 9.4 跑完还需要重新写哪里（论文位置清单，依 main_body.tex 行号）
- **摘要/高亮/main.tex**：MCP-Fault-20(80 runs) → 398 真 bug 普查口径。
- **Intro**：L43/L66/L103 处 "MCP-Fault-20" 表述改为 398 真 bug 数据集。
- **Related Work**：L241-280 与 Taraghi 对比段已大致覆盖（单库论证已在 sec:sampling），如需可再强化"为何单库"。
- **Methodology**：L367 "introduce the MCP-Fault-20" → 改为真实 bug 数据集。
- **Setup**：
  - L370-436 `Construction of the MCP-Fault-20 Dataset` 整节 → 改为"真实 bug 数据集构建"（删除合成 20 案例表 tab:cases 或改为真实 bug 表）。
  - L443-445 "80 total test runs / 4 variants" → 新口径。
  - L481 合成脚本错误表述 → 真实 bug。
  - L506 in-memory 局限段 → 真实传输。
- **Results**（L599+）：L599/L691/L697/L701/L716/L759/L777/L792/L799/L833/L839/L967 等所有 80 runs/18 issues/22.5%/合成 处 → 新数字。
- **Discussion**：L995/L1039/L1052 → 新口径。
- **Conclusion**：L1138/L1152 → 398 真 bug 数据集 + 新数字。
- **main_review 拆分稿**：01_intro / 03_method / 04_setup / 05_results / 06_discussion / 07_conclusion 同步上面改动。
- **paper_chinese.md**：同步中文版。
- **docs/numbers.md**：权威数字全部更新。

### 9.5 收尾（最后做）
- 建新文件夹 `IST_Right_REAL_merged`（已建），放改好 .tex + 新图 + 模板 + 数据说明。
- **打包新 zip**（一段段 tex 结构，方便改）。
- **发布 GitHub**（匿名 repo/DOI，正文红 TODO 待填）。

---

## 10.【关键发现 · 已复现 bug 清单（供第④步分析/论文引用）】

> ⚠️ **用途**：第④步重跑实验（三通道/静默/错位 + 报告层/暴露通道分类）与论文结果写作时，
> **直接从本清单引用已复现 bug 及其暴露形态**，不必再翻散落记录。每批复现后在此追加。
> 详细逐条触发/报文见 `MCP-Fault-Benchmark\data\real_raw\real_{n}.txt` + `repro_progress.json`。

### 10.1 三通道暴露模型 —— 已复现 bug 的分通道证据（核心，写论文用）

**通道① 推到 Server（错位：上游故障被 Server 调度层重报为 `Error executing tool X`, is_error=True）**
已复现证据（source 层 → 被错报为 Server）：
- **#110**（Client 源：server 返回非 UTF-8 字节 → 客户端 JSON 解码失败被掩蔽成 `Error executing tool bad`）
- **#698 / #743 / #1361 / #2153**（Server 源：工具抛异常，真实异常值/根因被吞成 `Error executing tool boom`）
- **#891**（Server 源：dict+str 非法操作真实 TypeError 被掩蔽成 `Error executing tool f`）
- **#1060**（Server 源：Image 类型 PydanticSchemaGenerationError 被掩蔽成 `Error executing tool img`）
- **#3351**（Server 源：输入校验 → `Error executing tool f: 1 validation error ... Input should be a valid integer`，校验细节部分保留）
- **#2386**（Server 源：CWE-209 错误清洗 —— 真实 ValueError "sensitive internals: password=abc" 被掩蔽成 `Error executing tool boom`）
- **#2431**（Server 源：McpError 非 pickle-safe —— unpickle 错误被掩蔽成 `Error executing tool boom`）
- **#1579**（Server 源：read_resource 资源未找到 → `MCPError: Unknown resource`, JSON-RPC code=-32602；错误路径复现，具体"错误码不对"是规格判断）
- **#2741**（Transport 源：有状态 Streamable HTTP —— 会话内异常被掩蔽为通用 `Error executing tool boom`, is_error=True，真实 cause 只在独立 "Session crashed" 日志）

> **结论**：真实报错文本被**通用化**（`Error executing tool <name>` + `is_error=True`），
> 真实根因/异常值/字节错误/类型错误/敏感信息全部丢失 —— 这是"难定位"的最强机制证据。

**通道② 静默（is_error=False，逻辑错误被无声吞掉）**
已复现证据（需人工判断，框架自动检测不敏感，已在进度文件修正 defect_captured）：
- **#3067**（Server 源：`call_tool(add,{a:1,b:2,typo:9})` 返回 3 无报错，typo 被静默丢弃 extra=ignore）
- **#2057**（Client 源：`"id":null` 被当通知静默接受，HTTP 202 未拒绝）
- **#2618**（Transport 源：MCP-Protocol-Version header 与 body 不匹配，HTTP 200 按 body 协商未校验）

**通道③ 调用方裸抛 Python 异常**
已复现证据：
- **#2429**（Server 源：outputSchema 验证阻断 isError:true 路径；异常路径正确返回 is_error=True）
- **#244 / #1974 / #3337**（注册期错误：server 构建时抛 ValueError/AttributeError/InvalidSignature，client 根本无法连接/列出工具）

### 10.2 已复现 bug 的"层分布"证据（第④步算错位/静默用）

按 origin 层整理（均可溯源到 `repro_cases.py::b_<n>` + `real_raw/real_<n>.txt`）：
- **Server 源（主要，多数为工具抛异常/序列化/注册期）**：#234/#348/#2114/#2422/#3266/#1702/#3342/#3385/#3656/#3099/#3067/#3341/#2770/#2539/#698/#743/#1060/#1361/#2153/#891/#244/#1974/#891/#2386/#2431/#1579 + verified 中 Server 源（#3549/#3554/#3569/#3573/#3578/#3585/#3586/#3592/#3640/#3643/#3644）
- **Client 源**：#110/#2057 + verified 中（#3557/#3637/#3646 等）
- **Transport 源**：#2618 + verified 中（#3556/#3560 等）
- **Host 源**：#3572/#3579/#3637/#3646 等（verified 中）

> ⚠️ **诚实边界**：已复现 48 条中，绝大多数呈现"通用错误掩蔽/注册期错误/静默"三种难定位形态，
> 只有极少数（如 #3351）保留了部分校验细节。**这些正是论文"为何难定位"的实证核心**。
> 注：48 条已复现中有大量是"工具抛异常被掩蔽"（`Error executing tool X`），归 Server 源；真正跨层错位（源≠报告层）的证据主要集中在 verified 18 条 + #110/#2057/#2618。

### 10.3 关键发现（每批，供 Discussion/根因分析引用）
- **第4批**：7 条全为"通用错误掩蔽"（`Error executing tool X`, is_error=True 隐藏真实根因/异常值/字节错误）→ 支撑"错误被通用化掩盖"。
- **第5批**：#244/#1974 为**注册期错误**（SDK 装饰器/类型发现层 bug，server 起不来）—— 与运行时错误掩蔽不同的一类难定位根因。
- **第6批**：#2386 直接对应 **CWE-209**（错误消息泄露/被清洗）主题；#2431 McpError 非 pickle-safe。均呈现"通用错误掩蔽"。
- **第7批**：#1579 资源未找到错误路径（`MCPError: Unknown resource`, code=-32602）复现；#2794（SEP-2164）已在 2.2.0 满足规格（fixed-in-current）。
- **通用观察**：mcp 2.2.0 已修复大量 1.x 时代 bug（fixed-in-current 48 条）；多个 defect（静默忽略/错误码丢失/协议不匹配）依赖**人工判断**（框架自动关键词检测不敏感）。

### 10.4 【本次会话新增·可复用代码/表格清单（防无用功）】

**复现框架（已建好，勿重建）**：`MCP-Fault-Benchmark\runner\repro_framework.py`（引擎）+ `runner\repro_cases.py`（Case 定义）。
- **本次新增 batch '4'–'9' 的 builders/cases**（全部在 `repro_cases.py`，已 py_compile 通过）：
  - batch '4'（19）：b_110/b_357/b_488/b_511/b_662/b_698/b_743/b_820/b_987/b_1060/b_1361/b_2153/b_3123/b_3345/b_3351/b_3384/b_3473/b_3487/b_3649
  - batch '5'（15）：b_244/b_1974/b_3337/b_891/b_140/b_2066/b_381/b_1391/b_2519/b_2960/b_2541/b_1215/b_1853/b_1482/b_1131
  - batch '6'（17）：b_103/b_123/b_178/b_262/b_337/b_341/b_389/b_399/b_853/b_1267/b_1768/b_2326/b_2386/b_2431/b_3434/b_3476/b_3484
  - batch '7'（7）：b_1579/b_2794/b_268/b_929/b_858/b_2156/b_2702
  - batch '8'（13）：b_3227/b_1843/b_1873/b_2376/b_892/b_1010/b_1212/b_2688/b_2741/b_3639/b_2848/b_2655/b_3150
  - batch '9'（7）：b_3273/b_1382/b_2375/b_2432/b_1717/b_2480/b_2328
  - batch '10'（15，2026-10-10）：b_280/b_691/b_290/b_1144/b_701/b_1079/b_1835/b_2548/b_2673/b_2564/b_3174/b_3490/b_3228/b_3503/b_2883
  - batch '13'（49，2026-10-10）：b_147/b_201/b_298/b_355/b_402/b_407/b_410/b_552/b_575/b_623/b_668/b_680/b_788/b_813/b_831/b_1051/b_1070/b_1095/b_1097/b_1100/b_1152/b_1213/b_1214/b_1219/b_1272/b_1372/b_1420/b_1421/b_1422/b_1423/b_1458/b_1648/b_1658/b_1744/b_1789/b_1805/b_1830/b_1941/b_1967/b_2064/b_2110/b_2604/b_2605/b_2958/b_3216/b_3469/b_3483/b_3522/b_3631（并发/异步/规范缺口/观察型，全部 limited，0 新复现）
  - **batch '14'（139，2026-10-10，全量补齐）**：`runner/repro_cases_b14.py`（接 `BATCHES['14']`）= 剩余全部**非认证**未追踪 bug（94 ENV/TRANSPORT-SETUP + 30 OTHER + 10 EXAMPLE + 5 SERIALIZATION-VALIDATION）。**1 新复现（#417）+ 138 limited**。**至此全部非认证 bug 已真跑**（342 有效 = 49 复现 + 301 limited + 48 认证跳过）。
- **BATCHES 字典**：'4'/'5'/'6'/'7'/'8'/'9'/'10' 已加；跑法 `python runner/repro_framework.py --batch N`。
- ⚠️ **框架已扩展（2026-10-10）**：`repro_framework.py` 加 `transport='sse'`（sse_client + ClientSession）、
  `disconnect`/`concurrency`/`reconnect`、`exc()` 递归展开 ExceptionGroup。11 条 SSE 场景 bug（batch '11'，#398/#585/#783/#1437/#1821/#906/#1190/#3356/#332/#491/#2965）
  改用 SSE 真跑：**0 新复现，全部 limited**。#491 经递归异常提取证实为 `Method not found`（订阅 API 已移除 = fixed-in-current），
  已纠正初版误判的 ExceptionGroup DONE。累计仍 48。
- **`repro_framework.py` raw_post 已扩展**：支持 `content_type`（覆盖 Content-Type）与 `raw_body`（裸字节 body）。
- **每个 builder 触发方式**（method/target/args）都定义在 CASES 里，能直接跑；原始报文落 `data/real_raw/real_{n}.txt`。

**分析/表格脚本（每次复现后重跑同步）**：
- `analysis/make_all_bugs_excel.py` → `data/full_pool/all_bugs_analysis.xlsx`（**398 行，18 列，已复现 48 条标绿**，脚本文件名/触发代码片段已填）。
- `analysis/assess_reproducibility.py` → `data/full_pool/repro_tiers.xlsx`（**T1 48 / T1-fixed 48 / T2 130 / T3 130 / T4 32 / T5 10**）。
- `data/repro_progress.json`（逐条 status=done/limited + reason + message + file，断点续跑依据）。

**本次复现结论（第④步分析直接用）**：
- 48 条已复现中最突出的形态 = **通用错误掩蔽**（`Error executing tool X` + `is_error=True`），覆盖 #110/#698/#743/#1060/#1361/#2153/#891/#2386/#2431/#2741 等。
- **注册期错误**：#244/#1974（server 构建时抛 ValueError/AttributeError，client 连不上）。
- **静默**：#3067/#2057/#2618（需人工判断）。
- **跨层错位证据**：verified 18 条 + #110（Client 源报成 Server）/ #2057 / #2618。
- **【2026-10-10 重要诚实结论】mcp 2.2.0 已修复绝大多数旧版报告 bug**：batch 8/9 真跑 20 条，仅 1 条新复现（#2741 通用错误掩蔽），
  其余 19 条多为 fixed-in-current（#3227/#1843/#1873/#2376/#2432/#2328）或 not-exercised（需并发/SSE/绕过 Client 的特定场景）。
  **T1-fixed 从 42 → 48**。仍可复现者高度集中在"通用错误掩蔽"类 —— 这**强化**而非削弱论文核心论点。
  ⚠️ 剩余 ~350 条绝大多数为 auth/env/SSE-stdio/协议规格/观察型，单次 streamable-HTTP 无法触发；
  需扩展框架支持 SSE/断开/重连/并发（REPRO_PROGRESS §五）或如实记 limited+原因。
  ✅ **batch '10' 已跑（2026-10-10）**：15 条全部 limited（0 新复现）——再次印证 mcp 2.2.0 已修复绝大多数旧版 bug。
  剩余可复现者集中在"通用错误掩蔽"（Error executing tool X）类。**累计已复现仍为 48**。


---

## 12.【下一步行动清单 · 重开后照做】（2026-10-10 记录）

> 用户决定：**除需登录/认证的 bug 外，其余全部真跑一遍**。已完成 batch 13 + batch 14（**全部非认证 bug 已真跑完**），
> 下一步进入第④步（更新论文）。

### 当前权威状态（已固化，2026-10-10 最新）
- **数据集 = 342 有效**（398 确认 − 56 已修复剔除，fixed_removed.json 56 条）
- **已复现 = 49**（31 batch + 18 verified；#417 为 batch 14 新增），全部可溯源
- **层分布（342）**：Server 91 / Client 118 / Transport 85 / Host 48；open/closed 93/249
- **342 = 49 已复现 + 245 不能复现（如实记录原因）+ 48 认证类跳过**（需 OAuth/凭证，用户确认跳过）
- **repro_progress**：49 done / 301 limited / 350 tracked
- **Excel**：all_bugs_analysis.xlsx 342 行 20 列，49 绿；列12=复现状态 13=是否能复现 14=不能复现的原因
  15=脚本文件名 16=故障描述 17=触发代码片段 18=异常类型 19=完整报错文本 20=故障范围标记
- **repro_tiers**：T1 49 / T2 174 / T3 47 / T4 72 / T5 0
- **复现代码**：`runner/repro_cases.py`（batch 1-13）+ `runner/repro_cases_b14.py`（batch 14，接 `BATCHES['14']`）

### 已完成的复现批次
batch 1..9（batch 2-9 = 序列化/协议/错误掩蔽/注册期/资源/杂项/客户端协议）、batch 10（15 条，0 新复现）、
batch 11（SSE 11 条，0 新复现）、batch 12（并发/断开/异步 8 条，0 新复现 → 已剔除 192/594/838/753/3493/212/1363/1577）、
**batch 13（49 条并发/异步/规范缺口/观察型，0 新复现，全部 limited，见 REPRO_PROGRESS §四·L）**、
**batch 14（139 条非认证全量补齐：94 ENV/TRANSPORT-SETUP + 30 OTHER + 10 EXAMPLE + 5 SERIALIZATION-VALIDATION，1 新复现 #417 + 138 limited，见 REPRO_PROGRESS §四·M）**。

### 【✅ 已完成：全部非认证 bug 真跑（batch 13 + batch 14，2026-10-10）】
**batch 13（49 条）**：0 新复现，全部 limited（spec-gap / observation-only / not-exercised / env-specific / external-tool / scenario-specific）。
**batch 14（139 条）**：**1 新复现（#417 通用错误掩蔽）+ 138 limited**（环境/示例/传输配置/协议观察，无法单次 streamable-HTTP 触发）。
**用户要求"除需登录/认证外全部真跑"** → 至此 342 有效数据集 = **49 已复现 + 301 已如实记录 limited + 48 认证类跳过**。
**累计已复现 48 → 49，数据集仍 342**（无新剔除）。详见 `docs/REPRO_PROGRESS.md` §四·L / §四·M。
⚠️ 认证类 48 条（需 OAuth/凭证）未跑，如实跳过（用户确认）。

> **下一步（第④步）**：全部非认证 bug 已跑完，可进入第④步——更新论文 sec:sampling（350→342 新分布）+
> 重算三通道/静默/错位 + 重画图 + LLM 诊断重跑。详见 §9.4 按行号清单与 §12 末尾。

**候选清单（batch 13 的 49 条，已在 _rest.py 核对，见下面）**：
#147 #201 #298 #355 #402 #407 #410 #552 #575 #623 #668 #680 #788 #813 #831 #1051 #1070 #1095 #1097 #1100
#1152 #1213 #1214 #1219 #1272 #1372 #1420 #1421 #1422 #1423 #1458 #1648 #1658 #1744 #1789 #1805 #1830 #1941
#1967 #2064 #2110 #2604 #2605 #2958 #3216 #3469 #3483 #3522 #3631

**能单次构造真实触发的（重点先跑）**：
- #201（ctx.info 客户端日志挂起）→ 工具里 ctx.info 构造
- #355（Lifespan/AppContext 类型错误）→ lifespan 构造
- #407（请求超时 5s）→ 慢工具 + 短 client_timeout
- #2605（重复 initialize 覆盖 client_params）→ 手动两次 initialize
- #1372（fastmcp.run() 报错）→ 直接调 run()（mcp 2.x 可能改名/报错）
- #2110（HTTP 吞非2xx）→ raw_post 到坏端点
- #1941（POST-only server 挂起）→ 需特殊构造
- #1097（Roots/List 挂起）→ list 操作

**规范缺口/观察型（#1420/#1421/#1422/#1423/#1458/#3483/#3216/#623/#668）**：多为代码审查发现、不崩溃无报错，
如实记 limited + 原因（"规范缺口：SDK 行为不符合协议规范，无运行时报错可捕获"），**不剔除**（属"难定位的一类"）。

**需特殊场景/外部（#788/#831/#1051/#1070/#1100/#1152/#1213/#1214/#1219/#1272/#1648/#1658/#1744/#1805/#1830/#1967/#2064/#2604/#2958/#3469/#3522/#3631/#552/#575/#813/#1789/#298/#410/#402/#147/#680）**：
需真正连接断开/ClientSessionGroup 多 server/stateless/反代/特定平台等，MCPServer 高层 API 难精确触发 →
如实记 limited + 原因；能构造的（如 #1648/#3469 断开读 body 报 500、#3631 通知触发重复响应）尝试真跑。

**跑完后的动作**（✅ 已完成 2026-10-10，含 batch 14）：
1. ✅ `python runner/repro_framework.py --batch 13`（49 条，0 新复现）+ `--batch 14`（139 条，1 新复现 #417）
2. ✅ 每条结果核对 status 与真实一致；无行为正确剔除（诚实：无法断言 fixed-in-current），需触发 → 记 limited+原因
3. ✅ `python analysis/make_all_bugs_excel.py`（342 行，49 绿）
4. ✅ `python analysis/assess_reproducibility.py`（T1 49/T2 174/T3 47/T4 72/T5 0）+ `python analysis/dataset_stats.py`（342：Server 91/Client 118/Transport 85/Host 48，复现 49）
5. ✅ 更新 `REPRO_PROGRESS.md`（§四·L/§四·M + §二·D 分布）+ `TASK.md`（§10/§12）+ `RECOVERY_README.md` + `QHISTORY.md`
6. ✅ 自检：每条在 repro_cases.py(_b14) / repro_progress.json / all_bugs_analysis.xlsx / REPRO_PROGRESS.md 四处一致

### 【之后的第④步】（本批跑完后）
1. 论文 sec:sampling 旧写 350 → 改为 342（新分布 Server 91/Client 118/Transport 85/Host 48，open/closed 93/249，复现 49）
2. 同步权威数字到 docs/numbers.md
3. 全文旧口径（MCP-Fault-20/80 runs/18 issues/350）→ 新口径（见 TASK.md §9.4 按行号清单）
4. 重画图（如基于旧数据）+ 需 LLM 重跑诊断的部分（用户跑 DeepSeek-V4）
5. 第⑤步改论文 → ⑥打包 zip → ⑦发布 GitHub

### 重开第一步
读 `RECOVERY_README.md` + `TASK.md` §12（本段）+ `data/repro_progress.json` + `docs/REPRO_PROGRESS.md`。
**已跑 batch 1-14（全部非认证 bug），勿重跑**（batch 13 见 §四·L，batch 14 见 §四·M，139 条）。下一步 = **第④步**：
更新论文 sec:sampling（350→342 新分布）+ 重算三通道/静默/错位 + 重画图 + 需 LLM 重跑诊断（用户跑 DeepSeek-V4），
见 §12 末尾 + §9.4。复现代码在 `runner/repro_cases.py`（batch 1-13）+ `runner/repro_cases_b14.py`（batch 14）。

### 【2026-10-11 两层数据集分析已完成 · 第④步前半】
**用户确认数据集写法 = 两层**：342（分析/普查数据集）+ 49（实证复现子集），金字塔 1343→439→398→342→49。
**重跑分析已完成**（新脚本 `analysis/analyze_active_dataset.py` → `data/full_pool/active_dataset_analysis.json`）：
- **TIER A（342 描述统计）**：漏斗 1343→439→398→342；层分布 Server 91/Client 118/Transport 85/Host 48；
  open/closed 93/249；复现 49 / 受限 245 / 认证跳过 48；受限原因分类（env/transport 94、not-exercised 62、
  auth 48、观察型 29、clean-success 25、example 10、observation-only 9、spec-gap 6 等）。
- **TIER B（49 三通道，基于运行时证据人工归类）**：推到Server 7 / 静默 11 / 调用方裸抛 3 /
  单层掩蔽 17 / 单层正确 8 / 注册期错误 3。**非Server错位 10/13 = 76.9%**；**静默 11/49 = 22.4%**；
  **通用掩蔽 17/49 = 34.7%**（最强机制）。
- **新图**：`figs/fig_funnel.png` / `fig_exposure_channels.png` / `fig_repro_reasons.png`。
- **Excel 回填**：`analysis/backfill_exposure_marker.py` → `all_bugs_analysis.xlsx` 列19（故障范围标记）已填 49 条三通道分类。
- ⚠️ **口径**：三通道/静默/错位只能算 49（要报错证据），342 只能算描述统计（不能给没跑出来的编报错形态）。
  LLM 诊断/修复仍为旧 80 合成集数字（45%/52.5%/69.6%），需用户本地跑 DeepSeek-V4 重算。
- **下一步**：第④步后半 = 更新论文 sec:sampling（350→342）+ 正文旧口径→342/49 两层口径 + 接入新图。

### 【2026-10-11 总表已补全 49 条中文错误原因分析】
用户要求把每条 bug 的"具体错在哪"写进总表（不只是三通道标签）。已完成：
- **新增列「错误原因分析」**（第21列）：为 49 条已复现 bug 各写一段中文根因分析（报错是什么、真正病灶在哪、为何难定位/难修复）。
- **修正列17（异常类型）**：统一为新三通道规范标签（pushed-server / silent / caller-exception / single-layer / registration），
  与列19（故障范围标记）完全一致（一致性校验 0 不一致）。旧 `see-raw`/陈旧标签已清除。
- **脚本**：`analysis/backfill_root_cause.py`（写原因分析 + 统一列17）。总表现 21 列，49 条已复现全填充。
- **列19（三通道标记）分布**：推到Server 7 / 静默 11 / 调用方裸抛 3 / 单层掩蔽 17 / 单层正确 8 / 注册期 3。
