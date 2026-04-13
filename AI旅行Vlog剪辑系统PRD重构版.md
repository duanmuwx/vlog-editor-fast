# AI 旅行 Vlog 剪辑系统 PRD 重构版

基于原始文档《AI旅行Vlog剪辑系统方案.md》整理。

本文档不替代原方案的愿景描述，而是将其重构为更适合产品评审、研发排期和 MVP 落地的 PRD 形态，重点补足以下三类内容：

- 明确当前方案存在的问题与风险
- 给出适合继续扩写的 PRD 修订版目录
- 提供可直接并入正式 PRD 的章节内容，其中“成功指标”和“版本边界”已落为正式条款

---

## 1. 文档定位

### 1.1 产品目标

打造一款面向个人旅行创作者的本地 AI 剪辑工具。系统以用户游记为叙事主线，结合照片、视频、音频、时间和地点信息，自动生成 2 到 4 分钟、16:9 横屏、轻松 Vlog 风格的旅行成片。

### 1.2 本次重构目标

将“概念方案”推进为“可落地 PRD 基础版”，解决以下问题：

- 产品目标清晰但验收标准不足
- 核心流程完整但缺少失败回退设计
- 自动化愿景明确但交互闭环过于单薄
- 技术模块定义较全但非功能要求不充分

### 1.3 适用范围

- 用于产品评审
- 用于研发拆解和阶段排期
- 用于 MVP 边界确认
- 用于后续补写详细交互稿和技术方案

---

## 2. 问题清单

以下问题按优先级排序，建议作为下一轮文档修订的直接输入。

| 优先级 | 问题 | 当前表现 | 风险 | 修订建议 |
|---|---|---|---|---|
| P0 | 缺少可量化验收标准 | 目标描述偏“可直接分享”“能看”这类主观表述 | 做完后难以判断 MVP 是否达标 | 增加“成功指标”章节，定义处理时长、成片成功率、人工修正率、满意度等指标 |
| P0 | 用户纠错入口过少 | 当前仅保留“高光确认”一个人工节点 | 一旦故事拆段或对齐出错，用户无法低成本修正 | 调整为“三段式轻交互”：故事骨架确认、高光确认、局部再生成 |
| P0 | 对齐策略与输入现实不匹配 | 匹配公式中时间和地点权重高，但元数据缺失是常见情况 | 大量真实素材会在核心链路上降质甚至失配 | 增加“置信度与回退策略”章节，定义无 EXIF、无 GPS、无语音、游记过短时的降级方案 |
| P0 | 本地优先边界不清 | 同时要求本地完成 ASR、视觉理解、LLM、TTS、渲染 | 用户设备差异会导致性能、内存、时长不可控 | 增加“运行环境与性能约束”章节，定义最低配置、推荐配置、CPU/GPU 分档和可选云端能力 |
| P1 | 缺少长任务状态与恢复设计 | 主链路长、步骤多，但没有任务状态机和断点续跑定义 | 一次失败可能导致整条链路重跑，体验差 | 增加“任务编排与失败恢复”章节，定义任务状态、缓存、可重试粒度 |
| P1 | Story-first 原则与低质素材剔除规则冲突 | 文档强调纪念意义，但默认剔除画质差素材 | 成片会偏“好看”而不是“真实旅行” | 增加“纪念性素材保留策略”，引入情绪价值分和保底保留机制 |
| P1 | 再编辑能力不清晰 | 方案强调直接出片，但缺少局部重算入口 | 用户想换旁白、换 BGM、压缩时长时成本高 | 定义“局部再生成”能力，如仅重写旁白、仅重混音、仅重排结构 |
| P1 | 用户输入要求不够成体系 | 仅说明游记、素材、可选元数据，但缺少质量要求 | 输入差异会直接影响可用性 | 增加“输入规范与校验”章节，说明素材数量、时长、游记长度、文件格式要求 |
| P2 | 输出定义偏粗 | 已定义 MP4、字幕、配音、manifest，但缺少预览、日志和诊断输出 | 调试困难，用户不理解失败原因 | 增加“输出产物与诊断文件”章节 |
| P2 | 产品阶段边界尚未完全闭合 | 自用工具和可产品化目标同时存在 | 研发过程中容易摇摆 | 增加“版本边界与决策原则”章节，明确 V1 只服务哪些场景，不服务哪些场景 |

### 2.1 核心判断

当前方案的主要问题不是方向错误，而是还停留在“能力蓝图”层，尚未完全进入“产品规格”层。

最需要补的不是更多模块，而是四类约束：

- 成功如何定义
- 错了如何回退
- 慢了如何降级
- 用户如何局部再生成

---

## 3. 修订版目录

以下目录适合作为下一版正式 PRD 的结构骨架。

## 3.1 文档信息

- 文档名称
- 版本号
- 状态
- 负责人
- 最近更新时间

## 3.2 产品概述

- 产品背景
- 核心目标
- 一句话定位
- 目标用户
- 使用场景

## 3.3 范围定义

- V1 要解决的问题
- V1 不解决的问题
- MVP 边界
- 产品原则

## 3.4 用户与场景

- 目标用户画像
- 核心使用动机
- 典型输入条件
- 典型失败场景

## 3.5 用户旅程

- 创建项目
- 导入游记与素材
- 分析与确认
- 出片与再生成
- 导出与复用

## 3.6 标准旅行项目定义与成功指标

- 标准旅行项目定义
- 北极星指标
- 体验指标
- 质量指标
- 性能指标
- 稳定性指标
- 验收口径说明

## 3.7 输入与输出定义

- 输入文件与格式要求
- 游记输入要求
- 素材输入要求
- 输出文件清单
- 诊断文件清单

## 3.8 功能需求

- 项目管理
- 故事解析
- 素材分析
- 故事与素材对齐
- 高光确认
- 自动成片
- 旁白与字幕
- 音频混合
- 导出与复用

## 3.9 交互闭环设计

- 必选交互节点
- 默认自动化节点
- 局部再生成入口
- 失败提示与人工接管

## 3.10 置信度与回退策略

- 元数据缺失时继续运行，并切换为语义优先的对齐策略
- 游记过短时回退为“时间顺序 + 高光增强”的简化叙事
- 素材不足时使用照片、地点卡、文字卡、旁白过渡等替代呈现单元，不得静默省略高重要度段落
- 对齐低置信时必须显式提示，并在必要时强制进入人工确认；低优先级段落可允许跳过
- 本地算力不足时切换轻量模式，并提示质量与耗时变化

## 3.11 非功能需求

- 本地运行约束
- 性能要求
- 可恢复性
- 隐私与数据安全
- 可观测性

## 3.12 技术实现边界

- 客户端职责
- 本地服务职责
- 模型与第三方能力边界
- 可替换模块说明

## 3.13 版本规划

- V1
- V1.5
- V2

## 3.14 风险与待确认项

- 风险列表
- 依赖项
- 待拍板问题

---

## 4. 关键补充章节

以下章节用于补齐正式 PRD。其中“成功指标”和“版本边界”已按正式条款写定，其余章节仍作为后续扩写草案使用。

## 4.1 产品概述草案

### 4.1.1 产品名称

AI 旅行 Vlog 剪辑系统

### 4.1.2 一句话定位

一个先理解游记，再自动把旅行素材剪成轻松 Vlog 的本地 AI 剪辑工具。

### 4.1.3 目标用户

- 有大量旅行照片和视频，但缺少时间手动剪辑的个人创作者
- 愿意写或已经写过旅行游记、朋友圈长文、备忘记录的用户
- 更在意“旅行回忆表达”而不是专业后期控制的轻创作者

### 4.1.4 核心价值

- 不是按时间机械拼接素材
- 而是把游记转成故事骨架，再用素材完成叙事
- 最终产出可以直接分享的旅行成片，而不是仅供二次编辑的粗剪工程

### 4.1.5 V1 产品原则

- 故事优先于素材质量
- 自动化优先，但必须保留低成本纠错能力
- 本地优先，但必须允许性能降级
- 先做稳定出片，再做复杂风格化

---

## 4.2 标准旅行项目定义与成功指标

### 4.2.1 标准旅行项目定义

除非另有说明，本文档中的成功指标均以“标准旅行项目”为统计口径。

标准旅行项目定义如下：

- 以一次旅行为一个项目单位
- 输入为中文自由文本游记，建议不少于 `150` 字
- 素材总量为 `150-300` 个文件
- 支持照片和视频混合导入
- 原始视频总时长建议不超过 `60` 分钟
- 允许部分素材缺失 `EXIF`、`GPS` 或拍摄时间
- 项目创建时已完成 `BGM` 选择和 `TTS` 音色选择

超出上述规模或明显偏离输入条件的项目，不纳入 V1 的默认验收承诺。

### 4.2.2 北极星指标

V1 的北极星指标定义为：

- 用户能够在一个标准旅行项目中，通过单项目流程生成一条 `2-4` 分钟、`16:9` 横屏、轻松 Vlog 风格的旅行成片
- 用户对最终成片的主观评分达到 `4/5` 及以上

其中，“愿意保留”以用户主观评分是否达到阈值为准，不使用外部分享行为作为验收条件。

### 4.2.3 体验指标

在基础档 CPU 设备上，V1 应满足以下体验指标：

- 从项目创建到得到第一版成片的总耗时目标为 `120` 分钟内
- 用户完成最终出片所需的人工干预步骤不超过 `3` 次
- 用户在第一版成片生成后，无需重新导入素材即可完成至少一次局部再生成并重新出片
- 系统在长任务处理中必须持续展示当前步骤和阶段进度

### 4.2.4 质量指标

V1 的质量指标定义如下：

- 每个高重要度故事段落至少命中 `1` 个可用镜头，或 `1` 个可替代呈现单元
- 可替代呈现单元包括：照片、地点卡、文字卡、旁白过渡
- 成片中重复镜头占比不高于 `15%`
- 旁白连续播报时长原则上不超过 `20` 秒
- 成片中至少保留 `3` 处现场原声时刻，用于增强在场感
- 当某段故事缺少足够素材支撑时，系统必须显式降级处理，不能静默省略

### 4.2.5 性能指标

V1 的性能指标定义如下：

- 标准旅行项目必须能够在基础档 CPU 设备上完整跑通
- 局部再生成不得触发素材分析全量重跑，具体交互约束见 `4.3.5`
- 以下操作必须复用已有中间结果：
  - 仅重写旁白
  - 仅更换 BGM 并重混音
  - 压缩到更短时长
- 失败后重试应支持模块级，而不是项目级重跑

### 4.2.6 稳定性指标

V1 的稳定性指标定义如下：

- 标准旅行项目端到端出片成功率目标不低于 `80%`
- 任一失败都必须定位到具体模块和步骤
- 导出阶段失败时，系统必须保留中间产物和诊断日志，并支持重新导出
- 低置信度结果必须显式提示，不能伪装成高确定性自动结果，相关人工确认节点见 `4.3.3` 和 `4.3.4`

### 4.2.7 验收口径说明

本节指标的默认验收口径如下：

- 验收设备为基础档 CPU 本地机器，不以 GPU 设备作为默认前提
- 验收项目为标准旅行项目，不将超大规模项目纳入 V1 默认承诺
- 主观验收由用户本人进行 `5` 分制评分，达到 `4/5` 及以上视为达标
- 若项目输入明显低于最低建议条件，系统可继续运行，但不计入默认成功率承诺

---

## 4.3 交互闭环设计

### 4.3.1 设计目标

V1 采用“三段式轻交互”闭环。

- 系统必须默认自动完成可稳定自动化的分析与生成步骤
- 用户只在高价值节点介入，并以低成本操作完成纠错
- 每个交互节点都必须支持显式确认、返回上一步和保留中间结果
- 第一版成片之前必须完成故事骨架确认和高光确认
- 第一版成片之后必须提供局部再生成入口，形成至少一次可闭环修正链路

### 4.3.2 必选交互节点与顺序

V1 必须保留以下三个交互节点，并按如下顺序触发：

1. 故事骨架确认
2. 高光确认
3. 局部再生成

各节点的默认顺序与约束如下：

- 游记解析完成后，系统必须进入故事骨架确认，用户确认前不得进入自动成片
- 故事与素材对齐完成后，系统必须进入高光确认，用户确认前不得进入第一版成片生成
- 第一版成片生成完成后，系统必须开放局部再生成入口，且不得要求用户重新导入素材
- 任一节点均应允许用户返回上一步重新确认，并复用已完成的中间结果

### 4.3.3 故事骨架确认

故事骨架确认的正式交互条款如下。

触发条件：

- 系统完成游记解析并生成首版故事段落后，必须进入本节点
- 本节点发生在素材对齐之前，是第一版成片前的必经节点

系统必须展示：

- 自动拆分的故事段落列表
- 每段的摘要信息
- 已识别的时间线索和地点线索
- 每段的高光标记状态
- 低置信度段落的显式提示
- 已标记为“必须保留”的段落状态

用户可执行的操作：

- 合并段落
- 删除段落
- 调整段落顺序
- 调整高光标记
- 标记某段为“必须保留”

确认后系统行为：

- 用户确认后，系统必须固化当前故事骨架版本，并以该版本进入素材对齐
- 用户未完成确认前，系统不得进入高光确认或第一版成片生成
- 用户返回修改故事骨架后，系统必须仅重算受影响的对齐结果，不得要求重新导入素材

默认规则：

- 系统应提供推荐故事骨架版本，用户可直接确认
- 未被用户显式删除的段落默认保留
- 被用户标记为“必须保留”的段落，在后续生成中不得被静默省略

失败与回退：

- 若用户删除或合并后导致故事段落低于最小可用规模，系统必须显式提示成片风险
- 若故事解析整体为低置信度，系统必须明确提示低置信原因，并要求用户在本节点完成修正、确认简化叙事模式或接受推荐骨架后再继续
- 系统必须支持一键恢复推荐骨架版本

### 4.3.4 高光确认

高光确认的正式交互条款如下。

触发条件：

- 故事骨架确认完成且故事与素材对齐结果生成后，系统必须进入本节点
- 本节点发生在第一版成片生成之前，是自动成片前的必经节点

系统必须展示：

- 每个高重要度段落的推荐镜头
- 每个高重要度段落的备选镜头
- 每个推荐镜头的匹配原因或匹配置信度
- 已被用户禁用的镜头状态
- 已被用户标记为“纪念性必保留”的镜头状态
- 无可用视频镜头时的降级呈现方案

用户可执行的操作：

- 接受推荐镜头
- 替换候选镜头
- 标记某镜头为“不要再用”
- 标记某镜头为“纪念性必保留”

确认后系统行为：

- 用户确认后，系统必须冻结当前高光选择结果，并以此生成第一版成片
- 被用户标记为“不要再用”的镜头，在当前项目后续生成中不得再次被自动选用
- 被用户标记为“纪念性必保留”的镜头，系统应优先保留在最终成片中

默认规则：

- 若用户未替换，系统默认采用推荐镜头
- 每个高重要度段落至少应保留 `1` 个可用镜头或 `1` 个可替代呈现单元
- 可替代呈现单元包括照片、地点卡、文字卡和旁白过渡

失败与回退：

- 当高重要度段落未命中可用镜头时，系统必须显式降级为可替代呈现单元，并标注降级原因，不得静默跳过
- 当低置信度匹配占比超过阈值，或任一高重要度段落仅命中低置信候选时，系统必须要求用户在本节点完成确认后再继续
- 低重要度段落在候选镜头持续低置信时，可由用户显式标记为“跳过”
- 用户必须可以返回故事骨架确认重新调整段落，再重新进入本节点

### 4.3.5 局部再生成

局部再生成的正式交互条款如下。

触发条件：

- 第一版成片生成完成后，系统必须开放本节点
- 本节点用于首版成片后的轻量修正，不得要求用户重新导入素材

系统必须提供以下 V1 固定入口：

- 仅重写旁白
- 仅更换 BGM 并重混音
- 压缩到更短时长

各入口的重算范围要求如下：

- 仅重写旁白：允许重算文案、配音、字幕与相关混音，不得重跑素材分析
- 仅更换 BGM 并重混音：允许重算配乐选择、音频混合与导出，不得重跑故事解析和素材分析
- 压缩到更短时长：允许基于既有故事骨架和候选镜头重排节奏，不得重跑素材分析

用户可执行的操作：

- 选择任一固定入口发起局部再生成
- 基于新版本继续发起下一次局部再生成
- 回看上一版成片并选择保留任一版本作为当前结果

确认后系统行为：

- 每次局部再生成都必须生成新的版本记录
- 系统必须复用既有故事骨架、素材索引和镜头候选，避免全链路重跑
- 局部再生成完成后，用户必须能够直接预览并决定是否继续迭代

默认规则：

- 局部再生成默认继承上一版的故事骨架确认结果和高光确认结果
- 若用户未改变入口类型之外的参数，系统不得主动改写其他已确认结果

失败与回退：

- 任一局部再生成失败时，系统必须保留上一可用版本
- 局部再生成失败后，系统必须支持模块级重试，不得触发项目级重跑
- 局部再生成不得触发素材分析全量重跑

---

## 4.4 置信度与回退策略草案

### 4.4.1 设计目标

不是所有输入都足够好，系统必须在输入不完整、模型不确定、设备性能有限时仍然可运行，并且明确告诉用户当前结果可信到什么程度。

### 4.4.2 置信度分层

将关键模块输出统一打上置信度：

- `high`
- `medium`
- `low`

同时统一记录以下回退信息：

- `match_confidence`：当前段落、镜头或建议结果的置信度
- `fallback_reason`：触发降级的主要原因，如 `metadata_missing`、`insufficient_assets`、`low_confidence_match`
- `fallback_action`：系统实际采用的降级动作，如 `semantic_align`、`simplified_timeline`、`alternative_render_unit`、`manual_confirm`、`segment_skip`

适用对象包括：

- 故事段落提取结果
- 故事与镜头对齐结果
- 原声保留判断
- 旁白生成建议
- 段落级替代呈现结果

### 4.4.3 统一回退枚举

后续所有模块必须复用同一组回退原因与动作，不得各自发明同义字段。

`FallbackReason` 至少包括：

- `metadata_missing`
- `short_note`
- `low_structure_note`
- `insufficient_assets`
- `low_confidence_match`
- `resource_limited`

`FallbackAction` 至少包括：

- `semantic_align`
- `simplified_timeline`
- `alternative_render_unit`
- `manual_confirm`
- `segment_skip`
- `switch_to_lightweight_mode`

### 4.4.4 回退触发表

以下规则用于把“触发条件 → 系统动作 → 状态变化 → 诊断输出”固定下来。

| `trigger_code` | 所属阶段 | 判定规则 | `fallback_reason` | `fallback_action` | 节点状态 | 项目状态 | `user_message_key` | 诊断文件 |
|---|---|---|---|---|---|---|---|---|
| `note_too_short` | `input_validation` / `story_parsing` | 游记有效字数 `<150` | `short_note` | `simplified_timeline` | `degraded` | `ready` 或 `running` | `input.note_too_short` | `input_validation_report.json` |
| `note_low_structure` | `story_parsing` | 有效事件、地点或转折线索 `<3`，或无法形成稳定故事段落 | `low_structure_note` | `simplified_timeline` | `degraded` | `running` | `story.note_low_structure` | `run_summary.json`、`segment_diagnostics.json` |
| `metadata_sparse_partial` | `alignment` | 仅部分素材缺失 `GPS`、`EXIF` 或拍摄时间 | `metadata_missing` | `semantic_align` | `degraded` | `running` | `alignment.metadata_sparse_partial` | `segment_diagnostics.json`、`fallback_events.jsonl` |
| `metadata_sparse_global` | `alignment` | 全项目大部分素材缺失时间和地点元数据 | `metadata_missing` | `semantic_align` | `degraded` | `running` 或 `awaiting_user` | `alignment.metadata_sparse_global` | `segment_diagnostics.json`、`fallback_events.jsonl` |
| `asset_coverage_low` | `alignment` / `edit_planning` | 某段落缺少足够视频镜头，但仍可由照片、地点卡、文字卡或旁白过渡补足 | `insufficient_assets` | `alternative_render_unit` | `degraded` | `running` | `alignment.asset_coverage_low` | `segment_diagnostics.json` |
| `high_priority_asset_missing` | `highlight_confirmation` | 高重要度段落缺少足够镜头，且替代呈现单元仍不足以满足最低表达要求 | `insufficient_assets` | `manual_confirm` | `failed_manual` 或 `blocked` | `awaiting_user` | `highlight.high_priority_asset_missing` | `segment_diagnostics.json`、`run_summary.json` |
| `segment_match_low_confidence` | `alignment` / `highlight_confirmation` | 单段推荐结果 `match_confidence=low` | `low_confidence_match` | 低重要度段落为 `segment_skip`，高重要度段落为 `manual_confirm` | `degraded` 或 `failed_manual` | `running` 或 `awaiting_user` | `alignment.segment_match_low_confidence` | `segment_diagnostics.json`、`fallback_events.jsonl` |
| `project_match_low_confidence_ratio` | `highlight_confirmation` | 低置信段落占比 `>30%` | `low_confidence_match` | `manual_confirm` | `failed_manual` | `awaiting_user` | `highlight.project_match_low_confidence_ratio` | `run_summary.json`、`segment_diagnostics.json` |
| `resource_budget_limited` | `media_analysis` / `alignment` / `render_export` | 设备资源低于 `4.7` 定义的推荐档或当前运行预算不足 | `resource_limited` | `switch_to_lightweight_mode` | `degraded` | `running` | `runtime.resource_budget_limited` | `run_summary.json`、`fallback_events.jsonl` |

补充约束如下：

- `metadata_sparse_global` 本身不得直接导致项目失败，但若高重要度段落回退后仍为 `low`，必须进入 `manual_confirm`
- `asset_coverage_low` 仅允许段落级降级，不得把单段素材不足直接上升为项目级失败
- `segment_match_low_confidence` 中，只有低重要度段落可被用户主动跳过；高重要度段落不得静默跳过
- `resource_budget_limited` 触发后，系统必须提示质量与耗时变化，并在诊断中记录切换前后的运行模式

### 4.4.5 多异常并发时的处理顺序

多异常并发时，系统必须按以下顺序处理：

1. 先处理硬性输入错误，未通过 `input_validation` 时不得进入后续阶段
2. 再处理资源模式切换，先确定是否进入轻量模式，再执行分析与对齐
3. 再处理元数据缺失，完成特征回退，不因缺少时间地点信息直接放弃对齐
4. 再处理素材不足，优先补足可替代呈现单元，而不是直接删除故事段落
5. 若回退后仍存在低置信匹配，则进入人工确认节点
6. 只有在无法形成最小可用故事骨架时，才允许项目级失败；其余情况应优先段落级降级

### 4.4.6 设计原则

- 不隐瞒不确定性
- 不在低置信时强行全自动
- 不让用户为底层模型错误承担全部成本
- 不静默省略高重要度段落

---

## 4.5 输入规范与校验草案

### 4.5.1 输入包定义

V1 项目输入必须抽象为统一的 `ProjectInputContract`，最少包含以下对象：

- `travel_note`：游记正文，作为故事解析主输入
- `media_files[]`：照片、视频素材集合
- `bgm_asset`：项目级背景音乐
- `tts_voice`：项目级配音音色
- `metadata_pack`：可选增强信息，包含 `GPS`、`EXIF`、拍摄时间等

系统不得将“游记为空但靠素材硬剪”视作 V1 正常输入；没有 `travel_note` 的项目不属于默认验收口径。

### 4.5.2 必填项与支持格式

V1 输入要求如下：

| 输入项 | 是否必填 | V1 支持格式 | 说明 |
|---|---|---|---|
| `travel_note` | 是 | `txt`、`md`、直接粘贴文本 | 仅支持中文自由文本 |
| `media_files[]` | 是 | 图片：`jpg`、`jpeg`、`png`、`heic`；视频：`mp4`、`mov`、`m4v` | 支持照片和视频混合导入 |
| `bgm_asset` | 是 | 本地可读音频文件 | V1 不支持“稍后再选 BGM” |
| `tts_voice` | 是 | 已配置的系统或项目内音色标识 | V1 不支持“无旁白”模式 |
| `metadata_pack` | 否 | `GPS`、`EXIF`、拍摄时间 | 作为增强信息，不作为项目创建前置条件 |

补充要求如下：

- 游记建议不少于 `150` 字
- 游记建议至少包含 `3` 个事件、地点或转折线索
- 标准旅行项目的素材总量建议维持在 `150-300` 个文件之间
- 标准旅行项目的原始视频总时长建议不超过 `60` 分钟

### 4.5.3 硬性阻断校验

以下情况必须在 `input_validation` 阶段阻断，不得进入 `ready`：

| `check_code` | 阻断条件 | `failure_type` | 节点状态 | 用户提示键 | 推荐修复动作 |
|---|---|---|---|---|---|
| `note_missing` | 未提供游记，或游记去除空白后为空 | `input_error` | `failed_manual` | `input.note_missing` | 补充游记后重新校验 |
| `media_missing` | 未导入任何照片或视频 | `input_error` | `failed_manual` | `input.media_missing` | 至少导入一项可读媒体 |
| `media_unreadable_all` | 所有媒体文件均不可读、损坏或解码失败 | `input_error` | `failed_manual` | `input.media_unreadable_all` | 替换损坏文件后重试 |
| `media_unsupported_all` | 所有媒体文件格式均不在 V1 支持范围内 | `input_error` | `failed_manual` | `input.media_unsupported_all` | 转码或替换为支持格式 |
| `bgm_missing` | 未选择 `bgm_asset` | `input_error` | `failed_manual` | `input.bgm_missing` | 选择 BGM 后继续 |
| `tts_voice_missing` | 未选择 `tts_voice` | `input_error` | `failed_manual` | `input.tts_voice_missing` | 选择音色后继续 |

上述场景必须满足以下规则：

- `input_validation` 失败时，项目状态保持 `draft`
- 阻断原因必须同时写入 `input_validation_report.json` 与 `run_summary.json`
- 若只存在“部分文件不可读或不支持”，但仍有最小可用输入，则不得按阻断处理

### 4.5.4 软性风险与自动降级

以下情况允许继续，但必须显式提示、留痕，并映射到后续回退策略：

| `check_code` | 触发条件 | 严重级别 | 默认处理 | 对应 `fallback_reason` | 对应 `fallback_action` | 用户提示键 |
|---|---|---|---|---|---|---|
| `note_too_short` | 游记有效字数 `<150` | `warning` | 允许继续，后续切换简化叙事 | `short_note` | `simplified_timeline` | `input.note_too_short` |
| `note_low_structure` | 游记缺少足够事件、地点或转折线索 | `warning` | 允许继续，降低复杂结构判断 | `low_structure_note` | `simplified_timeline` | `input.note_low_structure` |
| `media_unreadable_partial` | 存在部分损坏或不可读文件 | `warning` | 跳过异常文件并继续 | 无 | 无 | `input.media_unreadable_partial` |
| `media_unsupported_partial` | 存在部分不支持格式文件 | `warning` | 跳过异常文件并继续 | 无 | 无 | `input.media_unsupported_partial` |
| `metadata_sparse` | 时间、地点元数据覆盖不足 | `warning` | 允许继续并切换语义优先对齐 | `metadata_missing` | `semantic_align` | `input.metadata_sparse` |
| `asset_count_low` | 可用素材数量明显低于标准旅行项目建议值 | `warning` | 允许继续，但提示可能需要替代表现单元 | `insufficient_assets` | `alternative_render_unit` | `input.asset_count_low` |
| `video_missing` | 仅有照片，无可用视频 | `warning` | 允许继续，以照片、文字卡和旁白为主 | `insufficient_assets` | `alternative_render_unit` | `input.video_missing` |
| `photo_missing` | 仅有视频，无照片 | `info` | 允许继续，不触发项目级失败 | 无 | 无 | `input.photo_missing` |
| `media_over_budget` | 素材数量或总时长明显超出标准旅行项目建议值 | `warning` | 允许继续，但需提示耗时上升或建议先筛选素材 | `resource_limited` | `switch_to_lightweight_mode` | `input.media_over_budget` |

软性风险必须满足以下规则：

- 同一项目可同时命中多个 `check_code`，系统必须全部记录，不得只保留首个告警
- 软性风险默认不把项目状态打回 `draft`，但必须在后续节点中体现 `degraded`
- 所有“允许继续”的风险都必须提供 `recommended_fix`，如“补写游记摘要”“补充高光段落素材”“先筛选无效素材”

### 4.5.5 校验结果表达

输入校验结果必须统一抽象为 `InputValidationReport`，并输出到 `input_validation_report.json`。

`InputCheckSeverity` 取值固定为：

- `info`
- `warning`
- `blocking`

每条校验记录至少包含以下字段：

- `check_code`
- `severity`
- `blocking`
- `user_message_key`
- `failure_type`
- `fallback_reason`
- `fallback_action`
- `affected_assets[]`
- `recommended_fix`
- `detected_at_stage`

系统不得仅输出自然语言错误文案而缺少结构化字段；用户提示文案与日志诊断必须共享同一条校验记录。

---

## 4.6 任务编排与失败恢复

### 4.6.1 设计目标

本节用于定义 V1 主链路的统一运行规则，确保系统在长任务、人工确认、局部再生成和异常中断场景下都具备一致的状态表达与恢复路径。

系统必须满足以下约束：

- 长任务必须按明确阶段推进，不得以“黑盒处理中”覆盖整个流程
- 状态机必须同时表达“项目整体状态”和“节点执行状态”，避免单一状态无法描述人工确认与局部失败
- 任一失败都必须可定位到具体阶段、具体节点和最近可恢复边界
- 默认恢复动作必须优先复用最近有效中间产物，不得默认整项目重跑
- 任一高重要度段落的降级、跳过、人工接管和失败都必须留痕

### 4.6.2 主链路阶段与依赖关系

V1 项目运行必须按以下阶段推进：

1. `input_validation`
2. `asset_indexing`
3. `story_parsing`
4. `story_skeleton_confirmation`
5. `media_analysis`
6. `alignment`
7. `highlight_confirmation`
8. `edit_planning`
9. `narration_tts_subtitles`
10. `audio_mix`
11. `render_export`

第一版成片生成完成后，系统必须支持以下局部再生成分支：

- `regenerate_narration`
- `regenerate_bgm_mix`
- `regenerate_shorter_cut`

阶段依赖必须满足以下规则：

- `input_validation` 成功前，不得进入任何自动分析或生成阶段
- `asset_indexing` 成功后，`story_parsing` 与 `media_analysis` 可并行执行
- `story_skeleton_confirmation` 必须等待 `story_parsing` 成功后触发
- `alignment` 必须同时等待“故事骨架已确认”和“素材分析已完成”
- `highlight_confirmation` 必须等待 `alignment` 成功或降级完成后触发
- `edit_planning` 及其下游阶段，必须等待高光确认完成后才可继续
- 任一必选人工确认节点触发后，项目不得自动继续向下游推进

### 4.6.3 双层状态机定义

系统必须采用双层状态机。

项目整体状态定义为 `ProjectRunStatus`：

- `draft`：项目已创建但尚未通过输入校验
- `ready`：输入满足运行前置条件，等待启动或恢复
- `running`：存在至少一个自动处理节点正在执行
- `awaiting_user`：已进入故事骨架确认、高光确认或必须人工接管的确认节点
- `retryable_failed`：项目在某节点失败，但存在明确恢复起点和可执行重试动作
- `completed_with_fallback`：项目成功产出结果，但存在降级、替代表现或低置信人工确认痕迹
- `completed`：项目成功产出结果，且无影响验收的降级残留
- `canceled`：用户主动取消，后续不得继续自动推进

节点执行状态定义为 `TaskNodeStatus`：

- `pending`：节点尚未开始
- `blocked`：节点受上游依赖或人工确认阻塞
- `running`：节点正在执行
- `succeeded`：节点成功完成
- `degraded`：节点在降级条件下完成，允许主链路继续
- `failed_retryable`：节点失败，但允许从最近有效边界恢复
- `failed_manual`：节点失败，必须由用户修正输入、确认降级或切换模式后继续
- `skipped`：节点因用户显式跳过或分支不适用而未执行
- `canceled`：节点被用户取消或被更高优先级重算操作中止

系统不得再使用含义不清的 `partial_success` 作为统一状态；涉及“可用但有降级”的结果，必须明确落在 `degraded` 或 `completed_with_fallback`。

### 4.6.4 关键状态迁移规则

项目级状态迁移至少应满足以下规则：

- 输入校验通过后，项目状态从 `draft` 进入 `ready`
- 项目启动或恢复执行后，状态从 `ready` 或 `retryable_failed` 进入 `running`
- 当流程进入故事骨架确认、高光确认或必须人工确认的低置信节点时，状态从 `running` 进入 `awaiting_user`
- 用户完成确认并继续执行后，状态从 `awaiting_user` 重新进入 `running`
- 任一节点进入 `failed_retryable` 且当前无可继续的并行节点时，项目状态进入 `retryable_failed`
- 项目在存在降级痕迹的前提下成功导出时，状态进入 `completed_with_fallback`
- 项目在无关键降级残留的前提下成功导出时，状态进入 `completed`
- 用户主动终止运行时，项目状态进入 `canceled`

节点级迁移至少应满足以下规则：

- 未满足依赖的节点必须保持 `blocked`
- 依赖满足后，节点从 `pending` 或 `blocked` 进入 `running`
- 节点正常完成后进入 `succeeded`
- 节点因回退策略完成时进入 `degraded`
- 节点失败但存在明确重试路径时进入 `failed_retryable`
- 节点失败且必须用户介入时进入 `failed_manual`
- 用户返回上游重新确认后，仅受影响的下游节点重置为 `pending` 或 `blocked`

状态失效与重算边界必须满足以下要求：

- 用户修改故事骨架后，只允许使 `alignment` 及其下游节点失效，不得使 `asset_indexing` 或 `media_analysis` 失效
- 用户修改高光选择后，只允许使 `edit_planning` 及其下游节点失效
- 仅重写旁白时，只允许使 `narration_tts_subtitles`、`audio_mix`、`render_export` 失效
- 仅更换 BGM 并重混音时，只允许使 `audio_mix` 与 `render_export` 失效
- 压缩到更短时长时，只允许使 `edit_planning` 及其下游节点失效，不得重跑素材分析

### 4.6.5 失败分类与恢复动作

系统必须统一记录 `FailureType` 和 `RecoveryAction`。

失败分类至少包括：

- `input_error`：输入缺失、文件损坏、格式不支持、素材不可读
- `confidence_error`：故事解析、镜头对齐或生成建议置信度过低
- `resource_error`：本地内存、磁盘、算力或处理时间预算不足
- `dependency_error`：模型推理、本地服务、可选云端增强或外部依赖异常
- `artifact_error`：缓存损坏、中间产物缺失、版本不一致
- `export_error`：渲染、封装、写盘或导出产物生成失败

对应恢复动作 `RecoveryAction` 至少包括：

- `retry_same_node`
- `resume_from_last_good_boundary`
- `switch_to_lightweight_mode`
- `fallback_and_continue`
- `require_user_confirmation`
- `require_user_fix_input`
- `re_export_only`

失败处理规则如下：

- `input_error` 必须阻断主链路，并要求用户修复输入后再继续
- `confidence_error` 必须优先进入降级或人工确认，不得直接伪装成高确定性结果
- `resource_error` 必须优先提供轻量模式、延迟执行或缩小处理范围的恢复建议
- `dependency_error` 在不影响已有中间产物的前提下应默认为可重试
- `artifact_error` 必须从最近有效边界恢复，不得默认全链路重跑
- `export_error` 必须保留时间线、混音结果和诊断信息，优先支持仅重新导出

### 4.6.6 缓存边界与断点续跑

以下中间产物必须以可版本化方式持久化，统一抽象为 `ArtifactVersion`：

- `asset_index`
- `story_version`
- `media_analysis_pack`
- `alignment_version`
- `highlight_selection_version`
- `timeline_version`
- `narration_pack`
- `audio_mix_pack`
- `export_bundle`
- `diagnostic_bundle`

断点续跑必须满足以下要求：

- 每个持久化边界都必须记录生成时间、来源节点和上游依赖版本
- 项目恢复时，系统必须先识别最近有效边界，再决定从哪个节点继续执行
- 若下游中间产物依赖的上游版本已变化，则下游产物必须失效，不得继续复用
- 若仅导出环节失败，系统必须允许基于现有 `timeline_version` 和 `audio_mix_pack` 重新导出
- 若 `narration_pack` 或 `audio_mix_pack` 失败，不得连带清除 `alignment_version` 或更早阶段的产物
- 若 `diagnostic_bundle` 缺失，不得影响成片恢复，但必须在下一次运行时补写

### 4.6.7 模块级重试与局部再生成范围

系统应支持模块级重试，而不是项目级重跑。

最低重试粒度如下：

- 仅重跑游记解析：重算 `story_parsing` 与 `story_skeleton_confirmation`
- 仅重跑镜头对齐：重算 `alignment` 与 `highlight_confirmation`
- 仅重写旁白与 TTS：重算 `narration_tts_subtitles`、`audio_mix`、`render_export`
- 仅更换 BGM 并重混音：重算 `audio_mix`、`render_export`
- 仅压缩到更短时长：重算 `edit_planning` 及其下游
- 仅重新导出：只重跑 `render_export`

模块级重试必须满足以下条款：

- 任一局部再生成失败时，系统必须保留上一可用成片版本
- 重试时必须默认沿用最新已确认的故事骨架版本与高光确认版本
- 重试不得静默解除用户的“必须保留”“不要再用”“纪念性必保留”等显式选择
- 当失败节点属于高重要度段落相关处理时，恢复后仍必须保留对应降级、跳过或人工确认记录

### 4.6.8 诊断输出与验收约束

失败、降级或恢复场景下，系统必须输出统一的 `DiagnosticBundle`，用于同时支撑用户提示、研发排障和恢复执行。

#### 4.6.8.1 统一诊断字段

所有运行记录至少必须包含以下全局字段：

- `run_id`
- `project_id`
- `started_at`
- `ended_at`
- `project_status`
- `failed_stage`
- `failed_node`
- `failure_type`
- `failure_code`
- `retryable`
- `fallback_reason`
- `fallback_action`
- `resume_from`
- `last_good_version`
- `user_message_key`
- 原始错误日志路径
- 失败原因摘要

其中：

- `failure_code` 用于结构化定位问题，如 `note_missing`、`project_match_low_confidence_ratio`
- `user_message_key` 用于映射用户可见文案，不得直接用自由文本替代
- `fallback_reason`、`fallback_action` 必须与 `4.4` 中定义的枚举保持一致

#### 4.6.8.2 诊断文件清单

`DiagnosticBundle` 至少包含以下文件：

| 文件名 | 用途 | 最低必填内容 |
|---|---|---|
| `run_summary.json` | 项目级运行摘要 | 全局状态、失败节点、恢复入口、用户提示键 |
| `input_validation_report.json` | 输入校验结果 | 全部 `check_code`、严重级别、受影响文件、建议修复动作 |
| `segment_diagnostics.json` | 段落级诊断 | 每段重要度、匹配置信度、素材覆盖状态、替代表现情况、用户确认结果 |
| `fallback_events.jsonl` | 回退事件流 | 每次触发回退的时间、阶段、原因、动作、影响范围 |
| `node_status_timeline.jsonl` | 节点状态时间线 | 节点开始、完成、降级、失败、恢复记录 |
| `export_report.json` | 导出诊断 | 导出输入版本、失败原因、重导出入口、产物路径 |
| `logs/runtime.log` | 原始运行日志 | 模块日志、错误栈、外部依赖报错 |

#### 4.6.8.3 段落级诊断字段

`segment_diagnostics.json` 中每个故事段落至少必须记录：

- `segment_id`
- `importance`
- `story_summary`
- `coverage_status`
- `match_confidence`
- `selected_asset_ids[]`
- `candidate_count`
- `alternative_render_unit`
- `requires_manual_confirmation`
- `user_decision`

补充规则如下：

- 高重要度段落若触发降级、跳过或人工确认，必须单独成条记录，不得只体现在全局摘要
- `alternative_render_unit` 至少区分照片补位、地点卡、文字卡、旁白过渡
- `user_decision` 必须记录“接受降级”“替换素材”“跳过段落”“返回补写游记”等显式动作

#### 4.6.8.4 失败原因映射规则

系统必须把输入校验码、回退触发码和失败码映射到统一出口：

| 来源字段 | 示例 | 用户提示 | 节点状态 | 日志字段 | 诊断落点 |
|---|---|---|---|---|---|
| `check_code` | `note_missing` | 使用 `user_message_key=input.note_missing` | `failed_manual` | `failure_code=note_missing` | `input_validation_report.json`、`run_summary.json` |
| `check_code` | `metadata_sparse` | 使用 `user_message_key=input.metadata_sparse` | `degraded` | `fallback_reason=metadata_missing` | `input_validation_report.json`、`fallback_events.jsonl` |
| `trigger_code` | `segment_match_low_confidence` | 使用 `user_message_key=alignment.segment_match_low_confidence` | 高重要度为 `failed_manual`，低重要度为 `degraded` | `fallback_action=manual_confirm` 或 `segment_skip` | `segment_diagnostics.json`、`fallback_events.jsonl` |
| `trigger_code` | `project_match_low_confidence_ratio` | 使用 `user_message_key=highlight.project_match_low_confidence_ratio` | `failed_manual` | `failure_code=project_match_low_confidence_ratio` | `run_summary.json`、`segment_diagnostics.json` |
| `failure_type` | `export_error` | 使用 `user_message_key=export.failed_retryable` 或同类键 | `failed_retryable` | `failure_type=export_error` | `export_report.json`、`logs/runtime.log` |

映射规则必须满足以下约束：

- 用户界面不得直接读取原始错误栈作为提示文案
- 日志必须保留结构化 `failure_code`，不得只保留自然语言摘要
- 同一异常在用户提示、节点状态和诊断文件中必须可互相追溯，不得出现编码不一致

#### 4.6.8.5 运行期可观测性与验收口径

运行期可观测性必须满足以下要求：

- 长任务过程中必须持续展示当前阶段、当前节点和上一成功阶段
- 项目处于 `retryable_failed` 时，必须明确展示是否可重试和推荐恢复动作
- 项目处于 `awaiting_user` 时，必须明确展示阻塞原因，不得仅显示“处理中”
- 高重要度段落若发生降级、跳过或替代表现，必须在项目诊断中单独记录

本节默认验收口径如下：

- 恢复动作默认优先从最近有效边界继续，不以整项目重跑作为默认行为
- 任一模块失败都必须可定位到具体阶段和节点
- 导出失败时，系统必须保留可用于重新导出的中间产物和诊断日志
- 局部再生成失败时，用户仍可预览和保留上一可用版本

---

## 4.7 运行环境与性能约束草案

### 4.7.1 运行方式

V1 采用本地桌面应用 + 本地处理服务架构。

### 4.7.2 设备分层

建议至少定义两档设备：

- 基础档：CPU 可运行，但处理时间较长，默认启用轻量模型
- 推荐档：具备可用 GPU，加速 ASR、视觉分析与 TTS

### 4.7.3 性能设计原则

- 预处理与导出允许较长耗时，但必须给出明确进度
- 需要避免重复计算
- 需要支持后台处理与失败后恢复
- 需要给用户预计剩余时间的粗略提示

### 4.7.4 本地与联网边界

建议在 PRD 中明确以下策略：

- 哪些能力默认本地执行
- 哪些能力可选云端增强
- 用户素材是否离开本机
- 联网失败时哪些功能仍可用

---

## 4.8 版本边界

### 4.8.1 V1 必做

- 导入游记、素材、BGM
- 项目级音色选择
- 自动提取素材基础信息并建立索引
- 自动生成故事段落
- 自动分析素材并生成候选镜头
- 故事骨架确认
- 高光确认
- 自动生成第一版成片
- 支持以下至少 `3` 类局部再生成，具体交互约束见 `4.3.5`：
  - 仅重写旁白
  - 仅更换 BGM 并重混音
  - 压缩到更短时长
- 导出 `MP4`、字幕、配音文件、`manifest`、诊断日志
- 出错时支持模块级重试和重新导出

### 4.8.2 V1 不做

- 多风格模板市场
- 多平台比例自动适配
- 深度剪映工程互通
- 多人关系建模
- 复杂地图动画和高级文字特效
- 用户长期偏好学习
- 云端协同和多设备同步

### 4.8.3 V1 不承诺场景

以下场景不纳入 V1 的默认验收承诺：

- 超过标准旅行项目规模的大型项目
- 纯无游记输入的项目
- 全部素材均缺失时间线线索且语义信息极弱的项目
- 对纯 CPU 设备上的高性能处理要求
- 专业剪辑级精细时间线编辑需求

### 4.8.4 V1 成立条件

只有同时满足以下条件，才可视为 V1 成立：

- 系统能在基础档 CPU 设备上跑通标准旅行项目
- 系统能稳定产出 `2-4` 分钟、`16:9` 横屏的旅行成片
- 用户对最终成片的主观评分达到 `4/5` 及以上
- 系统支持至少一次局部再生成闭环
- 失败时可定位、可重试、可重新导出

---

## 4.9 模块需求草案

### 4.9.1 设计目标

本节用于把 `4.3`、`4.4`、`4.5`、`4.6` 中已确定的交互、回退、校验、状态和诊断规则落实到模块职责与接口边界中，形成可直接指导实现的正式 PRD 条款。

V1 模块设计必须满足以下要求：

- 每个主链路阶段都必须对应唯一主责模块，不得出现多模块共同拥有同一阶段状态的情况
- 每个模块都必须明确输入产物、输出产物、可接受状态和失败恢复动作
- 每个必选人工节点都必须以独立模块责任表达，不得混入自动分析模块内部
- 每个会降级、跳过、失败或等待人工确认的模块都必须写入统一诊断字段
- 模块设计必须优先支持版本复用、断点续跑和局部再生成，不得默认全链路重跑

### 4.9.2 模块分层

V1 模块按以下四层组织：

| 层级 | 包含模块 | 主要职责 |
|---|---|---|
| 交互与项目层 | `Project Workspace`、`Story Skeleton Confirmation`、`Highlight Confirmation` | 项目创建、素材导入、确认节点承载、版本切换、结果预览 |
| 编排与状态层 | `Input Validator`、`Run Orchestrator`、`Artifact & Version Store` | 输入校验、阶段调度、双层状态机推进、缓存与版本失效管理 |
| 核心生成层 | `Story Parser`、`Media Analyzer`、`Alignment Engine`、`Edit Planner`、`Narration / TTS / Subtitle Engine`、`Audio Composer`、`Renderer & Exporter` | 将输入逐步转成候选故事骨架、镜头对齐、时间线、音频和导出产物 |
| 产物与诊断层 | `Diagnostic Reporter` | 汇总运行记录、回退事件、段落级诊断和导出报告 |

分层约束如下：

- 交互与项目层不得直接承担重型媒体分析和渲染计算
- 编排与状态层不得直接生成最终成片内容，但必须拥有阶段推进与重试决策权
- 核心生成层不得绕过统一状态机直接写入“完成”状态
- 产物与诊断层不得决定业务流程，但必须对失败、降级和恢复结果形成统一出口

### 4.9.3 V1 模块清单与职责

| 模块 | 核心职责 | 主责阶段 | 必须产物 | 附加约束 |
|---|---|---|---|---|
| `Project Workspace` | 创建项目、接收 `ProjectInputContract`、建立项目配置、展示版本与结果入口 | `asset_indexing` | 项目配置、素材导入记录、`asset_index` | 只负责导入和展示，不直接执行复杂分析 |
| `Input Validator` | 执行硬性阻断校验与软性风险识别，生成 `InputValidationReport` | `input_validation` | `input_validation_report.json` | 必须把 `check_code` 映射到统一提示键与回退枚举 |
| `Artifact & Version Store` | 持久化 `ArtifactVersion`、校验依赖版本、判断产物是否可复用 | 无独占阶段 | 全部版本元数据、失效记录 | 不得复用依赖版本已变化的下游产物 |
| `Run Orchestrator` | 驱动 `ProjectRunStatus` 与 `TaskNodeStatus`、调度并发节点、发起恢复执行 | 无独占阶段 | 节点状态流、恢复入口、运行上下文 | 必须是所有长任务状态变更的唯一写入方 |
| `Story Parser` | 将游记解析为候选故事骨架、识别低结构风险、输出旁白初稿素材 | `story_parsing` | 候选故事段落、解析摘要 | 低置信时必须显式回退为简化叙事 |
| `Story Skeleton Confirmation` | 承载故事骨架确认、冻结 `story_version`、记录用户编辑动作 | `story_skeleton_confirmation` | `story_version`、用户决策记录 | 用户未确认前不得继续到对齐阶段 |
| `Media Analyzer` | 生成镜头级素材画像、质量评分、原声兴趣信号 | `media_analysis` | `media_analysis_pack` | 必须支持轻量模式和部分素材跳过 |
| `Alignment Engine` | 建立故事段落与候选镜头的匹配关系 | `alignment` | `alignment_version`、段落候选镜头集合 | 不得只依赖单一语义相似度做最终匹配 |
| `Highlight Confirmation` | 展示高重要度段落候选镜头、冻结高光选择与禁用规则 | `highlight_confirmation` | `highlight_selection_version`、用户决策记录 | 高重要度段落低置信时必须要求人工确认 |
| `Edit Planner` | 生成可执行的叙事结构、时长控制和镜头编排结果 | `edit_planning` | `timeline_version` | 压缩短版时只能复用已确认骨架与高光版本 |
| `Narration / TTS / Subtitle Engine` | 生成旁白文案、TTS 音频、旁白字幕与字卡计划 | `narration_tts_subtitles` | `narration_pack` | 仅重写旁白时只能使本模块及下游失效 |
| `Audio Composer` | 混合旁白、现场原声与 `BGM`，生成混音计划 | `audio_mix` | `audio_mix_pack` | 必须保留原声抉择的诊断留痕 |
| `Renderer & Exporter` | 执行片段拼接、字幕烧录、封装导出与重导出 | `render_export` | `export_bundle` | 导出失败时必须优先支持 `re_export_only` |
| `Diagnostic Reporter` | 汇总 `DiagnosticBundle`、落盘段落级诊断和运行摘要 | 无独占阶段 | `diagnostic_bundle` | 缺少诊断包不得阻断成片恢复，但必须在下次运行补写 |

### 4.9.4 模块与主链路阶段映射

所有主链路阶段必须按以下映射推进：

| 阶段 | 主责模块 | 协作模块 | 最低输出 | 阻断条件 |
|---|---|---|---|---|
| `input_validation` | `Input Validator` | `Run Orchestrator`、`Diagnostic Reporter` | `InputValidationReport` | 任一 `blocking` 校验未修复 |
| `asset_indexing` | `Project Workspace` | `Artifact & Version Store`、`Diagnostic Reporter` | `asset_index` | 无最小可用素材集 |
| `story_parsing` | `Story Parser` | `Run Orchestrator`、`Diagnostic Reporter` | 候选故事骨架草案 | 游记解析失败且无法形成最低骨架 |
| `story_skeleton_confirmation` | `Story Skeleton Confirmation` | `Project Workspace`、`Artifact & Version Store` | `story_version` | 用户未确认或需返回修正 |
| `media_analysis` | `Media Analyzer` | `Artifact & Version Store`、`Diagnostic Reporter` | `media_analysis_pack` | 无法得到最小可用镜头集合 |
| `alignment` | `Alignment Engine` | `Artifact & Version Store`、`Diagnostic Reporter` | `alignment_version` | 上游故事骨架未确认，或匹配结果需转人工确认 |
| `highlight_confirmation` | `Highlight Confirmation` | `Project Workspace`、`Artifact & Version Store` | `highlight_selection_version` | 高重要度段落仍未完成人工确认 |
| `edit_planning` | `Edit Planner` | `Artifact & Version Store`、`Diagnostic Reporter` | `timeline_version` | 无最小可用叙事结构 |
| `narration_tts_subtitles` | `Narration / TTS / Subtitle Engine` | `Artifact & Version Store`、`Diagnostic Reporter` | `narration_pack` | 必需音色不可用且无法恢复 |
| `audio_mix` | `Audio Composer` | `Artifact & Version Store`、`Diagnostic Reporter` | `audio_mix_pack` | 关键音轨缺失且无法重建 |
| `render_export` | `Renderer & Exporter` | `Artifact & Version Store`、`Diagnostic Reporter` | `export_bundle` | 渲染失败且需等待重试或重导出 |

阶段映射必须额外满足以下规则：

- `asset_indexing` 完成后，`story_parsing` 与 `media_analysis` 可并行，但状态推进必须仍由 `Run Orchestrator` 统一写入
- `story_skeleton_confirmation` 与 `highlight_confirmation` 都属于必选人工节点，项目状态必须进入 `awaiting_user`
- `Diagnostic Reporter` 不拥有独占阶段，但必须在每个阶段完成、降级、失败、恢复时同步更新诊断输出

### 4.9.5 模块输入输出与依赖边界

阶段型模块必须至少遵守以下 `StageContract`：

- `stage_name`
- `owner_module`
- `required_inputs[]`
- `produced_outputs[]`
- `allowed_statuses[]`
- `failure_types[]`
- `recovery_actions[]`

V1 阶段型模块的最低合同如下：

| 模块 | 必要输入 | 输出产物 | 上游依赖 | 允许状态 | 主要失败类型 | 默认恢复动作 | 用户动作关系 |
|---|---|---|---|---|---|---|---|
| `Input Validator` | `ProjectInputContract` | `InputValidationReport` | 无 | `succeeded`、`degraded`、`failed_manual` | `input_error` | `require_user_fix_input` | 用户修复输入后重校验 |
| `Project Workspace` | 已创建项目、`media_files[]` | `asset_index`、项目导入摘要 | `input_validation` 非阻断通过 | `succeeded`、`degraded`、`failed_retryable` | `input_error`、`artifact_error` | `retry_same_node`、`require_user_fix_input` | 无直接确认，但负责展示导入结果 |
| `Story Parser` | `travel_note`、项目配置 | 候选故事骨架草案、解析摘要 | `asset_index`、`ProjectInputContract` | `succeeded`、`degraded`、`failed_retryable`、`failed_manual` | `confidence_error`、`dependency_error` | `fallback_and_continue`、`retry_same_node`、`require_user_confirmation` | 为故事骨架确认提供初稿 |
| `Story Skeleton Confirmation` | 候选故事骨架草案 | `story_version`、`UserDecision` | `story_parsing` 完成 | `blocked`、`succeeded` | 无独立系统失败类型，用户返回上一步时视为待确认 | `require_user_confirmation` | 合并、删除、排序、必保留标记 |
| `Media Analyzer` | `asset_index` | `media_analysis_pack` | `asset_indexing` 完成 | `succeeded`、`degraded`、`failed_retryable`、`failed_manual` | `resource_error`、`dependency_error`、`artifact_error` | `switch_to_lightweight_mode`、`retry_same_node`、`resume_from_last_good_boundary` | 无直接确认，结果供高光确认使用 |
| `Alignment Engine` | `story_version`、`media_analysis_pack` | `alignment_version`、段落候选镜头集合 | 故事骨架已确认、素材分析已完成 | `succeeded`、`degraded`、`failed_retryable` | `confidence_error`、`resource_error`、`artifact_error` | `semantic_align`、`fallback_and_continue`、`resume_from_last_good_boundary` | 低置信结果必须传递到高光确认 |
| `Highlight Confirmation` | `alignment_version` | `highlight_selection_version`、`UserDecision` | `alignment` 完成 | `blocked`、`succeeded`、`failed_manual` | `confidence_error` | `require_user_confirmation` | 接受、替换、禁用、纪念性必保留、跳过低重要度段落 |
| `Edit Planner` | `story_version`、`highlight_selection_version` | `timeline_version` | 高光确认完成 | `succeeded`、`degraded`、`failed_retryable` | `confidence_error`、`artifact_error` | `fallback_and_continue`、`resume_from_last_good_boundary` | 压缩短版时复用既有确认结果 |
| `Narration / TTS / Subtitle Engine` | `story_version`、`timeline_version`、`tts_voice` | `narration_pack` | `edit_planning` 完成 | `succeeded`、`degraded`、`failed_retryable` | `dependency_error`、`resource_error` | `retry_same_node`、`switch_to_lightweight_mode` | 仅在局部再生成中接受“重写旁白” |
| `Audio Composer` | `timeline_version`、`narration_pack`、`bgm_asset` | `audio_mix_pack` | `narration_tts_subtitles` 完成 | `succeeded`、`degraded`、`failed_retryable` | `artifact_error`、`dependency_error` | `retry_same_node`、`resume_from_last_good_boundary` | 仅在局部再生成中接受“更换 BGM 并重混音” |
| `Renderer & Exporter` | `timeline_version`、`audio_mix_pack`、字幕计划 | `export_bundle` | `audio_mix` 完成 | `succeeded`、`degraded`、`failed_retryable` | `export_error`、`resource_error` | `re_export_only`、`switch_to_lightweight_mode` | 用户可从任一可用版本重新导出 |

边界约束如下：

- 阶段型模块只允许消费已确认或已持久化的上游产物，不得读取未冻结的临时界面状态作为正式输入
- 任一模块若输出 `degraded`，必须同时输出对应的 `fallback_reason`、`fallback_action` 和 `user_message_key`
- 任一模块若需要人工确认，不得自行把结果写成 `succeeded` 并越过确认节点
- 任一模块若读取到依赖版本已失效，必须先回退到 `pending` 或 `blocked`，不得继续复用旧产物

### 4.9.6 模块级回退与局部再生成约束

模块级回退和局部再生成必须满足以下映射：

| 入口或异常 | 允许重算模块 | 禁止重算模块 | 必须保留的约束 |
|---|---|---|---|
| 仅重写旁白 | `Narration / TTS / Subtitle Engine`、`Audio Composer`、`Renderer & Exporter` | `Story Parser`、`Media Analyzer`、`Alignment Engine` | 沿用最新 `story_version`、`highlight_selection_version` |
| 仅更换 `BGM` 并重混音 | `Audio Composer`、`Renderer & Exporter` | `Story Parser`、`Media Analyzer`、`Alignment Engine`、`Narration / TTS / Subtitle Engine` | 保留上一版旁白与字幕时间线 |
| 压缩到更短时长 | `Edit Planner` 及其下游模块 | `Media Analyzer` 及其上游模块 | 不得解除“必须保留”段落和镜头约束 |
| `metadata_missing` | `Alignment Engine`、`Edit Planner` | `Story Skeleton Confirmation` 之前模块 | 必须切换为 `semantic_align` 并记录诊断 |
| `insufficient_assets` | `Alignment Engine`、`Highlight Confirmation`、`Edit Planner` | `Media Analyzer` 之前模块 | 高重要度段落不得静默删除，必须落到替代表现或人工确认 |
| `resource_limited` | 当前运行模块及其下游 | 已确认且与当前降级无关的上游模块 | 必须记录轻量模式切换前后差异 |
| `export_error` | `Renderer & Exporter` | `Audio Composer` 之前模块 | 必须优先提供 `re_export_only` |

补充要求如下：

- 局部再生成触发后，`Run Orchestrator` 必须只重置受影响节点，不得把整个项目状态回退到 `draft`
- 任一局部再生成失败时，`Project Workspace` 必须继续暴露上一可用版本预览入口
- 被用户标记为“不要再用”的镜头和“纪念性必保留”的镜头都属于跨版本约束，局部再生成不得静默丢失

### 4.9.7 模块与交互节点映射

三个必选交互节点必须由以下模块组合承载：

| 交互节点 | 触发模块 | 承载模块 | 冻结产物 | 允许返回范围 | 下游失效范围 |
|---|---|---|---|---|---|
| 故事骨架确认 | `Story Parser` | `Story Skeleton Confirmation` + `Project Workspace` | `story_version` | 返回游记解析结果并重新确认 | `alignment` 及其下游 |
| 高光确认 | `Alignment Engine` | `Highlight Confirmation` + `Project Workspace` | `highlight_selection_version` | 返回故事骨架确认或更换候选镜头 | `edit_planning` 及其下游 |
| 局部再生成 | 第一版 `export_bundle` 产出后 | `Project Workspace` + `Run Orchestrator` | 新版 `timeline_version`、`narration_pack`、`audio_mix_pack`、`export_bundle` | 返回上一可用版本或继续同入口迭代 | 仅限所选入口涉及的下游模块 |

交互节点必须额外满足以下要求：

- 承载模块必须保存用户动作的结构化 `UserDecision`，不得只保存自然语言备注
- 每个交互节点都必须显示当前所基于的上游版本标识，避免用户在不知情状态下确认过期结果
- 用户从交互节点返回上一步后，`Artifact & Version Store` 必须按依赖关系失效下游版本，不得整库清空

### 4.9.8 V1 不纳入模块职责的能力

以下能力不得被任何 V1 模块隐式承担：

- 专业级手工时间线编辑器
- 多风格模板市场和模板编排系统
- 多平台比例联动导出
- 深度剪映工程互通
- 多人协同、云端项目共享和跨设备实时同步
- 用户长期偏好学习与跨项目个性化推荐

---

## 4.10 技术方案草案

### 4.10.1 架构原则

V1 技术方案必须满足以下原则：

- 采用本地桌面应用 + 本地处理服务的双层运行架构
- 以状态驱动执行，以版本化产物驱动恢复
- 以能力接口隔离具体模型、媒体工具和第三方实现
- 以模块级重试和局部再生成替代项目级重跑
- 以结构化诊断替代自由文本报错

### 4.10.2 运行架构分层

| 运行层 | 主要内容 | 必须承担的责任 | 不得承担的责任 |
|---|---|---|---|
| `Desktop Client` | 桌面端 UI、项目管理、确认节点、预览与导出入口 | 项目创建、输入组织、进度展示、用户决策采集、版本切换 | 不直接执行重型媒体分析、渲染和状态编排 |
| `Local Processing Service` | 本地长任务执行与编排进程 | 节点调度、模型调用、媒体分析、版本写入、恢复执行、重试控制 | 不直接决定 UI 呈现和交互文案布局 |
| `Capability Providers` | 元数据提取、镜头切分、文本理解、语音识别、视觉标签、TTS、渲染等可替换能力 | 按约定输入输出执行单点能力，返回结构化结果 | 不拥有项目状态，不直接写入项目完成状态 |
| `Storage & Artifact Layer` | 本地数据库、缓存目录、导出目录、诊断目录 | 持久化配置、版本依赖、诊断文件、导出产物 | 不绕过编排层自行决定失效和恢复 |

### 4.10.3 客户端职责

客户端职责固定如下：

- 组装 `ProjectInputContract` 并发起项目创建
- 展示 `ProjectRunStatus`、阶段进度、剩余时间估计和失败入口
- 承载故事骨架确认、高光确认、局部再生成三个必选交互节点
- 展示版本列表、导出结果、诊断摘要和可恢复动作
- 按 `user_message_key` 渲染用户提示，不得直接暴露原始错误栈

客户端约束如下：

- 客户端可缓存预览和轻量摘要，但不得作为正式版本来源
- 客户端不得绕过 `Run Orchestrator` 直接修改节点状态
- 客户端发起局部再生成时，必须显式携带所基于的版本标识

### 4.10.4 本地处理服务职责

本地处理服务职责固定如下：

- 接收客户端发起的项目运行、恢复执行和局部再生成请求
- 作为 `ProjectRunStatus` 与 `TaskNodeStatus` 的唯一写入方
- 按 `4.6.2` 的阶段依赖关系编排自动任务和人工阻塞节点
- 调用能力提供层并汇总结果为统一产物格式
- 向 `Artifact & Version Store` 写入可版本化中间产物
- 在失败、降级、恢复和重试时向 `Diagnostic Reporter` 发出结构化事件

服务层约束如下：

- 服务层不得把特定模型或第三方工具的内部状态直接暴露给客户端作为产品状态
- 服务层必须在恢复执行前先校验依赖版本是否仍有效
- 服务层必须支持并行执行 `story_parsing` 与 `media_analysis`，但不得并行推进需要人工确认的下游节点

### 4.10.5 能力提供层边界

能力提供层只定义能力类别、输入输出和替换原则，不把具体技术选型写成 V1 验收前提。

| 能力类别 | 最低输入 | 最低输出 | 替换原则 |
|---|---|---|---|
| 元数据提取 | 原始媒体文件 | 时间、地点、时长、方向、基础可读性信息 | 可替换实现必须保持字段语义一致 |
| 镜头切分与素材检测 | 视频文件、图片文件 | 镜头区间、素材质量信号、可用性评分 | 可替换实现不得改变 `media_analysis_pack` 的字段合同 |
| 语音识别与字幕对齐 | 视频音频流 | 转写文本、时间戳、说话片段 | 结果必须可用于字幕与原声判断，不能只返回全文文本 |
| 视觉标签与相似度 | 镜头帧、图片、故事段落提示 | 场景标签、人物线索、语义相似信号 | 不得把供应商私有评分直接当产品级 `match_confidence` |
| 文本理解 | 游记文本、故事上下文 | 故事段落、情绪与事件线索、旁白改写结果 | 输出必须可解释并支持低结构回退 |
| TTS | 旁白文本、音色标识 | 可混音的语音文件、时长和切句信息 | 音色实现可替换，但 `tts_voice` 语义必须稳定 |
| 渲染与混音 | 时间线、字幕、音轨计划 | 导出视频、音频和相关日志 | 导出失败时必须支持 `re_export_only`，不得清理上游版本 |

能力层约束如下：

- 任一能力调用失败时，必须返回可映射到 `failure_type` 的结构化错误，而不是只返回自由文本
- 任一能力若支持轻量模式，必须由服务层触发切换，不能自行更改项目模式
- 视觉、文本、TTS 等能力的具体实现允许升级替换，但不得改变上层 `ArtifactVersion` 和 `DiagnosticBundle` 的合同

### 4.10.6 存储与版本边界

所有中间产物必须通过统一的 `ArtifactVersion` 模型持久化。

| 产物名 | 用途 | 上游依赖 | 失效条件 |
|---|---|---|---|
| `asset_index` | 素材索引与基础媒体清单 | `ProjectInputContract` | 导入素材集合变化 |
| `story_version` | 已确认故事骨架 | 候选故事骨架草案、用户确认 | 用户修改段落顺序、合并、删除、高光标记 |
| `media_analysis_pack` | 镜头切分、质量评分、原声兴趣信号 | `asset_index` | 素材集合变化或分析模式变化导致版本不兼容 |
| `alignment_version` | 段落与镜头候选匹配结果 | `story_version`、`media_analysis_pack` | 故事骨架变化、素材分析版本变化 |
| `highlight_selection_version` | 已确认高光选择、禁用规则、必保留镜头 | `alignment_version`、用户确认 | 用户替换候选镜头或返回上一步修改 |
| `timeline_version` | 可执行时间线与节奏规划 | `story_version`、`highlight_selection_version` | 高光选择变化、短版重排、上游版本失效 |
| `narration_pack` | 旁白文案、TTS 语音、字幕计划 | `story_version`、`timeline_version`、`tts_voice` | 旁白重写、音色切换、时间线变化 |
| `audio_mix_pack` | 混音计划和中间音频产物 | `timeline_version`、`narration_pack`、`bgm_asset` | 更换 `BGM`、旁白重写、时间线变化 |
| `export_bundle` | 成片与导出清单 | `timeline_version`、`audio_mix_pack` | 导出参数变化或重导出 |
| `diagnostic_bundle` | 运行摘要、段落诊断、回退事件和日志 | 全流程事件流 | 缺失文件时应补写，不影响已有成片版本 |

存储边界必须满足以下要求：

- 每个 `ArtifactVersion` 都必须记录 `version_id`、`producer_stage`、`upstream_versions`、`created_at`、`storage_path`
- 任何下游产物被读取前，都必须先校验其 `upstream_versions` 与当前活动版本是否一致
- 导出失败时不得删除 `timeline_version`、`narration_pack`、`audio_mix_pack`

### 4.10.7 执行模型与并发约束

执行模型必须满足以下规则：

- `input_validation` 成功前，任何自动分析任务都不得启动
- `asset_indexing` 完成后，仅允许 `story_parsing` 与 `media_analysis` 并行执行
- 任一人工确认节点激活后，所有依赖该节点的下游自动任务必须保持 `blocked`
- 模块级重试必须从最近有效边界恢复，不得默认清空全量缓存
- 局部再生成必须视为新的运行版本，但默认继承上一次确认过的故事骨架和高光选择
- 同一项目同时只能存在一个写入正式活动版本的编排流程；若用户发起新的重算请求，旧流程必须被 `canceled` 或挂起

### 4.10.8 接口与事件边界

V1 至少需要固定以下文档级接口对象：

#### `StageContract`

| 字段 | 含义 |
|---|---|
| `stage_name` | 阶段唯一标识，必须与 `4.6.2` 一致 |
| `owner_module` | 阶段主责模块 |
| `required_inputs[]` | 执行前必须可用的上游输入或版本 |
| `produced_outputs[]` | 阶段成功或降级时必须产出的产物 |
| `allowed_statuses[]` | 该阶段允许进入的节点状态集合 |
| `failure_types[]` | 允许抛出的统一失败分类 |
| `recovery_actions[]` | 允许采用的恢复动作集合 |

#### `ArtifactVersion`

| 字段 | 含义 |
|---|---|
| `artifact_name` | 产物名称，如 `story_version` |
| `version_id` | 产物版本唯一标识 |
| `producer_stage` | 生成该产物的阶段 |
| `producer_run_id` | 生成该版本的运行实例 |
| `upstream_versions` | 上游依赖版本映射 |
| `created_at` | 生成时间 |
| `status` | 当前版本状态，如 `active`、`superseded`、`invalidated` |
| `storage_path` | 产物落盘位置 |
| `invalidated_by` | 失效原因或替换来源 |

#### `UserDecision`

| 字段 | 含义 |
|---|---|
| `decision_id` | 用户动作唯一标识 |
| `node_name` | 所属交互节点 |
| `decision_type` | 动作类型，如确认、替换、跳过、保留版本 |
| `decision_payload` | 结构化动作内容 |
| `based_on_version` | 用户决策所基于的版本标识 |
| `operator` | 触发用户或本地操作者 |
| `decided_at` | 动作时间 |

#### `RecoveryActionRecord`

| 字段 | 含义 |
|---|---|
| `failure_type` | 触发恢复的失败分类 |
| `failure_code` | 结构化失败码 |
| `recovery_action` | 实际采用的恢复动作 |
| `resume_from` | 恢复起点阶段或版本 |
| `preserved_versions[]` | 恢复时继续复用的版本 |
| `triggered_at` | 恢复触发时间 |

#### `ModuleOutputPolicy`

| 字段 | 含义 |
|---|---|
| `module_name` | 模块名称 |
| `supports_degraded` | 是否允许以 `degraded` 完成 |
| `requires_diagnostic_bundle` | 是否必须同步写诊断输出 |
| `reusable_when` | 允许复用旧版本的前提 |
| `must_block_when` | 必须阻断并等待人工或修复的条件 |

#### `CapabilityBoundary`

| 字段 | 含义 |
|---|---|
| `capability_name` | 能力类别名称 |
| `owned_by_service` | 是否由本地处理服务统一调度 |
| `input_contract` | 该能力允许接收的正式输入 |
| `output_contract` | 该能力必须返回的正式输出 |
| `swappable` | 是否允许替换实现 |
| `product_invariants[]` | 替换后仍不得破坏的产品级约束 |

#### `DiagnosticBundle`

| 字段 | 含义 |
|---|---|
| `run_summary` | 项目级状态、失败节点、恢复入口和提示键 |
| `input_validation_report` | 输入校验与软风险结果 |
| `segment_diagnostics` | 段落级覆盖、置信度和用户决策 |
| `fallback_events` | 回退事件流 |
| `node_status_timeline` | 节点状态演进时间线 |
| `export_report` | 导出过程与重导出入口 |
| `runtime_logs` | 原始日志与错误栈位置 |

接口边界必须满足以下要求：

- 文档级接口字段名在后续实现中允许做语言映射，但语义不得改变
- 任一模块和能力实现都不得自行扩展一套与上述接口平行的状态、版本或诊断协议
- 用户界面、日志、诊断文件之间必须通过这些统一对象互相追溯

### 4.10.9 本地与联网边界

V1 默认本地执行，联网仅作为增强能力。

必须明确以下规则：

- 素材文件、故事骨架、高光选择、时间线和导出产物默认不离开本机
- 若后续引入可选云端增强，必须明确标记触发条件、上传范围和联网失败后的回退路径
- 联网失败不得使已可在本地完成的主链路直接失败
- 任一云端增强结果若参与正式产物生成，仍必须转换为统一 `ArtifactVersion` 后再进入下游模块

### 4.10.10 V1 技术非目标

V1 技术方案不以以下能力为前提：

- 插件市场或通用插件运行时
- 远程任务队列、分布式执行和多机协同
- 专业级时间线编辑器内核
- 深度剪映工程格式读写
- 长期用户画像和跨项目偏好学习系统

---

## 5. 后续可选文档动作

当前文档已补齐运行机制、输入与诊断表达、模块需求和技术方案四个核心约束层。若后续继续扩写，建议优先补充以下内容：

1. 增加“验收用例与测试场景”，把 `V1 成立条件`、回退触发、局部再生成和导出失败恢复落成可执行验收矩阵
2. 增加“关键交互稿与页面状态”，把故事骨架确认、高光确认、局部再生成三类页面的展示字段和操作反馈写定
3. 增加“数据字典与产物 schema”，将 `ProjectInputContract`、`ArtifactVersion`、`UserDecision`、`DiagnosticBundle` 扩成统一字段表

如果后续继续扩写，建议把《AI旅行Vlog剪辑系统方案.md》保留为愿景与方案文档，把本文作为正式 PRD 主文档继续演进。
