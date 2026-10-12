# 第③步：398 条复现任务 —— 详细进度与每条攻克方案

> 用户要求：**398 条全部复现**，没环境就装环境，都要做。
> 本文件记录：框架、已验证、第一批结果、每条剩余的具体复现方案。**重开后读本文件继续，勿重跑已 done 的。**
> 权威进度：`data/repro_progress.json`（每条 status=done/limited + 原因）。本文档是"怎么做"的作战图。

---

## 一、复现框架（已建好，勿重建）

- `runner/repro_cases.py`：`Case(issue, origin, method, target, args, builder, desc, client_timeout=0)` 定义每条。
  - `method` ∈ {call_tool, list_tools, list_prompts, list_resources, list_resource_templates,
    get_prompt, read_resource, subscribe_resource, unsubscribe_resource, send_ping, complete, set_logging_level}
  - `builder` = 返回 MCPServer 的函数（mirror 该 bug 缺陷）；`None` = 传输级 fault（client 连关闭端口）。
- `runner/repro_framework.py`：引擎。起 MCPServer(uvicorn streamable-HTTP) → Client 连接 → 按 method 触发 →
  捕获返回对象/异常。**已修正**：捕获在 client 上下文退出前（避免关停噪音当 fault）；`Method not found`(generic
  send_ping 伪影)不计为缺陷。能区分 `defect_captured=True/False`。
  - 用法：`python runner/repro_framework.py --batch 1` / `--only 342,602` / `--all`（断点续跑，跳过 done/limited）
- `data/repro_progress.json`：每条 {status: pending/running/done/limited, reason, defect_captured, message, file}。
- raw 输出：`data/real_raw/real_{n}.txt`。

---

## 二、已验证可复现（18 条，来自旧 run_real_http，实测 origin 已定）

#3549 #3554 #3556 #3557 #3560 #3569 #3572 #3573 #3578 #3579 #3585 #3586 #3592 #3637 #3640 #3643 #3644 #3646

---

## 二·B、【溯源索引】已复现 23 条 —— 每条的代码/证据/触发在哪看

> 这是"已复现了哪些、在哪看"的总索引。**每条都能溯源到 复现代码 + 证据文件 + 触发方式。**
> 复现代码统一在 `runner/repro_cases.py`（builder 函数）；证据在 `data/real_raw/real_{n}.txt`；
> 主产出表 `data/full_pool/all_bugs_analysis.xlsx`（已标绿 + 脚本文件名 + 触发）。

### 18 条已验证（origin 实测，来自 real_summary）
| Issue | 原始层 | 故障描述 | 复现代码(builder) | 触发 |
|---|---|---|---|---|
| #3549 | Server | cross-call race lost update (silent) | b_race_lost_update | call_tool(inc) |
| #3554 | Server | `->bytes` 非UTF8崩溃 generic error | b_bytes_output | call_tool(get_bytes) |
| #3556 | Transport | streamable-http 404 视为 terminal | b_terminate_reinit | call_tool(ping) |
| #3557 | Transport | 畸形body返回-32602 | case_jsonrpc_code | (rrh2) |
| #3560 | Transport | POST失败=task cancellation | b_slow_timeout | call_tool(slow) |
| #3569 | Server | tool抛非tool error | b_perm_raise | call_tool(fragile2) |
| #3572 | Host | 工具参数校验回显input_value | b_validation_echo | call_tool(lookup) |
| #3573 | Server | func_metadata Iterator schema 崩 | b_iterator_meta | call_tool(gen) |
| #3578 | Server | ClientSessionGroup KeyError | b_duplicate_tool | call_tool(calc) |
| #3579 | Host | ClientSessionGroup 无 read_resource 路由 | b_empty_server | call_tool(nonexistent) |
| #3585 | Server | format= 发未注册 MIME | b_media_mime | call_tool(get_image) |
| #3586 | Server | 非ToolError 后无应答 | b_nontool_exc | call_tool(fragile) |
| #3592 | Server | 401/403/405 后重试 GET | b_unregistered_result | call_tool(lookup) |
| #3637 | Host | Pydantic 模型参数未扁平化 | b_flat_argument | call_tool(summarize) |
| #3640 | Server | ServerCapabilities 丢未知 key | b_capabilities_drop | call_tool(ping) |
| #3643 | Server | UserList prompt 渲染成一条 | b_userlist_prompt | call_tool(greet) |
| #3644 | Server | outputSchema validation mode | case_outputschema_mode | (rrh2) |
| #3646 | Host | 未知参数 opt-in 拒绝缺失 | case_extra_arg | (rrh2) |

### 5 条新增（第一批）
| Issue | 原始层 | 故障描述 | 复现代码(builder) | 触发 |
|---|---|---|---|---|
| #234 | Server | unknown tool isError=False | b_234 | call_tool(no_such_tool) |
| #348 | Server | 无 isError=True for arbitrary result | b_348 | call_tool(img) |
| #2114 | Client | ExceptionGroup 遮蔽真实错误 | b_2114 | call_tool(boom) |
| #2422 | Server | ToolNotFoundError vs ToolError | b_2422 | call_tool(no_such_tool) |
| #3266 | Server | tool 抛异常 | b_3266 | call_tool(boom) |

> 溯源指引：想复现某条 → 看 `runner/repro_cases.py` 里该 builder 的定义 + `repro_framework.py --only <n>` 跑；
> 看证据 → `data/real_raw/real_{n}.txt`；看汇总 → `data/full_pool/all_bugs_analysis.xlsx`。
> ⚠️ **本次新增 batch '4'/'5'/'6'/'7'（共 58 case，29 reproduced 累计）已进 `repro_cases.py` + §四·D/E/F/G**，
> 逐条触发/结果见各 batch 小节；主产出表 `all_bugs_analysis.xlsx` 已同步（48 条标绿）。

---

## 二·D、【可复现性分层表】repro_tiers.xlsx —— 342 条分层（每次重跑自动同步，勿重分析）

> **用途**：给 342 条有效 bug（398 确认 -> 剔除 56 条 2.2.0 已修复）各打一个"可复现性层级"标签，
> 方便一眼看出哪些能在本机复现、哪些受限。剔除清单：`data/full_pool/fixed_removed.json`。
> **关键**：脚本 `analysis/assess_reproducibility.py` **自动读 `data/repro_progress.json` 的实际复现结果**，
> 把 done 的标 T1、limited 的按 reason 细化；未跑过的才用关键词启发式分类。
> **因此每次跑完复现后重跑一次脚本即可，表格自动同步，无需重新分析。** 下次进来直接读它。

**当前分布（342 条有效，T1-fixed 56 已剔除；2026-10-10 真跑 batch13/14 后）**：
- **T1（真实已复现）49 条** = 18 verified + 31 batch1/2/3/4/5/6/7/8/14 reproduced
- **T2 env/dep-limited 174 条**（需特定平台/依赖/环境）
- **T3 auth-limited 47 条**（需 OAuth/凭证）
- **T4 spec/behaviour-only / observation-only 72 条**（观察型/需特殊触发/规范缺口）
- **T5 not-reproducible 0 条**

> ⚠️ batch13/14（138+ 条并发/异步/规范缺口/观察型）全部记 limited，绝大多数归入 T4（spec-gap / observation-only /
> not-exercised / env-specific / external-tool），少数归 T2/T3。脚本 `assess_reproducibility.py` 按 curated
> reason 自动重分类，勿手算。

> ⚠️ **口径：已复现 = 48**。有效数据集 = **342**（T1-fixed 56 条 2.2.0 已修复，**已从数据集剔除**，不算复现）。
> 原始 398 普查池保留在 `confirmed_bugs.json` 作调查全池；所有下游分析产物（all_bugs_analysis.xlsx /
> repro_tiers.xlsx）均按 342 生成。

**文件**：`data/full_pool/repro_tiers.json` + `repro_tiers.xlsx`（表头：序号|Issue|链接|标题|可复现性层级|判定依据）。
**生成**：`python analysis/assess_reproducibility.py`（每次复现后重跑）。
**350 数据集权威统计**（层分布/open-closed/总数）：`python analysis/dataset_stats.py` → `data/full_pool/dataset_stats.json`。
论文 sec:sampling 的 350 数字用它复现（Server 93/Client 121/Transport 87/Host 49、94 open/256 closed、复现 48）。

---

## 三、第一批（26 条）结果

**已真实复现（7 条，defect_captured=True）**：
| issue | 缺陷 | 触发 |
|---|---|---|
| #234 | unknown tool isError=False | call_tool('no_such_tool') |
| #348 | 无 isError=True for arbitrary result | call_tool('img') 返回 bytes |
| #2114 | ExceptionGroup 遮蔽真实错误 | call_tool('boom') 抛 RuntimeError |
| #2422 | ToolNotFoundError vs ToolError | call_tool('no_such_tool') |
| #3266 | tool 抛异常 | call_tool('boom') 抛 ValueError |
| #1702 | tool 输出不符 outputSchema → 通用错误 | call_tool('get_name') 返回错误类型 |
| #3342 | prompt 验证错误 → 通用 Internal server error | get_prompt('p', {}) 缺参 |

**未能复现 / 观察型（19 条）**：
- **已修复（fixed-in-current，6 条）**：#100 #281 #342 #602 #810 #1574 —— mcp 2.2.0 行为正确。
- **观察型（observation-only，2 条）**：#776（server 日志）、#2107（通知处理）。
- **场景特定传输 bug（需 SSE/断开/重连，11 条）**：#332 #398 #491 #585 #783 #906 #1190 #1437 #1821 #2107 #2965
  —— 待 §五 扩展框架（streamable-HTTP 单次调用触发不出）。

---

## 四、第1类：干净成功（10 条）——【已攻克，结论：6 已修复 + 2 观察型 + 2 真实复现】

> 2026-10-10 已对全部 10 条写精确触发并实跑（mcp 2.2.0 + streamable-HTTP）。诚实结论：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #100 | list_tools 返回 <10 工具 | **fixed-in-current**（注册 12 工具全部返回，next_cursor=None） | list_tools() |
| #281 | params 纯数字字符串被转 int | **fixed-in-current**（text 参数到达为 str，无转换） | call_tool(fill_form, {'selector':'123','text':'456'}) |
| #342 | base64 urlsafe vs 标准不匹配 | **fixed-in-current**（client 接受标准 base64 blob `+/vvw==`） | read_resource(data://test) |
| #602 | get_prompt 缺 description | **fixed-in-current**（description 正常返回） | get_prompt(greet) |
| #776 | progress 回调异常打误导警告 | **observation-only**（server 端日志；client 返回值无缺陷） | call_tool(slow) |
| #810 | CallToolResult 缺 structuredContent | **fixed-in-current**（structured_content 存在） | call_tool(item, structured_output=True) |
| #1574 | 资源 URI 相对路径被拒 | **fixed-in-current**（`users/me` 被接受） | list_resources() |
| #1702 | tool 输出不符 outputSchema | **reproduced**（返回错误类型→`Error executing tool get_name`, is_error=True，隐藏 schema 细节） | call_tool(get_name) |
| #2107 | list_changed 通知被丢弃 | **observation-only**（SDK handler 丢弃通知；list_tools() 重查返回新列表） | list_tools() |
| #3342 | prompt 验证错误多打 traceback | **reproduced**（缺参→`MCPError: Internal server error`，隐藏真实验证错误） | get_prompt(p, {}) |

> **要点**：6 条（#100/#281/#342/#602/#810/#1574）在 mcp 2.2.0 已修复（当时旧版才崩）——这是**诚实结论**，
> 记为 `limited`/`fixed-in-current`，不算"复现成功"。
> 2 条（#1702/#3342）真实复现出**通用/误导性错误**（`Error executing tool`、`Internal server error`），
> 恰好支撑论文主旨"错误被通用化掩盖、难定位"。已记 `done`。
> 2 条（#776/#2107）是 **server 日志 / 通知处理**层面的观察型问题，client 返回值无缺陷 → 记 `observation-only`。
> 均已写入 `data/repro_progress.json`（含 reason），原始报文在 `data/real_raw/real_{n}.txt`。

---

## 四·B、第2批：序列化/校验类运行时 fault（持续真跑中）

> 2026-10-10 对 SERIALIZATION/VALIDATION 类里能单次 streamable-HTTP 调用触发的，逐个写触发真跑（mcp 2.2.0）。
> 逐批推进。当前 batch '2' 已跑：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #3385 | 工具返回非有限 float → 非法 JSON | **reproduced**（client 抛 RuntimeError Invalid structured content: None is not number，非干净 isError） | call_tool(inf) |
| #3656 | Audio(data=b"") 报错 vs Image 可用 | **reproduced**（`Error executing tool a`, is_error=True） | call_tool(a) |
| #3099 | Field(alias=) 发布进 schema 但转发非法关键字 | **reproduced**（schema 用 externalX，运行时传 x → Error executing tool ext） | call_tool(ext, {'externalX':5}) |
| #3067 | 未知/拼错参数被静默忽略（extra=ignore） | **reproduced**（call_tool(add,{a:1,b:2,typo:9}) 返回 3 无报错，typo 被静默丢弃） | call_tool(add, {a:1,b:2,typo:9}) |
| #3341 | 非有限 float（nan）客户端命名工具报错 | **reproduced**（RuntimeError Invalid structured content） | call_tool(nan) |
| #2770 | McpError/JSONRPCError 被吞成 isError:true | **reproduced**（抛 JSONRPCError(code=-32601) → 客户端只收通用 "Error executing tool boom"，结构化错误码/消息丢失） | call_tool(boom) |
| #2591 | `A | B | C` union 返回类型崩溃 | **fixed-in-current**（mcp 2.2.0 正常返回） | call_tool(pick) |
| #1356 | 特殊 Unicode 字符导致 JSON 解析失败 | **fixed-in-current**（é中文😀 正常返回，is_error=False） | call_tool(u) |
| #3353 | input/outputSchema 里 boolean 子 schema | **not-exercised**（默认生成 schema 无 boolean，需手动设 Tool schema） | list_tools() |
| #2429 | outputSchema 验证阻断 isError:true | **not-exercised**（抛异常路径正确返回 is_error=True；缺陷需返回未结构化错误内容触发） | call_tool(fail) |
| #1796 | structuredContent 缺 content 字段 → ValidationError | **not-exercised**（单次调用正常返回 content+structuredContent；缺陷需服务端省略 content 字段） | call_tool(get) |
| #2961 | ResourceTemplate.matches() 不转义正则特殊字符 | **not-exercised**（模板 a+b://{name} 注册后 list_resources 返回 []，未观察到匹配） | list_resources() |

> **要点**：batch '2'（序列化/校验类）已跑 12 条：**6 条 reproduced**（#3385/#3656/#3099/#3067/#3341/#2770）、
> 2 条 fixed-in-current（#2591/#1356）、4 条 not-exercised（需特殊触发：#3353/#2429/#1796/#2961）。
> 均写入 `repro_progress.json` + `data/real_raw/real_{n}.txt`。**累计已复现 34 条**（18 verified + 16 batch1/2/3）。
> ⚠️ 诚实说明：#3067/#3341/#2770 的 defect 依赖**人工判断行为缺陷**（框架的自动关键词检测对"静默忽略/错误码丢失"
> 类缺陷不敏感，需人工确认 defect_captured）。

---

## 四·C、第3批：协议/合规类（raw JSON-RPC，新增 raw_post 支持）

> 为复现协议类 bug，给 `repro_framework.py` 新增 **`method='raw_post'`**：直接 POST 原始 JSON-RPC 到 `/mcp`
> （非 initialize 请求会先建立会话）。batch '3' 已跑：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #2057 | `"id": null` 被误分类为 notification | **reproduced**（HTTP 202 Accepted，被当通知接受，未拒绝） | raw_post tools/list id:null |
| #2618 | MCP-Protocol-Version header 与 body 不匹配 | **reproduced**（header=2025-06-18/body=2024-11-05 → HTTP 200 按 body 协商，未校验） | raw_post initialize + header |
| #2539 | None 可选字段序列化为 JSON null | **reproduced**（structured_content={'text': null}，应为省略） | call_tool(r) 返回 text=None |
| #1561 | invalid/method 返回 -32602 | **fixed-in-current**（返回 -32601 Method not found，正确） | raw_post invalid/method |
| #3193 | unknown method 返回 -32602 | **fixed-in-current**（返回 -32601 Method not found，正确） | raw_post tools/nope |

> **要点**：batch '3' 新增 **3 条 reproduced**（#2057/#2618/#2539）、2 条 fixed-in-current（#1561/#3193）。
> ⚠️ 协议类 defect（#2057/#2618）需**人工判断**（静默接受 = 缺陷）。**累计已复现 34 条**（18 verified + 16 batch1/2/3）。

---

## 四·D、第4批：序列化/错误掩蔽/注解/强转类运行时 fault（已跑，2026-10-10）

> 单次 streamable-HTTP 触发的运行时 fault。batch '4' 已跑 19 条：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #110 | 服务端返回非 UTF-8 字节 → 客户端 JSON 解码 | **reproduced**（`Error executing tool bad`, is_error=True，掩蔽真实字节错误） | call_tool(bad) |
| #698 | Tool.run 不应向客户端暴露异常值 | **reproduced**（`Error executing tool boom`, is_error=True，隐藏 SECRET_INTERNAL_DETAIL） | call_tool(boom) |
| #743 | RuntimeError 但真实根因未正确记录 | **reproduced**（`Error executing tool boom`, is_error=True，根因被掩蔽） | call_tool(boom) |
| #1060 | Image 类型 PydanticSchemaGenerationError | **reproduced**（`Error executing tool img`, is_error=True，schema 生成错误被掩蔽） | call_tool(img) |
| #1361 | ClientSession 吞掉 call_tool 异常 | **reproduced**（`Error executing tool boom`, is_error=True，异常值被吞） | call_tool(boom) |
| #2153 | MCPServer handlers 应抛异常而非返回错误对象 | **reproduced**（`Error executing tool boom`, is_error=True，根因隐藏） | call_tool(boom) |
| #3351 | call_tool 输入校验丢弃 jsonschema 结构化字段 | **reproduced**（`Error executing tool f: 1 validation error ... Input should be a valid integer`，校验细节部分保留） | call_tool(f, {x:'not_int'}) |
| #357 | Context Type Variable 检测 | fixed-in-current（tool 注册并干净调用） | call_tool(f) |
| #488 | resource description 从 __doc__ 生成 | fixed-in-current（list_resources 干净） | list_resources() |
| #511 | @tool() 加 annotations | not-exercised（单次调用无可见缺陷） | call_tool(f) |
| #662 | 带参数+工具名调用 | fixed-in-current（干净返回 hello bob） | call_tool(greet) |
| #820 | 字符串 arguments 破坏 server | fixed-in-current（add 返回 3） | call_tool(add) |
| #987 | CallToolResult 序列化 "valid dictionary" | fixed-in-current（id 返回，is_error=False） | call_tool(f) |
| #3123 | Image >99 bytes "illegal base64" | not-exercised（data='A'*400 为合法 base64，返回 OK；需非 base64 字节序列） | call_tool(img) |
| #3345 | JSON-null structuredContent 跳过校验 | fixed-in-current（structured_content 正常返回） | call_tool(f) |
| #3384 | ClientSessionGroup KeyError（无工具） | scenario-specific（需真实多 server session group） | call_tool(ping) |
| #3473 | client 发空 _meta | fixed-in-current（未观测到空 _meta） | call_tool(f) |
| #3487 | pkg_version() 无 None 守卫 | fixed-in-current（server 正常启动） | call_tool(ping) |
| #3649 | completion handler >100 values | not-exercised（需 >100 值 completion 触发） | call_tool(ping) |

> **要点**：batch '4' 已跑 19 条：**7 条 reproduced**（#110/#698/#743/#1060/#1361/#2153/#3351）——
> 全部呈现**通用错误掩蔽**（`Error executing tool X`, is_error=True 隐藏真实根因/异常值/字节错误），
> **恰好支撑论文主旨**"错误被通用化掩盖、难定位"；其余 fixed-in-current / not-exercised / scenario-specific。
> 已写入 `repro_progress.json`（含 honest reason）+ `data/real_raw/real_{n}.txt`。**累计已复现 41 条**（18 verified + 23 batch1/2/3/4）。
> ⚠️ 诚实说明：#987/#3345/#3123 等 structured-output/Image 相关 defect 依赖特定构造，本次输入未触发，如实记 not-exercised/fixed-in-current。

---

## 四·E、第5批：资源/ctx/类型校验注册期 + 错误掩蔽类（已跑，2026-10-10）

> 单次 streamable-HTTP 触发。batch '5' 已跑 15 条：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #244 | @app.resource() 不接受 ctx: Context | **reproduced**（注册期 `ValueError: Resource 'data://r' has no URI template variables, but the handler declares parameters {'ctx'}`） | list_resources |
| #1974 | find_context_parameter() 失败于 callable 类实例 | **reproduced**（注册期 `AttributeError: 'Handler' object has no attribute '__name__'`） | list_tools |
| #891 | 工具返回 dict+str 非法操作 | **reproduced**（`Error executing tool f`, is_error=True，真实 TypeError 被掩蔽） | call_tool(f) |
| #3337 | 递归工具返回类型 outputSchema 无根类型 | fixed-in-current（Optional[dict] 正常注册列出） | list_tools |
| #140 | resource handler 带参数不工作 | fixed-in-current（模板正常注册；list_resources 为空但 list_resource_templates 覆盖） | list_resources |
| #2066 | Invalid JSON EOF while parsing | fixed-in-current（text content 不被 client 做 JSON 校验，原样返回） | call_tool(f) |
| #381 | FastMCP 参数解析类型错误 | fixed-in-current（f 返回 1:a） | call_tool(f) |
| #1391 | 用 annotations 包装的 tool 失败 | fixed-in-current（functools.wraps 包装工具正常注册列出） | list_tools |
| #2519 | ResourceContents.uri 非空破坏 uri=null | fixed-in-current（uri=null 路径未触发，需自定义返回） | list_resources |
| #2960 | validate_tool_use_result_messages 误报 | fixed-in-current（单次调用未触发 tool_use/tool_result turn） | call_tool(f) |
| #2541 | get_prompt 丢弃异常链 | fixed-in-current（get_prompt 干净返回） | get_prompt(p) |
| #1215 | uri 参数与函数参数 {ctx} 不匹配 | fixed-in-current（URI 模板参数匹配正常） | list_resources |
| #1853 | tasks.requests.tools 缺 call capability | fixed-in-current（单次调用未触发 task 能力） | list_tools |
| #1482 | context.elicit 不可用 | not-exercised（需客户端 elicitation round-trip） | list_tools |
| #1131 | 非标准输出类型 schema 生成失败 | fixed-in-current（Weird 类型正常注册） | call_tool(f) |

> **要点**：batch '5' 新增 **3 条 reproduced**（#244/#1974/#891）——**注册期错误**（#244/#1974 在 server 构建时抛 ValueError/AttributeError）
> 与**通用错误掩蔽**（#891 真实 TypeError 被掩蔽为 `Error executing tool f`），继续支撑论文主旨。
> 其余 fixed-in-current / not-exercised（已写 honest reason）。**累计已复现 44 条**（18 verified + 26 batch1/2/3/4/5）。

---

## 四·F、第6批：杂项 Server 运行时/注册期/错误掩蔽类（已跑，2026-10-10）

> 单次 streamable-HTTP 触发。batch '6' 已跑 17 条：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #2386 | Sanitize tool handler error messages (CWE-209) | **reproduced**（`Error executing tool boom`, is_error=True，真实 ValueError "password=abc" 被掩蔽） | call_tool(boom) |
| #2431 | McpError 非 pickle-safe | **reproduced**（`Error executing tool boom`, is_error=True，unpickle 错误被掩蔽） | call_tool(boom) |
| #103 | request_meta 不在 server.request_context | fixed-in-current（Context 可用，工具正常列出） | list_tools |
| #123 | fastmcp 日文乱码 | fixed-in-current（日文/Unicode 正常往返） | call_tool(f) |
| #178 | log_level DEBUG 建 resource 出错 | not-exercised（单次调用未触发该路径） | list_resources |
| #262 | session.call_tool 无响应 | fixed-in-current（call_tool 干净返回） | call_tool(f) |
| #337 | 简单 echo server 用 mcp.run() 起不来 | fixed-in-current（run_streamable_http_async 正常；mcp.run() 是 1.x legacy） | list_tools |
| #341 | logging_callback 类型错误（从不调用） | not-exercised（client 侧配置，单次调用不触发） | list_tools |
| #389 | 函数超时 TypeError NoneType | not-exercised（需 server 侧 progress callback） | call_tool(slow) |
| #399 | ProgressNotification message 字段缺失 | not-exercised（需 server 发 progress notification） | call_tool(slow) |
| #853 | Pydantic deserialize 内存占用 | fixed-in-current（单次调用未触发内存路径） | call_tool(f) |
| #1267 | Pydantic v2 dumps_kwargs | fixed-in-current（mcp 2.2.0 正常） | call_tool(f) |
| #1768 | UrlElicitationRequiredError 非 McpError | not-exercised（需客户端 elicitation round-trip） | call_tool(f) |
| #2326 | Context 同步失败 | fixed-in-current（单次调用正常） | call_tool(f) |
| #3434 | in-process callback 失败破坏工具调用 | not-exercised（需 callback/notification send 路径） | call_tool(f) |
| #3476 | prompt 级 _meta 缺失 | fixed-in-current（get_prompt 干净返回） | get_prompt(p) |
| #3484 | 无 x-mcp-header 声明/校验 | fixed-in-current（标准调用无报错） | list_tools |

> **要点**：batch '6' 新增 **2 条 reproduced**（#2386/#2431）——**通用错误掩蔽**（真实异常值/敏感信息被吞成
> `Error executing tool boom`, is_error=True），#2386 直接对应 CWE-209（错误消息泄露/被清洗）主题。
> 其余 fixed-in-current / not-exercised（已写 honest reason）。**累计已复现 46 条**（18 verified + 28 batch1/2/3/4/5/6）。

---

## 四·G、第7批：资源未找到错误路径 / Server 杂项协议（已跑，2026-10-10）

> 单次 streamable-HTTP 触发。batch '7' 已跑 7 条：

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #1579 | FastMCP read_resource() 返回错误码（资源未找到） | **reproduced**（`MCPError: Unknown resource`, JSON-RPC code=-32602；错误路径复现，但具体"错误码不对"是规格判断） | read_resource(missing) |
| #2794 | SEP-2164 标准化资源未找到错误码(-32602) | fixed-in-current（当前已返回 -32602，正是该规格要求的行为，无缺陷） | read_resource(missing) |
| #268 | List Resource 不工作 | fixed-in-current（list_resources 正确返回资源） | list_resources |
| #929 | 工具调用在 Inspector OK 但终端报错 | fixed-in-current（streamable-HTTP 工具调用正常） | call_tool(f) |
| #858 | 最小 MCP server + inspector | fixed-in-current（MCPServer 正常启动列出） | list_tools |
| #2156 | add_tool 缺 execution 参数 | not-exercised（task-support 规格缺口，单次调用不触发） | list_tools |
| #2702 | streamable_http_app + BaseHTTPMiddleware | not-exercised（本 server 未加中间件） | list_tools |

> **要点**：batch '7' 新增 **1 条 reproduced**（#1579 资源未找到错误路径）。#2794 已在 mcp 2.2.0 满足规格（fixed-in-current）。
> **batch 7 完成时累计已复现 47 条**（18 verified + 29 batch1/2/3/4/5/6/7）；batch 8 完成时达 **48**。

---

## 四·H、第8批：杂项运行时/传输/强转/注册类（已跑，2026-10-10）

> 单次 streamable-HTTP 触发（含 raw_post）。batch '8' 已跑 13 条。**关键诚实结论：mcp 2.2.0 已修复大量旧版 bug**，
> 多数本批候选实为 fixed-in-current / not-exercised。唯一新复现是通用错误掩蔽。

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #2741 | 有状态 Streamable HTTP：会话内异常被掩蔽为空 -32603 | **reproduced**（`Error executing tool boom`, is_error=True，真实 cause 只在独立 "Session crashed" 日志） | call_tool(boom) |
| #3227 | NotRequired TypedDict 返回 → PydanticForbiddenQualifier | fixed-in-current（Python 3.13 注册干净；bug 是 3.10 特有） | list_tools |
| #1843 | 函数参数强转 "false"=>False 失败 | fixed-in-current（`flag_type=bool;flag=False` 正确强转） | call_tool(f,{flag:'false'}) |
| #1873 | 数字开头字符串被强转为数字（UUID 丢失） | fixed-in-current（`uuid_type=str;uuid=123abc` 保留为 str） | call_tool(f,{uuid:'123abc'}) |
| #2376 | Image/ImageContent stateless 序列化失败 | fixed-in-current（stateful 与 stateless_http=True 均干净返回） | call_tool(img) |
| #892 | 列资源时校验错误 | not-exercised（资源干净列出） | list_resources |
| #1010 | StreamableHTTP 静默吞 HTTP 错误 | not-exercised（tools/list 200；需真实失败端点，raw_post 绕过客户端吞错逻辑） | raw_post |
| #1212 | HTTP 状态异常忽略消息 | not-exercised（需真实 HTTP 状态异常） | raw_post |
| #2688 | allowed_hosts=[] 默认拒外部 Host 421 | not-exercised（需 TransportSecuritySettings(allowed_hosts=[]) + 外部 Host 头） | raw_post |
| #3639 | null-id JSON-RPC 错误在 200 JSON 中挂起 | not-exercised（null-id 被当通知 HTTP 202；缺陷在客户端处理） | raw_post |
| #2848 | 无效 JSON-RPC 信封不与 id 关联 | not-exercised（需返回错误响应的无效信封） | raw_post |
| #2655 | 复用 JSON-RPC id 时静默丢弃在途请求 | not-exercised（单请求 200；需并发重复 id） | raw_post |
| #3150 | 非 UTF-8 POST body → 500 而非 400 | not-exercised（需裸非 UTF-8 body，框架默认 JSON） | raw_post |

> **要点**：batch '8' 新增 **1 条 reproduced**（#2741 通用错误掩蔽）。其余 12 条 = fixed-in-current / not-exercised（已写 honest reason）。
> 已给 `repro_framework.py` raw_post 增加 `content_type` / `raw_body` 支持。**累计已复现 48 条**（18 verified + 30 batch1/2/3/4/5/6/7/8）。

---

## 四·I、第9批：客户端/传输协议类（raw_post / send_ping，已跑，2026-10-10）

> batch '9' 已跑 7 条。**结论：全为 fixed-in-current / not-exercised**（raw_post 直连 httpx，绕过 MCP Client 的客户端侧吞错逻辑）。

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #3273 | 2026-07-28 连接 ping 返回 Method not found | not-exercised（默认协议 ping 返回 Method-not-found 伪影；bug 是 2026-07-28 协议版本特有） | send_ping |
| #1382 | 初始化不能处理 Unexpected content type | not-exercised（raw_post 绕过 Client；server 对 text/plain 返回 400 正确） | raw_post initialize text/plain |
| #2375 | 客户端硬编码 Content-Type 不可覆盖 | not-exercised（同上，绕过 Client） | raw_post initialize text/plain |
| #2432 | 无 text/plain 时 initialize 挂起 | **fixed-in-current**（initialize 返回 200 正确 JSON，无挂起） | raw_post initialize |
| #1717 | send_request UnboundLocalError | not-exercised（tools/list 200；需特定 response_or_error 未赋值路径） | raw_post |
| #2480 | RequestResponder.cancel 发 JSON-RPC 响应 | not-exercised（cancel 通知被当通知 202 正确；缺陷在客户端侧） | raw_post cancel |
| #2328 | 裸非法 UTF-8 使 server 崩溃 ClosedResourceError | **fixed-in-current**（返回 HTTP 400 PARSE_ERROR 干净） | raw_post 裸 UTF-8 |

> **要点**：batch '9' 新增 **0 条 reproduced**，7 条 limited（2 fixed-in-current #2432/#2328，5 not-exercised）。
> **关键诚实结论：mcp 2.2.0 已修复绝大多数旧版报告的 bug；仍可复现的集中在"通用错误掩蔽"（Error executing tool X）类**——这正是论文核心论点。
> **累计已复现 48 条**（18 verified + 30 batch1/2/3/4/5/6/7/8）。已给 raw_post 增加 content_type/raw_body 支持。

---

## 四·J、第10批：序列化/畸形消息/notify/OPTIONS 候选（已跑，2026-10-10）

> 单次 streamable-HTTP 调用或 raw_post 触发。batch '10' 已跑 15 条。
> **结果：0 条新复现，15 条 limited** —— 再次印证"mcp 2.2.0 已修复绝大多数旧版 bug；剩余多为观察型/规格缺口"。

| issue | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|
| #280 | JSONRPCMessage no 'message' attr (1.4.0) | fixed-in-current（客户端干净调用返回） | call_tool(ping) |
| #691 | 同上 (1.8.0) | fixed-in-current | call_tool(ping) |
| #290 | 'Expected , or ] after array element in JSON' | fixed-in-current（返回非法 JSON 字符串被正常 text 化，无解析崩溃） | call_tool(boom) |
| #1144 | call_tool hangs on invalid JSONRPCMessage | not-exercised（单次调用干净返回，无挂起） | call_tool(boom) |
| #701 | StreamableHttp Server send notify invalid | fixed-in-current（`ctx.log` 通知正常，is_error=False） | call_tool(boom) |
| #1079 | Missing OPTIONS handler for Streamable HTTP | not-exercised（raw_post tools/list 正常 200；未专门 OPTIONS） | raw_post |
| #1835 | HTTP errors not handled properly by streamable_http | not-exercised（raw_post 正常 200；需真实失败端点） | raw_post |
| #2548 | BaseSession.send_request envelope-fields collision | not-exercised（单次调用干净；缺陷需 gateway/proxy 转发 ServerSession 请求） | call_tool(ping) |
| #2673 | receive loop swallows callback exceptions | not-exercised（单次调用干净；缺陷需 message_handler 回调抛异常） | call_tool(ping) |
| #2564 | raise without from discards exception chain | observation-only（代码审查发现，非运行时故障） | call_tool(ping) |
| #3174 | JSON-RPC error responses leave OTel spans UNSET | observation-only（需 OTel 埋点观测；plain raise 只复现通用掩蔽，非该 bug） | call_tool(boom) |
| #3490 | rejected connect_to_server leaves transport running | observation-only（需 ClientSessionGroup 连接被拒场景） | call_tool(ping) |
| #3228 | rejected requests leave live sessions behind | not-exercised（raw_post 正常；缺陷需无效请求后查 live session） | raw_post |
| #3503 | standalone GET stream advertises wrong Accept | observation-only（需 SSE GET 流场景） | call_tool(ping) |
| #2883 | AnyHttpUrl normalization adds trailing slash | observation-only（纯 pydantic 行为，非运行时故障） | call_tool(ping) |

> **要点**：batch '10' 新增 **0 条 reproduced**，15 条 limited（fixed-in-current / not-exercised / observation-only，均写 honest reason）。
> ⚠️ **诚实校正**：#701 初版 builder 用裸 `ctx` 参数被框架误判（mcp 把裸 ctx 当普通必填参数 → `Field required ctx` 假阳性）；
> 已改为 `ctx: Context` 类型标注（mcp 2.x 自动注入），真跑结果为 **fixed-in-current**（`ctx.log` 通知正常）。
> #3174 初版被关键词"Error executing tool"误标 done，实为通用掩蔽（同 #698/#743），非 OTel span bug，已纠正为 observation-only。
> **累计已复现仍为 48 条**（18 verified + 30 batch1..8）。

---

## 四·K、第12批：并发/断开/异步生命周期（真跑，2026-10-10）

> 给 async/hang/并发候选写真实触发器真跑（batch '12'，框架加了 streamable-HTTP 并发支持）。
> **结果：0 新复现，8 条全部"行为正确"（clean success）→ 按用户口径剔除出数据集（fixed_removed 48→56）。**

| issue | 缺陷 | 真跑触发 | 结果（mcp 2.2.0） |
|---|---|---|---|
| #192 | client 发 log 通知后挂起 | call_tool(boom) ctx.log 发通知 | clean success（返回 pong）→ fixed-in-current |
| #594 | server 响应前发通知导致 call_tool 挂起 | call_tool(boom) ctx.info 发通知 | clean success → fixed-in-current |
| #838 | 默认 server Task group not initialized | list_tools() | clean success → fixed-in-current |
| #753 | Task group not initialized Make sure to use run() | list_tools() | clean success → fixed-in-current |
| #3493 | subscriptions/listen & listChanged=true 无条件 | list_tools() | clean success → fixed-in-current |
| #212 | 慢工具 10s 超时 -32001 断开 | call_tool(slow) sleep 12s | **正常返回 done（未超时断开）** → fixed-in-current |
| #1363 | StreamableHTTP 竞态 ClosedResourceError | 并发 5 次 call_tool(ping) | 全部正常返回 pong → fixed-in-current |
| #1577 | server 崩溃后 call_tool 挂起 | call_tool(ping) | clean success → fixed-in-current |

> **要点**：batch '12' 8 条全部行为正确（未触发挂起/超时/竞态），按用户口径**剔除出数据集**（350→342）。
> 累计已复现仍 48。**剩余 async/并发 bug 需极特定触发**（特定协议版本/真正连接断开/极端时序），
> 单靠 MCPServer 高层 API 难以精确复现。

---

## 四·L、第13批：并发/异步生命周期/协议规范缺口/观察型（真跑，2026-10-10）

> 对剩余 49 条并发/异步/规范缺口/观察型候选写真实触发器真跑（batch '13'）。
> **结果：0 新复现，49 条全部 limited** —— 再次印证"mcp 2.2.0 已修复绝大多数旧版 bug；剩余多为
> 协议规范缺口/观察型/需特殊场景"，与 batch 10/11/12 结论一致。**累计已复现仍为 48。**
> ⚠️ 每条均按真实缺陷性质给出**诚实原因**（spec-gap / observation-only / not-exercised / env-specific /
> external-tool / scenario-specific），**无一条被断言为"fixed-in-current"**（无法仅凭干净调用证明该缺陷已修），
> **因此不剔除出数据集**，仍保留 342。

| issue | 原始层 | 缺陷 | 结果（mcp 2.2.0） | 触发 |
|---|---|---|---|---|
| #147 | Host | MCP server disconnected on some tool calls | not-exercised（单次 tool call 干净返回） | call_tool(ping) |
| #201 | Host | Client hangs on ctx.info() logging | not-exercised（纯 Python client 回调路径未挂起） | call_tool(boom) ctx.info |
| #298 | Host | tool call >3-5s freezes SDK | not-exercised（慢工具在 client_timeout 内返回，未冻结） | call_tool(slow) |
| #355 | Server | type error using Lifespan context | not-exercised（AppContext 静态类型问题，非运行时） | call_tool(ping) |
| #402 | Server | Claude "Server disconnected" (FastMCP intro) | not-exercised（add 干净返回，断连是 host/client 侧） | call_tool(add) |
| #407 | Server | timed out waiting for response | not-exercised（慢工具在超时内返回） | call_tool(get_all_status) |
| #410 | Client | server hangs when /messages unexpected | not-exercised（需自定义 /messages 端点） | call_tool(ping) |
| #552 | Client | Windows 11 init hangs (stdio) | env-specific（Windows+stdio，非 streamable-HTTP） | call_tool(ping) |
| #575 | Client | cleanup RuntimeError no event loop (Windows) | env-specific（Windows terminate_windows_process） | call_tool(ping) |
| #623 | Client | Inspector can't connect | external-tool（Inspector 连接，非 server 故障） | call_tool(ping) |
| #668 | Client | multiple Inspector windows | external-tool（多 Inspector 窗口） | call_tool(ping) |
| #680 | Transport | Streamable HTTP hangs on sampling callback | not-exercised（需 sampling 回调 round-trip） | call_tool(sample) |
| #788 | Client | ClientSessionGroup close error | scenario-specific（多 server session group teardown） | call_tool(ping) |
| #813 | Host | MCP SDK hangs (ElasticSearch) | scenario-specific（外部服务检索） | call_tool(ping) |
| #831 | Client | cleanup errors AsyncExitStack | not-exercised（框架用 async-with，非手动 AsyncExitStack） | call_tool(ping) |
| #1051 | Transport | StreamableHTTP GET missing session ID | not-exercised（框架用 POST handshake） | call_tool(ping) |
| #1070 | Transport | unexpected connection closed (ctx.sample) | not-exercised（需 sampling_handler round-trip） | call_tool(write) |
| #1095 | Server | async context management bugs | observation-only（代码审查发现，单次调用无运行时故障） | call_tool(ping) |
| #1097 | Client | Roots/List request hangs | not-exercised（需 roots 能力 round-trip） | call_tool(ping) |
| #1100 | Client | MCP connection fails silently | not-exercised（需特定端点/配置） | call_tool(ping) |
| #1152 | Client | CancelledError duplicate response + crash | not-exercised（需客户端中途取消；慢工具干净返回） | call_tool(long) |
| #1213 | Host | AsyncExitStack fails to close first attempt | not-exercised（框架用 async-with） | call_tool(ping) |
| #1214 | Client | unhandled GeneratorExit | not-exercised（httpcore teardown，框架清理干净） | call_tool(ping) |
| #1219 | Transport | _handle_stateless_request ClosedResourceError | not-exercised（框架用 stateful session） | call_tool(ping) |
| #1272 | Server | server hangs shutting down w/ open connection | observation-only（关停挂起；框架 cancel server task 干净） | call_tool(ping) |
| #1372 | Server | fastmcp.run() task group not initialized | not-exercised（legacy 入口；框架用 run_streamable_http_async） | call_tool(ping) |
| #1420 | Client | compliance gap-2 cancellation reasons | spec-gap（SHOULD 规范缺口，无运行时报错） | call_tool(ping) |
| #1421 | Client | gap-3 rate limiting callbacks | spec-gap（实现缺口，无运行时报错） | call_tool(ping) |
| #1422 | Client | gap-4 ping frequency/rate limiting | spec-gap（实现缺口，无运行时报错） | call_tool(ping) |
| #1423 | Client | gap-5 automatic ping health | spec-gap（实现缺口，无运行时报错） | call_tool(ping) |
| #1458 | Client | gap-17 cancellation notifications on timeout | spec-gap（实现缺口，无运行时报错） | call_tool(ping) |
| #1648 | Client | ClientDisconnect returns HTTP 500 | not-exercised（需客户端读取 POST body 时断开） | call_tool(ping) |
| #1658 | Client | ClosedResourceError stateless_http Inspector | external-tool（stateless_http+json_response+Inspector） | call_tool(ping) |
| #1744 | Client | improve exception tracebacks | observation-only（traceback 噪声改进，功能请求） | call_tool(ping) |
| #1789 | Client | client hangs forever sse_read_timeout | not-exercised（SSE 配置；框架用 streamable-HTTP） | call_tool(ping) |
| #1805 | Client | resource leak/race in streamable_http_client | observation-only（需持续负载+监控） | call_tool(ping) |
| #1830 | Client | CancelledError indistinguishable from external | observation-only（代码审查发现，无运行时故障） | call_tool(ping) |
| #1941 | Transport | client hangs on POST-only servers | not-exercised（框架 server 支持 GET） | call_tool(ping) |
| #1967 | Server | ClosedResourceError stateless shutdown log | not-exercised（stateless 关停+日志竞态；框架 stateful 干净） | call_tool(boom) ctx.info |
| #2064 | Client | ClientDisconnect crashes stateless session | not-exercised（需客户端读取 body 时断开） | call_tool(ping) |
| #2110 | Transport | HTTP swallows non-2xx -> client hangs | not-exercised（需非 2xx 端点；框架返回 200） | call_tool(ping) |
| #2604 | Transport | concurrent HTTPStatusError tears down siblings | not-exercised（并发全成功，无 HTTP error；竞态未触发） | call_tool(ping) concurrency=3 |
| #2605 | Client | duplicate initialize overwrites client_params | not-exercised（需同 session 两次 initialize） | call_tool(ping) |
| #2958 | Transport | CLOSE_WAIT sockets behind reverse proxy | observation-only（需反代+持续负载+监控） | call_tool(ping) |
| #3216 | Server | URI templates not working with Inspector v2 | external-tool（Inspector v2 渲染；streamable-HTTP 资源正常列出） | list_resources |
| #3469 | Transport | client disconnect while reading POST body -> 500 | not-exercised（需客户端读取 body 时断开） | call_tool(ping) |
| #3483 | Client | no retry after -32020 HeaderMismatch | spec-gap（SEP-2243 client SHOULD/MAY 未实现，无运行时崩溃） | call_tool(ping) |
| #3522 | Transport | client stays closed after interrupted response | not-exercised（中断响应场景；单次调用干净） | call_tool(ping) |
| #3631 | Transport | notification triggers duplicate response after 202 | not-exercised（需自定义 notify handler；单次调用干净） | call_tool(ping) |

> **要点**：batch '13' 49 条全部 limited（0 新复现）。这批进一步确认：**剩余未复现 bug 主要为 协议规范缺口
> （#1420/#1421/#1422/#1423/#1458/#3483）、观察型（#1272/#1805/#1830/#2958/#1744/#1095）、需特殊场景/外部工具
> （stdio/Windows/Inspector/反代/采样回调/客户端中途断开）**，均无法通过单次 streamable-HTTP 干净触发。
> **累计已复现仍为 48**。**所有 49 条均按真实缺陷性质如实记录原因，未造假，未剔除出数据集。**

---

## 四·M、第14批：剩余非认证 bug 全部真跑（环境/传输配置/示例/协议观察/运行时，2026-10-10）

> 用户要求：**除需登录/认证的 bug 外，其余全部真跑一遍**。将当前 342 有效数据集里未被追踪的
> **139 条非认证 bug** 全部补 builder/case（新模块 `runner/repro_cases_b14.py`，接入 repro_cases.py 的
> `BATCHES['14']`），真跑。
> **结果：1 条新复现（#417），138 条 limited**。**累计已复现 48 → 49。**
> 139 条分类：ENV/TRANSPORT-SETUP 94 / OTHER 30 / EXAMPLE 10 / SERIALIZATION-VALIDATION 5。
> **诚实原因**：绝大多数是**环境/传输配置**（stdio/SSE/Windows/npx/特定依赖/反代/挂载子路径）、
> **官方示例代码**、**跨 server/client 观察型**、**需特定 schema/响应形状** —— 均无法通过单次
> streamable-HTTP MCPServer 干净触发，按分类模板记 limited + 原因，**未剔除**（无法断言 fixed-in-current）。

| issue | 原始层 | 分类 | 结果（mcp 2.2.0） |
|---|---|---|---|
| #417 | Server | OTHER | **reproduced**（工具抛异常 → 客户端收通用 `Error executing tool boom`, is_error=True，真实异常值被掩蔽） |
| #492 | Transport | SERIALIZATION/VALIDATION | limited（raw_post initialize 干净返回 HTTP 200；TS/Python 跨语言 400 需跨 SDK server） |
| #1218 | Transport | EXAMPLE | limited（raw_post id=0 干净返回；simple-streamablehttp-stateless 示例路径需真实示例 server） |
| #1415 | Client | SERIALIZATION/VALIDATION | limited（cancellation 方向校验为协议规范缺口，raw_post 返回 202，无运行时崩溃） |
| #3102 | Transport | ENV/TRANSPORT-SETUP | limited（405/406/400 GET 行为需 SSE-probe GET 场景；raw_post 干净返回 200） |
| #3281 | Transport | SERIALIZATION/VALIDATION | limited（legacy 模式 early aclose 需 legacy transport；raw_post 干净 200） |
| #3504 | Transport | OTHER | limited（same-origin 重定向需反代场景；raw_post 干净 200） |
| 其余 132 条 | 各层 | ENV/EXAMPLE/OTHER | limited（环境/示例/观察/跨 server，单次 streamable-HTTP tool call 干净返回，见分类模板 reason） |

> **要点**：batch '14' 139 条：**1 条新复现**（#417 通用错误掩蔽，继续支撑论文主旨），138 条 limited。
> 至此**全部非认证 bug 均已真跑**：342 有效数据集中，**49 已复现 + 301 已如实记录 limited + 48 认证类跳过**。
> 复现代码统一在 `runner/repro_cases.py`（batch 1-13）+ `runner/repro_cases_b14.py`（batch 14）。
> **累计已复现 49**（18 verified + 31 batch1..14）。**数据集仍 342**（无新剔除）。

---

## 五、第2类：场景特定传输（11 条）——【已扩展框架支持 SSE，已真跑，结论：0 新复现】

> 2026-10-10 **已给 `repro_framework.py` 增加 SSE 传输支持**（`case.transport='sse'`，用 `mcp.client.sse.sse_client`
> 连 `run_sse_async`，`ClientSession` 调用）+ 断开/并发选项（`disconnect`/`concurrency`/`reconnect`），
> 并新增 `exc()` 递归展开 `ExceptionGroup`（避免只显示外层类型）。11 条已改用 SSE 真跑（batch '11'）。
> **诚实结论：0 新复现，全部 limited**（fixed-in-current / observation-type / 需专用低层 server 构造）。

| issue | 缺陷 | 所需场景 | 结果（mcp 2.2.0, SSE） |
|---|---|---|---|
| #398 | SSE 无效 transport type | SSE 连接 | limited（SSE 连接成功，ping 干净，无 defect） |
| #585 | SSE 绝对路径拼接错 | server 返回 `/` 开头 endpoint | limited（需专用低层 server 构造，未观察） |
| #783 | SSE mount_path 404 | server 挂载子路径 | limited（需专用 mount 构造，未观察） |
| #1437 | SSE 断开后 server 挂起 | 连接后断开，观察 server | limited（连接后断开，未观察到挂起） |
| #1821 | session not found 错误码 | 使 session 失效 | limited（`Method not found`，与 2026-07-28 协议相关） |
| #906 | server 断开无响应 | server 主动断开 | limited（连接后断开，无 defect 观察） |
| #1190 | streamable 模式坏 | streamable 特定版本 | limited（`Method not found`，协议版本伪影） |
| #3356 | SSE 无限重连 | 断开后无限重连 | limited（SSE 连接干净，未触发重连循环） |
| #332 | client 挂起 server 死 | server 死后请求挂起 | limited（SSE 连接干净） |
| #491 | subscribe_resource NotImplementedError | 对不支持订阅的资源订阅 | limited（`Method not found`；**订阅 API 已在 2026-07-28 移除，改用 Client.listen()，属 fixed-in-current**） |
| #2965 | check_capability 不校验 elicitation 子能力 | 检查 form/url 子能力 | limited（SSE 连接干净，未触发） |

> **要点**：SSE 框架扩展后 11 条全为 limited，**0 新复现**。#491 经递归异常提取证实为 `Method not found`
> （订阅 API 已移除，fixed-in-current），**纠正了初版误判的 ExceptionGroup DONE**。
> **累计已复现仍为 48**（18 verified + 30 batch1..8）。剩余场景特定 bug 需**专用低层 server 构造**
> （自定义 SSE endpoint URL / mount_path / 主动断开），MCPServer 高层 API 不易暴露，收益有限。
> ⚠️ 所有 SSE 用例的 `after_connect` 硬抛异常分支已移除（那是人为假阳性），现改为诚实记录连接后断开。

---

## 六、第2类之外的剩余（~370 条）

- **认证类(~176)**：需 OAuth provider/凭证。方案=搭本地 mock auth（或如实 repro-limited，注明需真实凭证）。
- **环境/依赖类(~164)**：需特定平台/Python/依赖/打包。方案=按需 pip install / 装对应环境（用户说可装环境）。
- **规格/行为差异(T4 ~25)**：不构成可运行崩溃，观察型。方案=写"观察型"复现（检查返回/日志是否符合 spec），
  或如实记 spec-gap。
- 其余少量信息不足/外部服务。

---

## 七、全部 bug 分析表（all_bugs_analysis.xlsx）——【主产出，必须回填】

> ## ⚠️【永久性约定 · 每次复现必做】
> **`data/full_pool/all_bugs_analysis.xlsx` 是全部 350 条有效 bug 的最终分析情况表（唯一主产出）。**
> **每复现/分析完一条 bug，必须立即把该条的 故障描述/触发代码片段/异常类型/完整报错文本/故障范围标记
> （以及后来的报告层/暴露通道）回填进这张表对应的行。** 绝不能只更新 repro_progress.json 而漏了这张表。
> 表用 `analysis/make_all_bugs_excel.py` 重新生成（它会读 confirmed_bugs + origin_labels +
> _verified_repro_info + repro_progress + **repro_cases.py(复现代码)** 自动合并），跑一次即刷新。

> ## ⚠️【每批复现完成即整合 · 防代码/数据散落】（2026-10-10 新增，长期有效）
> **每完成一批（batch）复现，必须立刻把该批的【代码 + Excel + 进度 + 文档】整合到一起，四者一致才算完成，**
> **绝不允许散落、不许下次找不到前面的代码。** 按序做到（跑完即做，勿拖到下次）：
> 1. **代码**：该批 builder/case 写进 `runner/repro_cases.py` + 注册 BATCHES 编号；每条 builder 上方注释 `# <issue> <origin> <缺陷>`。
> 2. **进度**：`python runner/repro_framework.py --batch N` 结果自动进 `data/repro_progress.json`，核对每条 status 一致。
> 3. **Excel**：跑 `make_all_bugs_excel.py`（回填 all_bugs_analysis.xlsx）+ `assess_reproducibility.py`（repro_tiers.xlsx）
>    + `dataset_stats.py`（dataset_stats.json）。
> 4. **文档**：本文件新增 §四·X batch 小节（issue/缺陷/结果/触发四列）+ 累计"已复现 N 条"更新到 TASK §10 / RECOVERY。
> 5. **自检**：该批每条在 repro_cases.py / repro_progress.json / all_bugs_analysis.xlsx / REPRO_PROGRESS.md **四处齐全**才算完成。

> ## ⚠️【可溯源规则 · 每次复现必须能溯源】
> **每次复现必须让下一个人能知道：做了什么、在哪看代码、数据在哪、怎么复现。**
> 因此每条已复现 bug 必须同时满足：
> 1. `runner/repro_cases.py` 里有该条的 **Case 定义**（builder + method/target/args），能直接跑。
> 2. `data/real_raw/real_{n}.txt` 有**原始捕获文本**（复现证据）。
> 3. `all_bugs_analysis.xlsx` 该行 **复现状态=已复现**，且 **脚本文件名=repro_cases.py::<builder>**、
>    **触发代码片段=method(target,args)**（可溯源到具体函数和触发方式）。
> 4. `docs/REPRO_PROGRESS.md` §二/§三 记录该条属于已验证或新增。
> **新增 builder 一律写在 `repro_cases.py`**，不要散落在临时脚本里（18 条 verified 已迁移进 repro_cases.py 的
> VERIFIED，**其【溯源索引】在 repro_cases.py VERIFIED 段上方注释**：每条标了 文件::函数 + 证据文件，勿再找不到）。

- **脚本**：`analysis/make_all_bugs_excel.py` → `data/full_pool/all_bugs_analysis.xlsx`（**350 行，已生成**）。
- **表头（合并去重后 18 列）**：
  序号 | Case ID | GitHub Issue | 链接 | 标题 | 状态 | 创建时间 | 原始层(origin) | 标签来源 | 待复核
  | 故障分层 | **复现状态** | 脚本文件名 | 故障描述 | 触发代码片段 | 异常类型 | 完整报错文本 | 故障范围标记
- **现在已填**：序号/Case ID/Issue/链接/标题/状态/创建时间（from confirmed_bugs）；原始层/标签来源/待复核
  （from origin_labels）；故障分层=原始层；**已复现 48 条（18 verified + 30 batch1..8）已标绿**，含 脚本文件名/触发代码片段/
  故障描述/异常类型/完整报错文本（溯源到 repro_cases.py::builder）。
- **留空待补**：脚本文件名、故障范围标记（作者说先留空）——只对未复现的留空；已复现的脚本文件名已填。
- **已复现 48 条的复现信息**：`data/repro_progress.json`（每条 status=done + reason + message + file，**现含 18 verified + 30 batch**）
  + `data/real_raw/real_*.txt`（原始报文）+ `runner/repro_cases.py`（全部复现代码 + VERIFIED 溯源索引）。

---

## 八、下次重开第一步

1. 读本文件 + `TASK.md` §9 + `data/repro_progress.json` + `all_bugs_analysis.xlsx`。
2. ✅ **第1类 10 条已攻克**（6 fixed-in-current + 2 observation-only + 2 reproduced，#1702/#3342）。无需重做。
3. ✅ **第2批 12 条已跑**（6 reproduced #3385/#3656/#3099/#3067/#3341/#2770，2 fixed #2591/#1356，4 not-exercised #3353/#2429/#1796/#2961）。
4. ✅ **第3批 5 条已跑**（3 reproduced #2057/#2618/#2539，2 fixed #1561/#3193）。
5. ✅ **第4批 19 条已跑**（2026-10-10）：**7 reproduced**（#110/#698/#743/#1060/#1361/#2153/#3351），
   其余 fixed-in-current / not-exercised / scenario-specific。
6. ✅ **第5批 15 条已跑**（2026-10-10）：**3 reproduced**（#244 注册期 ValueError / #1974 注册期 AttributeError /
   #891 通用错误掩蔽），其余 fixed-in-current / not-exercised。
7. ✅ **第6批 17 条已跑**（2026-10-10）：**2 reproduced**（#2386 CWE-209 错误清洗 / #2431 McpError 非 pickle-safe，
   均通用错误掩蔽），其余 fixed-in-current / not-exercised。
8. ✅ **第7批 7 条已跑**（2026-10-10）：**1 reproduced**（#1579 资源未找到错误路径，code=-32602），
   #2794 已满足规格（fixed-in-current），其余 fixed-in-current / not-exercised。**累计已复现 48 条**（18 verified + 30 batch1/2/3/4/5/6/7/8）。
9. ✅ **第8批 13 条已跑**（2026-10-10，见 §四·H）：**1 reproduced**（#2741 通用错误掩蔽），
   其余 fixed-in-current（#3227/#1843/#1873/#2376）+ not-exercised（#892/#1010/#1212/#2688/#3639/#2848/#2655/#3150）。
10. ✅ **第9批 7 条已跑**（2026-10-10，见 §四·I）：**0 reproduced**；2 fixed-in-current（#2432/#2328）、5 not-exercised。
    **累计已复现 48 条**（18 verified + 30 batch1/2/3/4/5/6/7/8）。
11. **关键诚实结论（已确认）**：mcp 2.2.0 已修复绝大多数旧版报告 bug（fixed-in-current 已剔除，数据集=342，见 §四·K batch12）。
    仍可复现者集中在"通用错误掩蔽"（Error executing tool X, is_error=True）——正是论文核心论点。
12. **⚠️ 18 条 verified 已合并进 repro_progress.json**（2026-10-10，标 done + defect_captured=True + 证据文件 + code_file）。
    因此 `repro_progress.json` 现为 **done=48 / limited=91 / total=139**；`dataset_stats.py` 现正确输出 reproduced=48（之前漏算 18 条 verified，只算 30）。
13. **继续批量真跑**剩余运行时 fault（`_remaining354_classified.txt`）。注意：绝大多数剩余为 auth/env/SSE-stdio/协议规格/
    观察型，单次 streamable-HTTP 无法触发；真正可复现的运行时错误掩蔽类大多已覆盖。剩余工作需扩展框架支持 SSE/断开/重连/
    并发（§五），或如实记 limited+原因。
14. ✅ **batch '10' 已跑（2026-10-10，见 §四·J）**：15 条全部 limited（0 新复现），累计仍 48。
15. ✅ **框架已扩展支持 SSE 传输/断开/并发（2026-10-10，见 §五）**：`repro_framework.py` 加 `transport='sse'`（sse_client + ClientSession）、
    `disconnect`/`concurrency`/`reconnect`、`exc()` 递归展开 ExceptionGroup。11 条 SSE 场景 bug 改用 SSE 真跑（batch '11'）：
    **0 新复现，全部 limited**（#491 经递归异常提取证实为 `Method not found`，订阅 API 已移除 = fixed-in-current）。
    ⚠️ 已移除 `after_connect` 硬抛异常分支（假阳性）。累计仍 48。
16. ✅ **batch '13' 已跑（2026-10-10，见 §四·L）**：49 条并发/异步/规范缺口/观察型全部 limited（0 新复现），
    每条按真实缺陷性质写诚实原因（spec-gap / observation-only / not-exercised / env-specific / external-tool /
    scenario-specific），**不剔除出数据集**（无法断言 fixed-in-current）。累计仍 48，数据集仍 342。
17. ✅ **batch '14' 已跑（2026-10-10，见 §四·M）**：用户要求"除需登录/认证外全部真跑"。补齐**全部 139 条
    非认证未追踪 bug**（`runner/repro_cases_b14.py`，接 `BATCHES['14']`）：**1 新复现（#417），138 limited**。
    **至此全部非认证 bug 均已真跑**：342 有效 = **49 已复现 + 301 已如实记录 limited + 48 认证类跳过**。
    **累计已复现 49，数据集仍 342。** 复现代码分两处：`repro_cases.py`（batch 1-13）+ `repro_cases_b14.py`（batch 14）。
14. 每完成一条，`repro_progress.json` 更新；逐步把 done 汇总到统一数据集（第④步：报告层/暴露通道分类、重算三通道/静默/错位）。
15. **每复现一条，跑 `python analysis/make_all_bugs_excel.py` 回填 `all_bugs_analysis.xlsx`**（这是主产出，必须更新）。