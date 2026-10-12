# MCP-IST-Release



---

## 目录结构

```
MCP-IST-Release/
├── README.md            ← 本文件（总说明）
├── PAPER/               ← 论文最新版（投稿/编译用）
│   └── IST_Right_merged/
│       ├── main.tex            (主文件, \input 各 sec_*.tex)
│       ├── sec_intro.tex       (引言)
│       ├── sec_related.tex     (相关工作与背景)
│       ├── sec_method.tex      (研究方法 + 四层故障分类)
│       ├── sec_setup.tex       (实验设置 + 数据集构建)
│       ├── sec_results.tex     (实验结果 RQ1-RQ4)
│       ├── sec_discussion.tex  (讨论 + 结论 + 致谢)
│       ├── cas-common.sty / cas-dc.cls / cas-model2-names.bst / cas-refs.bib
│       └── figs/               (论文引用的 5 张图 + methodology)
├── BENCHMARK/           ← 实验代码 + 数据 + 图 + 文档（49-bug 口径）
│   ├── README.md               (benchmark 说明, 原版)
│   ├── requirements.txt        (依赖)
│   ├── .env.example            (LLM API key 模板)
│   ├── .gitignore
│   ├── analysis/               (49-bug 分析脚本, 32 个)
│   ├── metrics/                (LLM 诊断 / 线索 / 修复, 6 个)
│   ├── runner/                 (复现引擎, 3 个)
│   ├── faultcases/             (复现用例: original 81 + advanced 2)
│   ├── data/full_pool/         (49-bug / 342 核心数据, 28 个)
│   ├── data/real_raw/          (49 条复现 bug 的原始 SDK 输出)
│   ├── data/repro_progress.json(复现进度记录)
│   ├── figs/                   (49-bug 图, 15 张)
│   └── docs/                   (权威数字 + 各分析结果文档, 11 个)
└── PROGRESS/            ← 进度 / 交接文档（供团队或 AI 恢复上下文）
    ├── RECOVERY_README.md      (恢复入口 + 一句话现状)
    ├── QHISTORY.md             (时间线日志)
    └── TASK.md                 (数据重构/复现线进度 + 待办)
```

---

## 最新版口径（49-bug，唯一权威）

| 指标 | 数值 |
|---|---|
| 数据漏斗 | 1,343 纯 issue → 439 关键词 BUG → 398 确认 → **342 有效**（剔除 56 已修复）→ **49 复现 / 293 未复现** |
| 四层起源（49 复现） | Server 36 / Transport 5 / Client 4 / Host 4（非 Server = 13） |
| 三通道（非 Server） | 推到 Server 7 / 静默 3 / 调用方异常 3（**错位 10/13 = 76.9%**） |
| 静默 | 11/49 = **22.4%** |
| 泛化（genericised） | 17/49 = **34.7%** |
| LLM 诊断基线 | 整体 **77.6%**，非 Server **15.4%**（Host/Client 均 0%） |
| Top-K | 整体 79.6%/87.8%/95.9%；非 Server **23.1%/53.8%/84.6%** |
| 诊断线索工具 | 非 Server 15.4% → **23.1%**（+7.7pp）；裸标签对照 0% |
| 修复实验 | **69.6%**（可自动验证子集，有无线索一致） |

权威数字详见 `BENCHMARK/docs/numbers.md`（单一事实来源）。

---

## 最新东西都在哪（速查）

| 内容 | 路径 |
|---|---|
| 论文正文（编译用） | `PAPER/IST_Right_merged/` |
| 权威数字 | `BENCHMARK/docs/numbers.md` |
| 49-bug 实验代码地图/运行顺序 | `BENCHMARK/docs/EXPERIMENTS_49.md` |
| 分析进度（已完成勿重跑） | `BENCHMARK/docs/ANALYSIS_PROGRESS.md` |
| 数据集漏斗表 + 正文 | `BENCHMARK/docs/FUNNEL_TABLE.md` |
| 49 条复现 bug 分类表（Table 4） | `BENCHMARK/docs/REPRO_49_ANALYSIS_DRAFT.md` |
| 49 条难定位原因表 | `BENCHMARK/docs/HARD_TO_LOCALIZE_49.md` |
| 293 未复现·故障性质 | `BENCHMARK/docs/FAULT_NATURE_293.md` |
| Top-K 结果 | `BENCHMARK/docs/TopK_49_RESULTS.md` |
| 诊断线索干预结果 | `BENCHMARK/docs/CLUES_49_RESULTS.md` |
| 四层分类定义 | `BENCHMARK/docs/taxonomy.md` |
| 49-bug 核心数据 | `BENCHMARK/data/full_pool/` |
| 49 条复现原始输出 | `BENCHMARK/data/real_raw/` |
| 49-bug 图 | `BENCHMARK/figs/` |
| 复现/分析/诊断/修复代码 | `BENCHMARK/analysis/`, `metrics/`, `runner/` |

---

## 建议的 GitHub 发布方式

把本目录 `MCP-IST-Release/` 整体作为 GitHub 仓库根（或 `PAPER/` + `BENCHMARK/` 分开两个仓库）。
发布前注意：
- `BENCHMARK/.env`（含 API key）**不要**提交，只提交 `.env.example`（已含在 gitignore）。
- `data/*.xlsx`、`figs/`、`*.zip` 在 `.gitignore` 中已排除，可按需调整。
- 正文中的数据集匿名 repo / DOI 链接（红 TODO）需在发布前补上。

## 中文版（非发布物，供阅读）

最新中文稿在桌面：`C:\Users\kehuichen2\Desktop\IST\中文版审阅.md`（及 `.pdf`）。
它不在本发布目录内，仅作作者/导师阅读用。
