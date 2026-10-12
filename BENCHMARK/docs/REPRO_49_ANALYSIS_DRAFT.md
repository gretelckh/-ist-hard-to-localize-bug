# 【草稿】49 条已复现 bug 的三通道分析 —— 论文表格 + 正文文字

> 数据源：`data/full_pool/active_dataset_analysis.json`（tier_b，49 条，基于运行时证据人工归类）。
> 脚本：`analysis/analyze_active_dataset.py` + `analysis/export_reproduced_49.py`。
> 数据集口径：342 有效 bug（398 确认 − 56 已修复）中的 **49 条可复现子集**。
> 三通道/静默/错位只在此 49 条上计算（需运行时报错证据）；342 只用于描述统计（另表）。

---

## 一、权威数字（写论文用）

| 指标 | 数值 |
|---|---|
| 复现子集 | 49 条真实 bug（全部来自官方 python-sdk，Streamable HTTP 传输） |
| 三通道：推到Server | 7（Host 3 + Client 3 + Transport 1） |
| 三通道：静默 | 11（Server 8 + Host 1 + Client 1 + Transport 1） |
| 三通道：调用方裸抛 | 3（Transport 3） |
| 单层-正确 | 8（Server 源，报在 Server，保留细节） |
| 单层-通用化掩蔽 | 17（Server 源，报在 Server，但真实根因被 `Error executing tool X` 替换） |
| 注册期错误 | 3（Server 构建/注册失败） |
| **非Server错位（mismatch）** | **10/13 = 76.9%**（7 推到Server + 3 调用方） |
| **静默率** | **11/49 = 22.4%** |
| **通用化掩蔽率（消息降质）** | **17/49 = 34.7%**（最强单一机制） |

> ⚠️ 口径说明：
> - 三通道模型只对**非 Server 起源**的 fault 计算"错位"（源 ≠ 报告层）。49 条中非 Server 源 = 13 条。
> - Server 起源（36 条）不构成"错位"，但其中 **17 条**的真实根因被通用化成 `Error executing tool X`
>   （消息降质/掩蔽），这是独立于层错位的另一难定位机制，单独列为"单层-通用化掩蔽"。
> - 静默 11 条跨所有层（is_error=False 逻辑错被吞）。

---

## 二、LaTeX 表格（49 条，按通道分组）

可用 `tabularx` + `booktabs`（宏包已在 main.tex 补齐）。为控制篇幅，下表列出每条
`#issue`、起源层、暴露通道、根因。可整表或按通道拆分。

```latex
\begin{table}[!t]
\centering
\caption{The 49 reproduced real bugs, classified by origin layer and the channel through which
the MCP SDK exposes each fault. Bugs are from the official \texttt{modelcontextprotocol/python-sdk}
issue tracker and reproduced over the Streamable HTTP transport.}
\label{tab:repro49}
\scriptsize
\renewcommand{\arraystretch}{1.03}
\setlength{\tabcolsep}{1.25pt}
\begin{tabularx}{\columnwidth}{@{}l c >{\raggedright\arraybackslash}X@{}}
\toprule
\textbf{Issue} & \textbf{Origin} & \textbf{Exposure channel / root cause} \\
\midrule
\multicolumn{3}{@{}l}{\emph{Pushed-to-Server (7): non-Server fault reported at the Server layer}}\\
\#110 & Client & Server returns non-UTF-8 bytes; client JSON decode error masked as \texttt{Error executing tool bad} \\
\#1361 & Client & \texttt{call\_tool} exception swallowed, re-surfaced as \texttt{Error executing tool boom} \\
\#2114 & Client & \texttt{ExceptionGroup} obscures the real tool error, masked as \texttt{Error executing tool boom} \\
\#2741 & Transport & in-session exception masked as \texttt{Error executing tool boom}; real cause in \texttt{Session crashed} log \\
\#3572 & Host & tool validation error echoes the rejected input; reported as \texttt{Error executing tool lookup} \\
\#3579 & Host & unknown tool requested from a component-less server; reported at Server \\
\#3637 & Host & Pydantic model param not flattened; flat client arg dict rejected at Server \\
\midrule
\multicolumn{3}{@{}l}{\emph{Silent (11): \texttt{is\_error=False}, logical error hidden}}\\
\#2057 & Client & \texttt{id:null} misclassified as notification, accepted (HTTP 202), never rejected \\
\#2539 & Server & optional \texttt{None} field serialised as JSON \texttt{null}; wrong result shape returned \\
\#2618 & Transport & \texttt{MCP-Protocol-Version} header vs body mismatch not validated (HTTP 200) \\
\#3067 & Server & misspelled argument silently dropped (\texttt{extra=ignore}); returns plausible result \\
\#3549 & Server & 20 concurrent calls lose updates (result=1, expected 20); no error flag \\
\#3578 & Server & duplicate tool registration silently keeps the first version \\
\#3585 & Server & unregistered MIME type (\texttt{image/jpg}) emitted without error \\
\#3592 & Server & stale-cache fallback marker returned as success (\texttt{is\_error} mismatch) \\
\#3640 & Server & unknown \texttt{ServerCapabilities} keys silently dropped from advertised capabilities \\
\#3643 & Server & \texttt{UserList} prompt result rendered as one stringified message \\
\#3646 & Host & unknown extra tool argument silently accepted (no opt-in rejection) \\
\midrule
\multicolumn{3}{@{}l}{\emph{Caller-exception (3): raw Python / HTTP exception in calling code}}\\
\#3556 & Transport & client treats 404 (dead session) as terminal; raises \texttt{ExceptionGroup} \\
\#3557 & Transport & malformed body answered with \texttt{-32602} (should be \texttt{-32600}); HTTP 400 \\
\#3560 & Transport & no default timeout; slow tool blocks caller, raises \texttt{ExceptionGroup} \\
\midrule
\multicolumn{3}{@{}l}{\emph{Single-layer, genericised (17): Server-origin, but real cause replaced by \texttt{Error executing tool X}}}\\
\#348 & Server & no way to set \texttt{isError=True} for arbitrary tool result; real error masked \\
\#417 & Server & internal error masked as \texttt{Error executing tool boom} \\
\#698 & Server & tool exception value not revealed; masked as \texttt{Error executing tool boom} \\
\#743 & Server & root cause not logged; masked as \texttt{Error executing tool boom} \\
\#891 & Server & \texttt{dict+str} real \texttt{TypeError} masked as \texttt{Error executing tool f} \\
\#1060 & Server & \texttt{PydanticSchemaGenerationError} for Image masked as \texttt{Error executing tool img} \\
\#1702 & Server & tool output fails outputSchema validation; masked as \texttt{Error executing tool get\_name} \\
\#2153 & Server & handler should raise; masked as \texttt{Error executing tool boom} \\
\#2386 & Server & CWE-209 sensitive value (\texttt{password=abc}) sanitised; real ValueError masked \\
\#2431 & Server & \texttt{McpError} not pickle-safe; masked as \texttt{Error executing tool boom} \\
\#2770 & Server & \texttt{McpError} swallowed as \texttt{isError:true}; masked \\
\#3099 & Server & field alias in schema but invalid Python keyword; masked as \texttt{Error executing tool ext} \\
\#3266 & Server & tool-call exception not logged; masked as \texttt{Error executing tool boom} \\
\#3554 & Server & non-UTF-8 bytes output crashes; masked as \texttt{Error executing tool get\_bytes} \\
\#3569 & Server & non-ToolError surfaced; masked as \texttt{Error executing tool fragile2} \\
\#3586 & Server & non-ToolError surfaced; masked as \texttt{Error executing tool fragile} \\
\#3656 & Server & \texttt{Audio(data=b"")} raises while \texttt{Image} works; masked as \texttt{Error executing tool a} \\
\midrule
\multicolumn{3}{@{}l}{\emph{Single-layer, correct (8): Server-origin, correctly reported (detail retained)}}\\
\#234 & Server & unknown tool returns \texttt{is\_error=True} (wrong \texttt{is\_error} semantics) \\
\#1579 & Server & \texttt{read\_resource} returns wrong error code on not-found \\
\#2422 & Server & \texttt{ToolNotFoundError} vs generic \texttt{ToolError} (wrong error granularity) \\
\#3341 & Server & non-finite float (\texttt{nan}) fails structured-content validation \\
\#3342 & Server & prompt validation error collapsed to \texttt{Internal server error} \\
\#3351 & Server & input-validation discards jsonschema field detail \\
\#3385 & Server & non-finite float (\texttt{inf}) produces invalid JSON in text content \\
\#3644 & Server & outputSchema in validation mode but content serialised by alias (schema mismatch) \\
\midrule
\multicolumn{3}{@{}l}{\emph{Registration-time (3): server cannot build / register a tool}}\\
\#244 & Server & \texttt{@app.resource()} rejects \texttt{ctx: Context}; \texttt{ValueError} at registration \\
\#1974 & Server & \texttt{find\_context\_parameter} fails on callable class; \texttt{AttributeError} at registration \\
\#3573 & Server & \texttt{-> Iterator} annotation raises \texttt{PydanticSchemaGenerationError} at registration \\
\bottomrule
\end{tabularx}
\vspace{0.35em}
\parbox{\columnwidth}{\scriptsize\raggedright
\textit{Note:} ``Issue'' is the GitHub issue number of \texttt{modelcontextprotocol/python-sdk}.
``Origin'' is the layer where the root cause lies. The channel describes how the SDK \emph{exposes}
the fault; the 17 ``genericised'' Server-origin bugs are reported at the correct layer but their real
root cause / error value is replaced by the generic \texttt{Error executing tool X} string.}
\end{table}
```

---

## 三、Results 正文文字（可直接接在 Results 节，替换旧合成集口径）

> ★ 新增小节，建议放在 Results 的 RQ2（机械量化三通道）之前或之内，作为**真实 bug 实证**，
> 与旧合成集对照。以下为英文正文 + 中文注释（符合论文双语注释约定）。

```latex
% ★【中文说明】新增：49 条真实复现 bug 的三通道实证。替代旧"合成 MCP-Fault-20(80 runs)"，
%   作为 RQ1/RQ2 的核心证据。三通道只在此 49 条上计算(需运行时报错)，342 只做描述统计。
% ★[English] New: three-channel evidence over the 49 genuinely reproduced real bugs. Supersedes the
%   synthetic MCP-Fault-20 (80 runs) as the core evidence for RQ1/RQ2. Channels are computed only on
%   these 49 (they have runtime evidence); the 342 is used only for descriptive statistics.
\subsubsection{Three-channel evidence over genuinely reproduced real bugs}

\textcolor{red}{To ground the three-channel model in \emph{real} MCP defects rather than synthetic
scripts, we reproduce 49 bugs directly from the official
\texttt{modelcontextprotocol/python-sdk} issue tracker over the production Streamable HTTP
transport. Each bug is bound to a real issue number, so no fault is fabricated; each is observed at
runtime and its exposure channel is read directly from the SDK's output
(Table~\ref{tab:repro49}).}

\textcolor{red}{Over the 13 non-Server-origin bugs, the model holds strongly:
\textbf{10/13 = 76.9\%} are manifestation-root-cause \emph{mismatched} --- 7 are pushed to the Server
layer (a Host or Client fault re-surfaced as \texttt{Error executing tool X} with
\texttt{is\_error=True}), and 3 surface as a bare caller-side \texttt{ExceptionGroup} / HTTP error.
The remaining 3 non-Server bugs are themselves \emph{silent}, so \textbf{13/13 non-Server real bugs
are not correctly localised at their true origin} --- echoing the synthetic set's 47/48.}

\textcolor{red}{Two further mechanisms are even more revealing. First, \textbf{11/49 = 22.4\%} of the
reproduced bugs are \emph{silent}: the SDK returns a successful status
(\texttt{is\_error=False}) with a plausible result despite a logical error, including a lost update
from 20 concurrent calls (\#3549) and a duplicate tool registration that silently keeps the first
version (\#3578). Second, and most strikingly, \textbf{17/49 = 34.7\%} are \emph{genericised}:
although reported at the correct (Server) layer, the SDK replaces the real root cause / error value
with the generic \texttt{Error executing tool X} string. This \emph{message-degradation} mechanism
is independent of layer mismatch: even when a developer \emph{does} look at the right layer, the
specific cause (a \texttt{TypeError}, a non-pickle-safe \texttt{McpError}, a CWE-209-sensitive
value, an \texttt{Image} schema failure) is stripped away. Finally, 3 bugs fail at
\emph{registration} time, so the server cannot even start.}

\textcolor{red}{\textbf{Finding.} Over 49 genuinely reproduced real bugs, the three-channel model
persists and is sharpened by a new mechanism: 76.9\% of non-Server bugs are layer-mismatched,
22.4\% are silent, and 34.7\% are genericised (the real cause replaced by \texttt{Error executing
tool X}). Real MCP defects are masked even more strongly than the synthetic set, confirming that
fault localisation is hard because the SDK \emph{erases} the true origin --- both at the wrong layer
and by degrading the error message itself.}
```

---

## 四、生成 Excel（用户查看用）

已生成 `data/full_pool/reproduced_49_channels.csv`（49 行：Issue / Origin / Channel / Title / Note）。
可另存为 xlsx。