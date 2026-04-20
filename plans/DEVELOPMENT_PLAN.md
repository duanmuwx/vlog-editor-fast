# Vlog Editor Fast - 剩余开发计划

## 项目现状

- **完成度**：85-90%（所有后端核心功能已实现）
- **已实现**：18个核心模块、20+个API端点、44个测试文件
- **待实现**：前端界面、部署配置、部署指南文档

## 开发优先级

1. **Phase 7: 前端开发** - Electron + React 桌面应用
2. **Phase 8: 部署配置** - Docker 容器化 + 本地部署脚本
3. **Phase 9: 文档完善** - 部署指南 + 用户手册

---

## Phase 7: 前端开发（Electron + React，对齐当前仓库）

### 7.1 目标与原则

**目标**：交付一个基于 Electron + React 的桌面端，能够直接编排当前 FastAPI 后端已经实现的工作流，完成：

1. 项目创建/打开
2. 输入校验
3. 故事解析与骨架确认
4. 媒体分析、镜头对齐与高光确认
5. 时间线生成、旁白生成、音频混合、最终渲染导出
6. 导出历史查看

**核心原则**：

- 前端设计必须以**当前后端真实接口**为准，不重新假设一套“理想 API”
- Phase 7 分为 **MVP 主流程** 和 **增强能力** 两层，先保证完整可用，再承接高级能力
- 桌面端以“本地文件路径 + 本地项目工作区”为核心，不按 Web 上传模型设计
- 运行模式采用：**开发环境外连后端、生产环境由 Electron 拉起后端**

### 7.2 技术栈

| 组件 | 技术 | 版本建议 | 说明 |
|------|------|----------|------|
| 桌面框架 | Electron | 最新稳定版 | 跨平台桌面壳 |
| 前端框架 | React | 18+ | 生态成熟 |
| 语言 | TypeScript | 5.0+ | 类型安全 |
| UI组件库 | Ant Design | 5.0+ | 中文友好，表单/表格/步骤条完备 |
| 状态管理 | Redux Toolkit | 最新 | 管理项目、工作流、产物状态 |
| HTTP客户端 | Axios | 最新 | 调用 FastAPI |
| 构建工具 | Vite | 最新 | 渲染进程开发体验好 |
| 打包工具 | electron-builder | 最新 | 桌面端打包 |

### 7.3 运行架构

#### 7.3.1 开发模式

- 渲染进程通过 `VITE_API_BASE_URL` 连接本地启动的 FastAPI
- 开发命令仍然分开执行：
  - 后端：`uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000`
  - 前端：`cd vlog-editor-desktop && npm run dev`

#### 7.3.2 生产模式

- Electron 主进程负责拉起后端子进程并做 `/health` 探活
- 渲染进程只感知 API 地址，不直接负责启动 Python 服务
- 打包阶段真正的 Python 运行时与依赖收敛由 **Phase 8** 完成

#### 7.3.3 安全边界

- 仅保留 `src/main/preload.ts` 作为 preload 入口
- Electron 配置必须启用：
  - `contextIsolation: true`
  - `nodeIntegration: false`
- 通过 `contextBridge` 暴露白名单能力：
  - 选择本地媒体文件
  - 打开导出目录
  - 打开导出文件
  - 读取后端健康状态

### 7.4 前端项目结构

```
vlog-editor-desktop/
├── src/
│   ├── main/
│   │   ├── main.ts                 # Electron 主进程
│   │   ├── preload.ts              # 安全桥接
│   │   └── backend/
│   │       └── launcher.ts         # 后端拉起与健康检查
│   ├── renderer/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── ProjectList.tsx
│   │   │   ├── ProjectSetupWizard.tsx
│   │   │   ├── ValidationResult.tsx
│   │   │   ├── SkeletonReview.tsx
│   │   │   ├── HighlightReview.tsx
│   │   │   ├── RenderCenter.tsx
│   │   │   └── ExportHistory.tsx
│   │   ├── components/
│   │   │   ├── SegmentEditor.tsx
│   │   │   ├── CandidatePicker.tsx
│   │   │   ├── TimelineSummary.tsx
│   │   │   ├── VersionHistoryDrawer.tsx
│   │   │   └── DiagnosticsPanel.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── ipc.ts
│   │   ├── store/
│   │   │   ├── projectSlice.ts
│   │   │   ├── creationDraftSlice.ts
│   │   │   ├── workflowSlice.ts
│   │   │   ├── artifactSlice.ts
│   │   │   ├── runSlice.ts
│   │   │   └── store.ts
│   │   ├── types/
│   │   │   └── api.ts
│   │   └── styles/
│   │       └── global.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── electron-builder.yml
```

### 7.5 页面与工作流设计

#### 7.5.1 ProjectList

**职责**：

- 展示所有项目
- 打开项目进入工作流
- 删除项目
- 进入新建向导

**依赖接口**：

```
GET /api/projects
GET /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

#### 7.5.2 ProjectSetupWizard

> 用一个“项目创建向导”替代原计划中的 `ProjectCreate + MediaUpload + StoryInput`

**职责**：

- 填写项目名称
- 输入 travel note
- 通过 Electron 选择本地媒体文件
- 选择 BGM、TTS 配置、metadata pack（可选）
- 一次性提交创建请求

**注意**：

- 当前后端创建项目需要提交完整 `ProjectInputContract`
- 因此桌面端不能采用“先创建空项目，再上传文件”的模式

**依赖接口**：

```
POST /api/projects/create
```

#### 7.5.3 ValidationResult

**职责**：

- 展示创建返回的 `validation_report`
- 展示创建返回的 `asset_index`
- 允许用户在进入下一阶段前检查输入质量
- 支持重新触发校验

**依赖接口**：

```
POST /api/projects/{project_id}/validate
GET /api/projects/{project_id}/assets
```

#### 7.5.4 SkeletonReview

**职责**：

- 触发故事解析
- 展示当前 skeleton
- 支持段落排序与编辑确认
- 支持“重新生成骨架”

**实现约束**：

- 当前后端没有单独的 `POST /skeleton/regenerate`
- “重新生成”在前端语义上等价于再次调用 `POST /story/parse`
- 骨架确认页以“排序、删除、合并”等后端已支持的编辑语义为准

**依赖接口**：

```
POST /api/projects/{project_id}/story/parse
GET /api/projects/{project_id}/skeleton/current
GET /api/projects/{project_id}/skeleton/{skeleton_id}
POST /api/projects/{project_id}/skeleton/{skeleton_id}/confirm
```

#### 7.5.5 HighlightReview

**职责**：

- 执行媒体分析
- 执行故事段落与镜头候选对齐
- 展示每个 segment 的候选镜头
- 允许用户逐段确认高光镜头

**实现约束**：

- 当前后端没有 `GET /highlights` 和 `POST /highlights/regenerate`
- 当前真实流程应为：
  1. `analyze-media`
  2. `align-media`
  3. `alignment-candidates/{segment_id}`
  4. `confirm-highlights`
- “重新生成高光”的语义改为重新运行对齐

**依赖接口**：

```
POST /api/projects/{project_id}/analyze-media
GET /api/projects/{project_id}/media-analysis
POST /api/projects/{project_id}/align-media
GET /api/projects/{project_id}/alignment-candidates/{segment_id}
POST /api/projects/{project_id}/confirm-highlights
GET /api/projects/{project_id}/highlights/current
```

#### 7.5.6 RenderCenter

> 用 `RenderCenter` 替代原计划中的 `Preview`

**职责**：

- 生成时间线
- 查看时间线摘要
- 生成旁白
- 混合音频
- 执行最终渲染导出

**实现约束**：

- 当前后端没有 preview 相关接口
- 因此前端不能承诺“实时预览参数调节”
- MVP 只展示阶段结果与摘要，不实现自由时间线拖拽编辑

**依赖接口**：

```
POST /api/projects/{project_id}/edit-plan
GET /api/projects/{project_id}/versions/timeline
GET /api/projects/{project_id}/timeline/{version_id}
POST /api/projects/{project_id}/generate-narration
POST /api/projects/{project_id}/mix-audio
POST /api/projects/{project_id}/render-export
```

#### 7.5.7 ExportHistory

**职责**：

- 查看导出历史
- 展示导出文件路径与状态
- 打开文件、打开文件夹

**依赖接口**：

```
GET /api/projects/{project_id}/exports
```

### 7.6 增强能力（基于 Phase 5 已有后端能力）

这部分不阻塞 MVP，但必须在 Phase 7 后半段承接，避免后端能力“已存在但前端不可用”。

#### 7.6.1 版本历史与切换

**能力**：

- 查看 artifact 版本历史
- 切换当前激活版本
- 比较两个版本的差异

**依赖接口**：

```
GET /api/projects/{project_id}/versions/{artifact_type}
POST /api/projects/{project_id}/versions/{artifact_type}/{version_id}/switch
GET /api/projects/{project_id}/versions/{artifact_type}/{v1_id}/diff/{v2_id}
```

#### 7.6.2 运行记录与诊断

**能力**：

- 查看 runs
- 查看单次 run 的诊断包
- 支持 markdown/html/json 诊断内容展示

**依赖接口**：

```
GET /api/projects/{project_id}/runs
GET /api/projects/{project_id}/runs/{run_id}/diagnostics
GET /api/projects/{project_id}/diagnostics/{run_id}
```

#### 7.6.3 失败恢复与重试

**能力**：

- 从失败点恢复
- 对特定 stage 执行 retry

**依赖接口**：

```
POST /api/projects/{project_id}/runs/{run_id}/resume
POST /api/projects/{project_id}/runs/{run_id}/retry/{stage_name}
POST /api/projects/{project_id}/regenerate/{regen_type}
```

### 7.7 状态管理设计（Redux Toolkit）

#### 7.7.1 `projectSlice`

负责：

- 项目列表
- 当前项目摘要
- 当前项目详情
- 项目打开/删除状态

#### 7.7.2 `creationDraftSlice`

负责：

- 新建向导草稿
- `ProjectInputContract` 对应字段
- 本地已选媒体路径

#### 7.7.3 `workflowSlice`

负责：

- validation report
- asset index
- skeleton
- media analysis
- alignment candidates
- highlights
- 当前工作流阶段

#### 7.7.4 `artifactSlice`

负责：

- timeline
- narration
- audio mix
- exports
- active version histories

#### 7.7.5 `runSlice`

负责：

- runs 列表
- diagnostics 内容
- retry / resume 状态

### 7.8 API 服务层设计

**文件**：`src/renderer/services/api.ts`

```typescript
class ApiService {
  private baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

  // 项目
  getProjects(): Promise<ProjectSummary[]>
  createProject(input: ProjectInputContract): Promise<CreateProjectResponse>
  getProject(projectId: string): Promise<ProjectDetailResponse>
  deleteProject(projectId: string): Promise<void>

  // 校验与资产
  validateProject(projectId: string): Promise<ValidationResponse>
  getAssets(projectId: string): Promise<AssetIndexResponse>

  // 骨架
  parseStory(projectId: string): Promise<StorySkeleton>
  getCurrentSkeleton(projectId: string): Promise<StorySkeleton>
  getSkeleton(projectId: string, skeletonId: string): Promise<StorySkeleton>
  confirmSkeleton(projectId: string, skeletonId: string, edits: SkeletonEdit[]): Promise<StorySkeleton>

  // 高光
  analyzeMedia(projectId: string): Promise<MediaAnalysis>
  getMediaAnalysis(projectId: string): Promise<MediaAnalysis>
  alignMedia(projectId: string): Promise<AlignmentSummary>
  getAlignmentCandidates(projectId: string, segmentId: string): Promise<AlignmentCandidatesResponse>
  confirmHighlights(projectId: string, selections: HighlightSelectionInput[]): Promise<HighlightSelection[]>
  getCurrentHighlights(projectId: string): Promise<HighlightSelection[]>

  // 渲染导出
  createEditPlan(projectId: string): Promise<TimelineSummary>
  getVersionHistory(projectId: string, artifactType: string): Promise<VersionHistory>
  getTimeline(projectId: string, versionId: string): Promise<TimelineDetail>
  generateNarration(projectId: string): Promise<NarrationSummary>
  mixAudio(projectId: string): Promise<AudioMixSummary>
  renderExport(projectId: string): Promise<ExportSummary>
  getExports(projectId: string): Promise<ExportHistoryResponse>

  // 增强能力
  getRuns(projectId: string): Promise<RunHistoryResponse>
  getRunDiagnostics(projectId: string, runId: string, format?: string): Promise<DiagnosticBundle>
  retryStage(projectId: string, runId: string, stageName: string): Promise<void>
  resumeRun(projectId: string, runId: string): Promise<void>
}
```

### 7.9 需要补齐或调整的后端接口

为使桌面端可落地，需要在当前后端基础上做最小补口：

#### 7.9.1 新增项目列表接口

```
GET /api/projects
```

返回字段至少包含：

- `project_id`
- `project_name`
- `status`
- `created_at`
- `updated_at`
- 可选统计信息：`total_videos`、`total_photos`、`total_duration`

#### 7.9.2 新增项目删除接口

```
DELETE /api/projects/{project_id}
```

负责删除：

- 项目数据库
- 项目工作区目录

#### 7.9.3 扩展资产接口返回媒体明细

当前 `GET /api/projects/{project_id}/assets` 只有汇总信息，前端无法定位每个镜头对应的源文件。

需要扩展返回：

- `file_id`
- `file_path`
- `file_type`
- `file_size`
- `duration`
- `resolution`
- `creation_time`
- `has_audio`

#### 7.9.4 修正校验接口的重跑能力

当前 `POST /api/projects/{project_id}/validate` 无法基于数据库完整重建输入。

需要修正为可从已存储的：

- 项目元数据
- project config
- media_files

重新生成完整 `validation_report`。

### 7.10 开发步骤

#### Step 1：前后端契约对齐与最小补口（2-3天）

- 整理真实接口清单
- 完成 `GET /api/projects`
- 完成 `DELETE /api/projects/{project_id}`
- 扩展 `GET /assets`
- 修正 `POST /validate`

**交付结果**：

- 前端能够拿到项目列表、项目详情、资产明细和校验结果

#### Step 2：桌面壳与安全边界（2-3天）

- 搭建 Electron 主进程
- 实现 preload 与 IPC 白名单
- 实现开发/生产两种后端连接模式
- 增加后端健康检查

**交付结果**：

- 桌面端可安全启动并连接后端

#### Step 3：项目创建与打开（3-4天）

- 实现 ProjectList
- 实现 ProjectSetupWizard
- 实现 ValidationResult
- 接通本地文件选择器

**交付结果**：

- 用户可以从零创建项目并重新打开旧项目

#### Step 4：故事与高光主流程（5-7天）

- 实现 SkeletonReview
- 实现 SegmentEditor
- 实现 HighlightReview
- 实现 CandidatePicker

**交付结果**：

- 用户可以完成从 travel note 到 confirmed highlights 的全过程

#### Step 5：渲染与导出（4-5天）

- 实现 RenderCenter
- 实现 TimelineSummary
- 接通 narration / audio / render
- 实现 ExportHistory

**交付结果**：

- 用户可以在桌面端拿到导出结果并打开输出目录

#### Step 6：增强能力接入（3-4天）

- 版本历史
- diff 与切换
- runs 列表
- diagnostics 展示
- retry / resume 操作

**交付结果**：

- Phase 5 已实现的高级能力在桌面端可用

#### Step 7：测试与打包准备（3-4天）

- 单元测试
- Electron 端到端主流程测试
- 错误态测试
- 打包 smoke test

**交付结果**：

- 主流程与增强能力入口可验证

### 7.11 测试策略

#### 单元测试

- 表单校验
- Redux slices
- API adapter
- skeleton edits 映射逻辑
- alignment candidate 数据映射逻辑

#### 端到端测试

覆盖以下完整主流程：

1. 新建项目
2. 查看 validation result
3. 解析故事
4. 确认 skeleton
5. 分析媒体
6. 对齐候选镜头
7. 确认 highlights
8. 生成 timeline
9. 生成 narration
10. mix audio
11. render export
12. 查看 export history

#### 错误处理测试

- 后端未启动
- `/health` 探活失败
- 接口返回 4xx/5xx
- 无候选镜头
- 导出失败
- diagnostics 内容缺失
- 版本切换后 UI 状态未同步

### 7.12 排期估算

- **MVP 主流程**：14-19天
- **增强能力接入**：6-8天
- **总计**：20-27天

### 7.13 本阶段明确不做的内容

以下内容不纳入 Phase 7 MVP，避免前端承诺超出后端能力：

- 浏览器式文件上传进度条
- 实时 preview 参数调节
- 自由时间线拖拽编辑
- 导出百分比级实时进度
- 新增一套独立于当前后端的“前端专用接口”

---

## Phase 8: 部署配置

### 8.1 目标与交付边界

**目标**：交付一套与 Phase 7 一致的部署方案，覆盖：

1. 后端 Python 服务的可复用运行时镜像
2. 本地开发环境的一键初始化与启动脚本
3. Electron 桌面端生产包中对后端的内置启动能力
4. macOS / Linux 下统一的数据目录和配置约定

**本阶段明确区分三类场景**：

- **开发模式**：后端与桌面端分开启动，便于调试
- **容器模式**：仅用于后端开发、联调、集成测试，不作为桌面端生产交付形式
- **生产模式**：由 Electron 主进程拉起本地后端，用户直接运行桌面应用，不再手动启动 `uvicorn`

**本阶段不做**：

- 不提供浏览器版前端生产部署
- 不把 `Vite dev server` 视为正式交付物
- 不引入 Kubernetes、远程数据库或云端对象存储方案
- 不继续沿用“复制 `.env.example` 为容器内 `.env`”的做法

### 8.2 交付物清单

| 交付物 | 文件 | 用途 |
|--------|------|------|
| 后端运行时镜像 | `Dockerfile.backend` | 构建后端最小运行镜像 |
| 开发环境编排 | `docker-compose.dev.yml` | 本地启动后端容器，供开发/测试使用 |
| 本地初始化脚本 | `scripts/setup-local.sh` | 创建虚拟环境、安装依赖、检查系统工具 |
| 后端开发启动脚本 | `scripts/start-backend.sh` | 启动 FastAPI 并做健康检查 |
| 桌面端开发启动脚本 | `scripts/start-desktop-dev.sh` | 启动后端后再启动 Electron 桌面端 |
| Electron 后端拉起器 | `vlog-editor-desktop/src/main/backend/launcher.ts` | 生产模式拉起后端并轮询 `/health` |
| 打包配置 | `vlog-editor-desktop/electron-builder.yml` | 将 Python 运行时与后端代码一起打包 |

### 8.3 后端运行时镜像

**文件**：`Dockerfile.backend`

**设计原则**：

- 仅打包后端运行所需内容，不打包测试工具、格式化工具
- 依赖来源以 `pyproject.toml` 为准，不再以 `requirements.txt` 作为部署主入口
- 使用非 root 用户运行服务
- 提供 `/health` 健康检查
- 数据目录通过环境变量和挂载卷注入，不写死到 `/root/.vlog-editor`

**镜像要求**：

- 基础镜像：`python:3.10-slim`
- 系统依赖：`ffmpeg`，以及 OpenCV / 图像处理所需最小共享库
- 安装方式：`pip install .`
- 运行用户：`app`
- 默认工作目录：`/app`
- 默认数据目录：`/home/app/.vlog-editor`
- 启动命令：

```bash
uvicorn src.server.main:app --host 0.0.0.0 --port 8000
```

**必须补充的配套文件**：

- `.dockerignore`
- 容器健康检查：轮询 `http://127.0.0.1:8000/health`

### 8.4 开发用 Docker Compose

**文件**：`docker-compose.dev.yml`

**用途**：仅用于后端开发、联调和集成测试，不作为生产部署方案。

**服务定义**：

#### `backend`

- 基于 `Dockerfile.backend` 构建
- 端口映射：`8000:8000`
- 挂载源码目录以支持热重载
- 挂载应用数据目录到容器用户目录
- 启动命令启用 `--reload`
- 注入开发环境变量：
  - `APP_ENV=development`
  - `SERVER_HOST=0.0.0.0`
  - `SERVER_PORT=8000`
  - `APP_DATA_DIR=/home/app/.vlog-editor`

**注意**：

- `docker-compose.dev.yml` 不再包含 `frontend` 服务
- 如果 Phase 7 前端已落地，桌面端开发仍通过本地 `npm run dev` / Electron 命令启动，而不是在 Compose 中长期运行一个 Vite 容器

**示例命令**：

```bash
docker compose -f docker-compose.dev.yml up --build backend
```

### 8.5 本地开发脚本

#### 8.5.1 初始化脚本

**文件**：`scripts/setup-local.sh`

**职责**：

1. 检查 `python3`、`node`、`npm`、`ffmpeg` 是否可用
2. 创建或复用 `venv`
3. 安装后端开发依赖：

```bash
python -m pip install -e '.[dev]'
```

4. 创建本地数据目录：

```bash
~/.vlog-editor/projects
~/.vlog-editor/logs
```

5. 若 `vlog-editor-desktop/` 已存在，则执行前端依赖安装
6. 输出后续启动方式

**实现要求**：

- 脚本需幂等，可重复执行
- 使用 `set -euo pipefail`
- 不执行不存在的“全局数据库初始化”逻辑
- 不假设 SQLite 在项目启动前需要预建单库；项目数据库按 `project_id` 懒创建

#### 8.5.2 后端启动脚本

**文件**：`scripts/start-backend.sh`

**职责**：

- 激活虚拟环境
- 以开发模式启动 FastAPI：

```bash
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
```

#### 8.5.3 桌面端联调启动脚本

**文件**：`scripts/start-desktop-dev.sh`

**职责**：

1. 启动后端
2. 轮询 `/health`，确认后端就绪
3. 进入 `vlog-editor-desktop/` 启动 Electron 开发环境
4. 捕获退出信号并同时关闭子进程

**实现要求**：

- 不使用固定 `sleep 3`
- 必须改为健康检查轮询
- 渲染进程开发模式读取：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

### 8.6 Electron 生产打包

**前提**：Phase 7 已交付 `vlog-editor-desktop/` 桌面端工程。

**目标**：用户双击桌面应用即可使用系统，无需手动启动 Python 服务。

#### 8.6.1 主进程职责

**文件**：`vlog-editor-desktop/src/main/backend/launcher.ts`

主进程在生产模式负责：

1. 定位打包后的 Python 运行时与后端代码目录
2. 启动本地后端子进程
3. 注入环境变量：
   - `APP_ENV=production`
   - `APP_DATA_DIR=<用户目录下的 .vlog-editor>`
   - `SERVER_HOST=127.0.0.1`
   - `SERVER_PORT=<固定端口或保留端口>`
4. 轮询 `GET /health`
5. 成功后通知渲染进程可用
6. 应用退出时回收后端子进程

#### 8.6.2 渲染进程职责

- 生产模式不直接依赖 `VITE_API_BASE_URL`
- API 地址由 preload / launcher 注入
- 若后端未就绪，显示“正在启动本地服务”状态页
- 若后端启动失败，显示错误信息与诊断入口

#### 8.6.3 打包要求

**文件**：`vlog-editor-desktop/electron-builder.yml`

打包时需包含：

- Python 运行时
- 后端源代码或已整理的运行目录
- 必需的 Python 依赖
- FFmpeg 能力的系统兼容策略说明

**说明**：

- macOS 与 Linux 的桌面包均以内置后端为目标
- Windows 支持可放到后续阶段，不纳入本阶段承诺

### 8.7 配置契约

部署相关配置统一收敛为以下变量：

| 变量 | 用途 | 默认值 | 使用场景 |
|------|------|--------|----------|
| `APP_ENV` | 运行环境 | `development` | 全局 |
| `APP_DATA_DIR` | 应用数据根目录 | `~/.vlog-editor` | 全局 |
| `SERVER_HOST` | 服务监听地址 | 开发 `0.0.0.0` / 生产 `127.0.0.1` | 后端 |
| `SERVER_PORT` | 服务端口 | `8000` | 后端 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 后端 |
| `KIMI_API_KEY` | 可选外部能力配置 | 无 | 后端 |
| `VITE_API_BASE_URL` | 渲染进程开发态 API 地址 | `http://127.0.0.1:8000/api` | 仅开发模式 |

**要求**：

- 后端实现需真正读取以上环境变量
- `.env.example` 仅作为示例，不直接复制为生产配置
- 文档需区分“开发态变量”和“生产态由 Electron 注入的变量”

### 8.8 部署与验证步骤

#### macOS / Linux 本地开发

```bash
# 1. 克隆项目
git clone <repo-url>
cd vlog-editor-fast

# 2. 初始化本地环境
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh

# 3. 启动后端（后端单独调试）
chmod +x scripts/start-backend.sh
./scripts/start-backend.sh
```

若 Phase 7 前端已落地，可使用：

```bash
chmod +x scripts/start-desktop-dev.sh
./scripts/start-desktop-dev.sh
```

#### Docker 后端开发模式

```bash
docker compose -f docker-compose.dev.yml up --build backend
```

#### 桌面端生产模式

- 安装打包后的桌面应用
- 双击启动应用
- 应用自动拉起本地后端
- 用户无需手动访问 `localhost:5173`

### 8.9 验收标准

本阶段完成后，必须满足以下标准：

1. 后端镜像可成功构建并启动
2. `/health` 探活正常
3. 本地开发脚本可重复执行且不报错
4. 本地数据目录创建在用户目录下，而不是容器 root 目录
5. 开发模式下桌面端可连通本地后端
6. 生产模式下 Electron 可自动拉起后端并完成至少一次项目创建流程
7. 重启应用后，项目数据仍可从本地数据目录恢复

---

## Phase 9: 文档完善

### 9.1 目标与交付边界

**目标**：基于当前仓库真实实现，交付一套可执行、可验证、可维护的文档体系，覆盖：

1. 用户首次安装、启动、创建项目和完成核心流程的操作说明
2. 开发者本地开发、测试、调试、部署和目录约定说明
3. 与当前 FastAPI 实现一致的 API 参考文档
4. 与 Phase 8 一致的开发模式 / Docker 模式 / Electron 生产模式说明

**本阶段优先级**：

- **先纠偏**：先修正现有过时文档，再补新增文档
- **以实现为准**：所有命令、路径、接口以仓库当前代码和脚本为准
- **减少重复**：尽量复用现有 `docs/` 分层结构，不新增大而全的重复手册
- **可验证**：每一类文档都要有明确验收方式

**本阶段不做**：

- 不编写与当前实现不一致的“预告型”文档
- 不把尚未落地的功能写成既成事实
- 不手工维护与 OpenAPI 完全重复的全量接口清单
- 不为了“文档齐全”新增大量低价值截图或营销材料

### 9.2 交付物清单

| 交付物 | 文件 | 用途 |
|--------|------|------|
| 文档导航页 | `docs/README.md` | 提供文档入口、阅读顺序、受众说明 |
| 部署指南 | `docs/deployment/DEPLOYMENT_GUIDE.md` | 说明开发、Docker、桌面生产三类运行模式 |
| 快速开始 | `docs/user_guide/quick_start.md` | 面向首次使用者，提供最短启动路径 |
| 用户工作流指南 | `docs/user_guide/workflow.md` | 说明项目从创建到导出的核心流程 |
| 用户故障排查 | `docs/user_guide/troubleshooting.md` | 收敛常见报错、恢复办法、日志定位方式 |
| 用户 FAQ | `docs/user_guide/faq.md` | 回答限制、性能、兼容性等高频问题 |
| 开发环境指南 | `docs/developer_guide/development_setup.md` | 说明本地环境、依赖、脚本、数据目录 |
| 后端开发指南 | `docs/developer_guide/backend_guide.md` | 说明后端结构、模块边界、调试方式 |
| 前端开发指南 | `docs/developer_guide/frontend_guide.md` | 若桌面端已落地，说明 Electron/React 结构与联调方式 |
| API 参考 | `docs/api/API_REFERENCE.md` | 说明接口约定、错误模型、示例请求与 OpenAPI 入口 |
| 仓库入口更新 | `README.md` | 链接核心文档，避免根文档继续漂移 |

### 9.3 编写原则

所有文档必须遵循以下原则：

1. **单一事实来源**
   - 安装与运行命令以 `pyproject.toml`、`scripts/`、`src/server/main.py` 为准
   - API 文档以 FastAPI 暴露的 OpenAPI 和实际路由实现为准

2. **区分已实现与计划中**
   - 当前仓库未实现的能力，不写成默认可用
   - 若桌面端工程尚未落地，前端文档需明确标注“前提条件”或暂缓输出

3. **避免重复维护**
   - 用户指南采用拆分文档，不再额外维护 `USER_MANUAL.md` 这类总册
   - 开发指南采用分主题文档，不把测试、性能、部署、架构全部堆到单文件

4. **命令可执行**
   - 文档中的安装、启动、测试命令必须至少人工验证一次
   - 文档中的文件路径、接口路径、环境变量名必须与仓库一致

5. **错误信息真实**
   - API 文档只描述当前存在的认证、错误处理、状态码约定
   - 在未引入项目级认证前，不单列“认证机制”作为既有能力

### 9.4 工作分解

#### 9.4.1 文档审计与纠偏

**目标**：先清理现有文档中的过时内容，避免“新文档正确、旧文档误导”。

**需要检查的重点**：

- `README.md`
- `docs/user_guide/quick_start.md`
- `docs/developer_guide/testing_guide.md`
- `docs/developer_guide/performance_guide.md`
- Phase 6/Phase 8 相关报告中的交叉链接

**重点修正项**：

- 安装方式统一为：

```bash
python -m venv venv && source venv/bin/activate
python -m pip install -e '.[dev]'
```

- 后端启动方式统一为：

```bash
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
```

- 移除或修正不存在的 `.env.example`、过时的 `requirements.txt` 主安装入口、与当前接口不符的示例
- 明确项目数据目录位于 `~/.vlog-editor/projects/`

**交付结果**：

- 现有主入口文档与当前代码一致，不再出现明显过时命令

#### 9.4.2 部署与运行指南

**文件**：`docs/deployment/DEPLOYMENT_GUIDE.md`

**内容范围**：

- 系统要求与前置依赖
- 本地开发模式：后端独立启动
- Docker 模式：后端开发 / 联调用法
- Electron 生产模式：由主进程拉起本地后端
- 配置契约：`APP_ENV`、`APP_DATA_DIR`、`SERVER_HOST`、`SERVER_PORT`、`LOG_LEVEL`、`VITE_API_BASE_URL`
- 数据目录、日志目录、排障方式
- 常见问题：端口占用、依赖缺失、后端未就绪、FFmpeg 不可用

**实现要求**：

- 文档结构与 Phase 8 保持一致
- 必须明确区分“开发态变量”和“生产态由 Electron 注入的变量”
- 不把 Docker 写成桌面端正式交付方式

**交付结果**：

- 新用户或开发者可按文档完成至少一种可工作的启动方式

#### 9.4.3 用户指南补齐

**目标**：在现有 `docs/user_guide/` 基础上补齐核心操作路径，而不是新增重复手册。

**涉及文件**：

- `docs/user_guide/quick_start.md`
- `docs/user_guide/workflow.md`
- `docs/user_guide/troubleshooting.md`
- `docs/user_guide/faq.md`

**内容要求**：

- 快速开始：最短启动路径、创建第一个项目、查看结果
- 工作流：项目创建 → 校验 → 骨架 → 高光 → 时间线 / 旁白 / 导出
- 故障排查：日志位置、常见失败原因、恢复建议
- FAQ：支持格式、性能预期、是否依赖外部 API、数据是否上传云端

**写作原则**：

- 以用户任务为组织方式，不以后端模块名组织
- 对未完成的桌面端流程，明确标注“当前适用于 API / 开发态”

**交付结果**：

- 用户无需阅读源码即可完成核心使用流程

#### 9.4.4 开发者文档补齐

**目标**：让新开发者能在 30 分钟内完成环境搭建并定位主要代码入口。

**涉及文件**：

- `docs/developer_guide/development_setup.md`
- `docs/developer_guide/backend_guide.md`
- `docs/developer_guide/frontend_guide.md`（若桌面端已存在）
- `docs/developer_guide/testing_guide.md`
- `docs/developer_guide/performance_guide.md`

**内容要求**：

- 仓库结构与模块职责
- 本地开发命令、测试命令、格式化与 lint 命令
- 后端主要模块边界：`api/`、`modules/`、`models/`、`storage/`
- 数据目录与 SQLite 存储约定
- 接口联调方式、日志排查入口
- 若 Phase 7 已落地，补充 Electron 主进程 / preload / 渲染进程职责与 API 连接方式

**交付结果**：

- 开发者能快速定位代码入口并按约定进行开发和测试

#### 9.4.5 API 文档与契约说明

**文件**：`docs/api/API_REFERENCE.md`

**内容要求**：

- API 概览与 OpenAPI 访问入口
- 路由分组与资源命名规则
- 通用错误处理与常见状态码
- 当前已实现端点的请求/响应示例
- 与 Phase 7/8 联调相关的关键接口说明

**关键要求**：

- 以 FastAPI 实际暴露接口为准，不编造不存在的认证机制
- 对仍在补口中的接口，标注“计划补齐”而不是写成已完成
- 示例请求需优先使用 `curl` 或现有测试中的真实 payload

**交付结果**：

- 前后端联调和测试人员可直接根据文档调用接口

### 9.5 执行顺序

#### Step 1：审计并修正现有文档（0.5-1天）

- 梳理现有 `README.md` 与 `docs/` 中的过时内容
- 修正安装、运行、路径、环境变量、接口示例
- 新增 `docs/README.md` 作为统一导航入口

**交付结果**：

- 文档入口清晰，现有文档不再明显误导

#### Step 2：补齐部署与用户文档（1-2天）

- 完成 `docs/deployment/DEPLOYMENT_GUIDE.md`
- 更新 `quick_start.md`、`workflow.md`、`troubleshooting.md`、`faq.md`

**交付结果**：

- 用户和测试人员可独立完成安装、启动、基本使用和排障

#### Step 3：补齐开发者与 API 文档（1-2天）

- 完成开发环境、后端、前端联调说明
- 完成 `docs/api/API_REFERENCE.md`
- 将 `README.md` 链接到核心文档

**交付结果**：

- 新开发者和联调人员可快速上手

#### Step 4：文档验证与收尾（0.5-1天）

- 逐条验证命令、路径、环境变量、接口示例
- 检查文档之间的交叉链接
- 标注暂未落地或需后续补齐的内容

**交付结果**：

- 文档具备可执行性和可维护性

### 9.6 验收标准

本阶段完成后，必须满足以下标准：

1. `README.md` 与 `docs/README.md` 能正确引导到核心文档
2. 安装、启动、测试命令与仓库当前实现一致
3. 文档中所有关键路径、环境变量名、接口路径与代码一致
4. 用户文档覆盖“创建项目 → 查看结果”的最短闭环
5. 部署文档明确区分开发模式、Docker 模式、Electron 生产模式
6. API 文档不描述当前不存在的认证机制或未落地能力
7. 至少一轮人工验证关键命令和关键接口示例
8. 对尚未实现的桌面端内容有明确前提说明，不误导读者

---

## 开发时间表

| Phase | 任务 | 预计时间 | 优先级 |
|-------|------|---------|--------|
| 7.1-7.2 | 前端项目初始化和框架搭建 | 3-5天 | 高 |
| 7.3-7.4 | 页面和组件开发 | 10-15天 | 高 |
| 7.5 | 集成测试 | 2-3天 | 高 |
| 7.6 | 打包优化 | 2-3天 | 中 |
| 8.1-8.3 | Docker和本地部署配置 | 2-3天 | 高 |
| 9.1-9.6 | 文档审计、修正与补齐 | 3-5天 | 中 |
| **总计** | | **24-34天** | |

---

## 关键决策和约束

### 技术选择理由

1. **Electron** - 项目已推荐，支持跨平台（macOS/Linux/Windows）
2. **React** - 成熟生态，组件丰富，开发效率高
3. **TypeScript** - 类型安全，减少运行时错误
4. **Ant Design** - 企业级组件库，中文支持完善
5. **Redux Toolkit** - 简化Redux复杂度，开发体验好
6. **Vite** - 快速开发体验，构建速度快

### 架构原则

1. **前后端分离** - 前端通过REST API与后端通信
2. **本地优先** - 所有数据存储在本地，不上传到云
3. **模块化** - 页面、组件、服务分离，便于维护
4. **类型安全** - 使用TypeScript确保类型安全
5. **可测试性** - 组件和服务易于单元测试

### 性能考虑

1. **代码分割** - 使用Vite的动态导入实现路由级代码分割
2. **懒加载** - 大型组件使用React.lazy实现懒加载
3. **缓存策略** - Redux缓存API响应，减少不必要的请求
4. **视频优化** - 使用Video.js的流媒体支持
5. **内存管理** - 及时清理Redux状态中的大型对象

---

## 风险和缓解措施

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 前端开发周期长 | 延迟交付 | 优先开发核心页面，其他页面可后续迭代 |
| Electron打包复杂 | 部署困难 | 使用electron-builder自动化打包 |
| 跨平台兼容性 | 功能异常 | 在macOS和Linux上充分测试 |
| API变更 | 前后端不同步 | 定义清晰的API契约，使用OpenAPI文档 |
| 性能问题 | 用户体验差 | 进行性能基准测试，及时优化 |

---

## 下一步行动

1. **确认技术栈** - 确认是否同意使用 Electron + React + TypeScript
2. **创建前端项目** - 初始化Electron + React项目结构
3. **开始页面开发** - 从ProjectList页面开始，逐步实现其他页面
4. **并行进行** - 后端可继续优化和集成推荐的开源工具
5. **定期集成** - 每周进行前后端集成测试

---

## 附录：推荐的开源工具集成

根据项目的 `tools_research.md`，以下工具应在后端逐步集成：

| 工具 | 用途 | 优先级 | 集成时间 |
|------|------|--------|---------|
| ExifTool | 元数据提取 | 高 | Phase 7进行中 |
| PySceneDetect | 镜头切分 | 高 | Phase 7进行中 |
| WhisperX | 词级时间戳 | 中 | Phase 7后期 |
| OpenCLIP | 语义匹配 | 中 | Phase 8 |
| Qdrant | 向量检索 | 中 | Phase 8 |
| HanLP/JioNLP | 中文文本处理 | 中 | Phase 8 |
| CosyVoice | 中文TTS | 高 | Phase 8 |

这些工具的集成不会阻塞前端开发，可以并行进行。
