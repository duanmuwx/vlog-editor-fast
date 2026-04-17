# AI 旅行 Vlog 剪辑系统 - 详细开发计划

## Context

本计划是为 AI 编程工具设计的详细实现指南。系统目标是将旅行游记转化为 2-4 分钟的自动化 Vlog，采用故事优先、多模态对齐的设计理念。项目当前仅有文档，无实现代码。计划从项目初始化开始，指导完整系统实现。

---

## 1. 项目初始化与技术栈

### 1.1 项目结构

```
vlog-editor-fast/
├── src/
│   ├── client/                 # 桌面客户端 (Electron/Tauri)
│   │   ├── components/         # UI 组件
│   │   ├── pages/              # 页面
│   │   └── services/           # 客户端服务
│   ├── server/                 # 本地处理服务
│   │   ├── orchestrator/       # 运行编排器
│   │   ├── modules/            # 核心模块实现
│   │   ├── capabilities/       # 能力提供层
│   │   └── storage/            # 存储与版本管理
│   └── shared/                 # 共享类型与常量
├── tests/                      # 测试套件
├── docs/                       # 现有文档
└── config/                     # 配置文件
```

### 1.2 技术栈选择

**客户端**：
- Electron 或 Tauri（本地桌面应用）
- React + TypeScript（UI 框架）
- 理由：跨平台、本地优先、与处理服务通信

**服务端**：
- Python 3.10+（核心处理服务）
- FastAPI（IPC 通信）
- SQLite（项目元数据存储）
- 理由：AI/ML 生态完善、媒体处理库丰富、易于集成模型

**媒体处理**：
- FFmpeg（视频/音频处理）
- OpenCV（视觉分析）
- librosa（音频分析）
- Whisper（语音识别）

**模型与 NLP**：
- LLM（游记解析、旁白生成）- 可选云端或本地
- 视觉模型（场景识别、相似度）
- TTS（文本转语音）

---

## 2. 核心模块实现顺序

### 2.1 第一阶段：基础设施与输入处理

**目标**：建立项目管理、输入校验、素材索引的基础框架

**模块**：
1. **Project Workspace** - 项目创建、配置管理
2. **Input Validator** - 输入校验与风险识别
3. **Asset Indexing** - 素材扫描、元数据提取

**关键产物**：
- `ProjectInputContract` 数据模型
- `InputValidationReport` 校验结果
- `asset_index` 素材索引

**验收标准**：
- 能创建项目并导入素材
- 能识别并报告输入风险
- 能生成完整的素材索引

---

### 2.2 第二阶段：故事解析与确认

**目标**：实现游记解析、故事骨架生成与用户确认流程

**模块**：
1. **Story Parser** - 游记解析为故事段落
2. **Story Skeleton Confirmation** - 故事骨架确认 UI 与逻辑

**关键产物**：
- `story_version` - 已确认故事骨架
- 故事段落列表（摘要、时间范围、重要度）

**验收标准**：
- 能将游记拆分为 3-8 个故事段落
- 用户可合并、删除、排序、标记段落
- 能冻结故事骨架版本

---

### 2.3 第三阶段：素材分析与对齐

**目标**：实现素材分析、故事与素材对齐、高光确认

**模块**：
1. **Media Analyzer** - 镜头切分、质量评分、原声检测
2. **Alignment Engine** - 故事段落与镜头匹配
3. **Highlight Confirmation** - 高光确认 UI 与逻辑

**关键产物**：
- `media_analysis_pack` - 镜头分析结果
- `alignment_version` - 段落与镜头匹配
- `highlight_selection_version` - 已确认高光选择

**验收标准**：
- 能检测视频镜头边界
- 能为每个故事段落生成 3-5 个候选镜头
- 用户可接受、替换、禁用、标记镜头
- 能处理素材不足的降级方案（照片+旁白过渡）

---

### 2.4 第四阶段：成片生成与导出

**目标**：实现时间线规划、旁白生成、音频混合、视频渲染

**模块**：
1. **Edit Planner** - 时间线与节奏规划
2. **Narration / TTS / Subtitle Engine** - 旁白、配音、字幕
3. **Audio Composer** - 音频混合
4. **Renderer & Exporter** - 视频渲染与导出

**关键产物**：
- `timeline_version` - 可执行时间线
- `narration_pack` - 旁白、TTS、字幕
- `audio_mix_pack` - 混音结果
- `export_bundle` - 最终成片

**验收标准**：
- 能生成 2-4 分钟的成片
- 旁白连贯、字幕准确
- 音频混合平衡（旁白、原声、BGM）
- 导出 MP4、字幕、配音文件

---

### 2.5 第五阶段：局部再生成与版本管理

**目标**：实现三类局部再生成、版本切换、失败恢复

**模块**：
1. **Run Orchestrator** - 运行编排、状态机、恢复逻辑
2. **Artifact & Version Store** - 版本管理、缓存失效
3. **Diagnostic Reporter** - 诊断输出

**关键产物**：
- 版本历史与切换
- 三类局部再生成：仅重写旁白、仅更换 BGM、压缩时长
- 诊断日志与恢复入口

**验收标准**：
- 能进行至少 1 次局部再生成
- 版本间可快速切换
- 失败时能定位到具体模块
- 支持模块级重试

---

## 3. 关键设计决策

### 3.1 双层状态机

**项目级状态** (`ProjectRunStatus`)：
- `draft` → `ready` → `running` → `awaiting_user` → `completed` / `failed`

**节点级状态** (`TaskNodeStatus`)：
- `pending` → `running` → `succeeded` / `degraded` / `failed_retryable` / `failed_manual`

**实现要点**：
- `Run Orchestrator` 是唯一状态写入方
- 每个状态变化都必须记录时间戳和原因
- 支持从任意失败点恢复

### 3.2 版本化产物与缓存管理

**核心原则**：
- 每个中间产物都是版本化的 (`ArtifactVersion`)
- 版本记录上游依赖关系
- 下游产物读取前必须校验上游版本是否有效
- 用户修改时只失效受影响的下游版本

**实现要点**：
- 使用 SQLite 记录版本元数据
- 文件系统存储实际产物
- 支持版本复用和增量更新

### 3.3 置信度与回退策略

**回退触发表**（来自 PRD 4.4.4）：
- `note_too_short` → 简化叙事
- `metadata_sparse` → 语义优先对齐
- `asset_coverage_low` → 替代呈现单元
- `segment_match_low_confidence` → 人工确认或跳过
- `resource_limited` → 轻量模式

**实现要点**：
- 统一的 `FallbackReason` 和 `FallbackAction` 枚举
- 每个回退都必须记录诊断信息
- 高重要度段落不得静默跳过

### 3.4 三段式轻交互

**必选交互节点**：
1. 故事骨架确认 - 用户审阅、修改、确认
2. 高光确认 - 用户审阅、替换、禁用镜头
3. 局部再生成 - 用户选择再生成类型

**实现要点**：
- 每个节点都必须支持返回上一步
- 用户决策必须结构化记录
- 不得跳过必选节点

---

## 4. 数据模型与 API 设计

### 4.1 核心数据模型

```python
# ProjectInputContract - 项目输入
{
  "project_name": str,
  "travel_note": str,
  "media_files": List[str],  # 文件路径
  "bgm_asset": str,
  "tts_voice": str,
  "metadata_pack": Optional[Dict]  # GPS、EXIF 等
}

# ArtifactVersion - 版本化产物
{
  "artifact_name": str,
  "version_id": str,
  "producer_stage": str,
  "upstream_versions": Dict[str, str],
  "created_at": datetime,
  "status": str,  # active, superseded, invalidated
  "storage_path": str
}

# UserDecision - 用户决策
{
  "decision_id": str,
  "node_name": str,
  "decision_type": str,  # confirm, replace, skip, mark
  "decision_payload": Dict,
  "based_on_version": str,
  "decided_at": datetime
}

# DiagnosticBundle - 诊断输出
{
  "run_summary": Dict,
  "input_validation_report": Dict,
  "segment_diagnostics": List[Dict],
  "fallback_events": List[Dict],
  "node_status_timeline": List[Dict],
  "export_report": Dict,
  "runtime_logs": str
}
```

### 4.2 客户端-服务端 IPC 接口

```python
# 主要 API 端点
POST /api/projects/create
POST /api/projects/{project_id}/run
POST /api/projects/{project_id}/confirm-skeleton
POST /api/projects/{project_id}/confirm-highlights
POST /api/projects/{project_id}/regenerate
GET /api/projects/{project_id}/status
GET /api/projects/{project_id}/diagnostics
```

---

## 5. 实现指南与技术细节

### 5.1 故事解析模块 (Story Parser)

**输入**：游记文本、项目配置
**输出**：故事段落列表、解析摘要

**实现步骤**：
1. 文本预处理（分句、分段）
2. 事件识别（使用 NLP 或 LLM）
3. 时间线索提取（日期、时间表达）
4. 地点线索提取（地名识别）
5. 段落聚类与摘要生成
6. 重要度评分

**关键约束**：
- 游记过短时（<150 字）切换简化叙事
- 低结构游记时降级为时间顺序
- 必须输出置信度和回退原因

### 5.2 素材分析模块 (Media Analyzer)

**输入**：素材索引、项目配置
**输出**：镜头分析包

**实现步骤**：
1. 视频镜头切分（场景变化检测）
2. 镜头质量评分（清晰度、稳定性）
3. 原声检测（语音、环境音）
4. 视觉特征提取（场景标签、人物、物体）
5. 照片分析（清晰度、内容标签）

**关键约束**：
- 支持轻量模式（快速但质量下降）
- 必须处理部分文件损坏的情况
- 输出结构化的镜头候选集合

### 5.3 对齐引擎 (Alignment Engine)

**输入**：故事版本、媒体分析包
**输出**：对齐版本、段落候选镜头

**实现步骤**：
1. 多模态特征对齐（文本、视觉、时间、地点）
2. 候选镜头排序（置信度评分）
3. 替代呈现单元生成（照片、地点卡、文字卡）
4. 低置信检测与标记

**关键约束**：
- 元数据缺失时切换语义优先对齐
- 高重要度段落必须至少有 1 个候选
- 必须输出匹配置信度和原因

### 5.4 编辑规划模块 (Edit Planner)

**输入**：故事版本、高光选择版本
**输出**：时间线版本

**实现步骤**：
1. 镜头时长规划（2-4 分钟目标）
2. 节奏与转场规划
3. 旁白时长分配
4. 原声保留决策
5. 时间线生成

**关键约束**：
- 压缩短版时只能复用已确认的骨架和高光
- 必须保留"必须保留"的段落和镜头
- 输出可执行的时间线结构

### 5.5 旁白与 TTS 模块 (Narration / TTS / Subtitle Engine)

**输入**：故事版本、时间线版本、TTS 音色
**输出**：旁白包（文案、音频、字幕）

**实现步骤**：
1. 旁白文案生成（基于故事段落）
2. 文案优化与分句
3. TTS 音频生成
4. 字幕时间对齐
5. 字幕文件生成

**关键约束**：
- 旁白连续播报不超过 20 秒
- 必须支持仅重写旁白的局部再生成
- 输出结构化的旁白计划

### 5.6 音频混合模块 (Audio Composer)

**输入**：时间线版本、旁白包、BGM、原声
**输出**：混音包

**实现步骤**：
1. 音轨规划（旁白、原声、BGM）
2. 音量平衡
3. 淡入淡出效果
4. 混音生成

**关键约束**：
- 必须保留至少 3 处原声时刻
- 支持仅更换 BGM 的局部再生成
- 输出混音计划和中间音频

### 5.7 渲染与导出模块 (Renderer & Exporter)

**输入**：时间线版本、混音包、字幕
**输出**：导出包（MP4、字幕、配音、manifest）

**实现步骤**：
1. 视频片段拼接
2. 字幕烧录
3. 音频混合
4. 视频编码与导出
5. 诊断文件生成

**关键约束**：
- 导出失败时保留中间产物
- 支持仅重新导出的恢复
- 输出完整的诊断包

---

## 6. 验收标准与测试策略

### 6.1 标准旅行项目定义

- 视频：20-50 个
- 图片：300-600 张
- 游记：3000-5000 字
- 原始视频总时长：60-120 分钟
- 设备：MacBook Air M1，8GB RAM

### 6.2 北极星指标

- 能生成 2-4 分钟、16:9 横屏的成片
- 用户评分 ≥ 4/5
- 总处理时长 ≤ 120 分钟
- 人工干预步骤 ≤ 3 次

### 6.3 关键验收用例

1. **标准流程** - 从导入到成片的完整流程
2. **故事骨架调整** - 用户修改段落后重新对齐
3. **高光确认与替代呈现** - 处理素材不足的情况
4. **局部再生成** - 三类再生成都能成功
5. **低置信处理** - 显式提示和人工确认
6. **导出失败恢复** - 支持重新导出

### 6.4 测试策略

**单元测试**：
- 每个模块的核心逻辑
- 数据模型的序列化/反序列化
- 状态机的状态转移

**集成测试**：
- 模块间的数据流
- 版本依赖关系
- 恢复执行流程

**端到端测试**：
- 完整的项目流程
- 局部再生成流程
- 失败恢复流程

**性能测试**：
- 标准项目的处理时长
- 内存占用
- 磁盘占用

---

## 7. 实现时间表

### Phase 1: 基础设施 (2-3 周)
- 项目结构、技术栈初始化
- 数据模型定义
- 客户端-服务端通信框架
- 项目管理、输入校验、素材索引

### Phase 2: 故事解析 (2-3 周)
- Story Parser 实现
- Story Skeleton Confirmation UI
- 故事骨架确认流程

### Phase 3: 素材分析与对齐 (3-4 周)
- Media Analyzer 实现
- Alignment Engine 实现
- Highlight Confirmation UI
- 高光确认流程

### Phase 4: 成片生成 (3-4 周)
- Edit Planner 实现
- Narration / TTS / Subtitle Engine 实现
- Audio Composer 实现
- Renderer & Exporter 实现

### Phase 5: 版本管理与恢复 (2-3 周)
- Run Orchestrator 实现
- Artifact & Version Store 实现
- Diagnostic Reporter 实现
- 局部再生成流程

### Phase 6: 测试与优化 (2-3 周)
- 单元测试、集成测试、端到端测试
- 性能优化
- 文档完善

**总计**：14-20 周

---

## 8. 关键风险与缓解策略

| 风险 | 影响 | 缓解策略 |
|------|------|---------|
| LLM 游记解析质量不稳定 | 故事骨架质量差 | 提供用户确认节点，支持手动调整 |
| 视觉对齐置信度低 | 镜头匹配不准 | 多模态对齐，支持用户替换 |
| 处理时长超预期 | 用户体验差 | 支持轻量模式，显示进度 |
| 素材质量差异大 | 成片质量不稳定 | 替代呈现单元，显式降级提示 |
| 本地资源不足 | 处理失败 | 支持模块级重试，资源监控 |

---

## 9. 验证与交付

### 9.1 验收检查清单

- [ ] 所有 10 个关键用例都能正确执行
- [ ] 功能完整性项都已实现
- [ ] 性能指标都达到目标
- [ ] 质量指标都达到目标
- [ ] 稳定性指标都达到目标
- [ ] 用户评分 ≥ 4/5
- [ ] 所有失败场景都能正确处理和恢复

### 9.2 交付物

- 可执行的桌面应用
- 完整的诊断日志和恢复入口
- 用户文档和快速开始指南
- 技术文档和 API 文档

---

## 10. 后续迭代方向

- V1.5：多风格模板、高级编辑能力
- V2：云端协同、多人协作、跨设备同步
- V3：专业级时间线编辑、深度剪映互通

