# Phase 5: 版本管理与恢复 - 实现计划

## Context

Phase 5 是 vlog-editor-fast 系统的最后一个核心阶段，目标是实现完整的版本管理、局部再生成和失败恢复能力。前 4 个 Phase 已实现了从输入处理到完整成片导出的全流程。Phase 5 需要在此基础上增强：

1. **Run Orchestrator 增强** - 支持完整的状态机、恢复逻辑、模块级重试
2. **Artifact & Version Store 增强** - 完整的版本历史、依赖追踪、缓存失效
3. **Diagnostic Reporter 完善** - 详细的诊断输出、错误定位、恢复入口

## 核心需求

### 三类局部再生成
1. **仅重写旁白** - 复用 timeline 和 audio_mix，重新生成 narration 和 export
2. **仅更换 BGM** - 复用 timeline 和 narration，重新生成 audio_mix 和 export
3. **压缩时长** - 复用 story 和 highlights，重新生成 timeline、narration、audio、export

### 版本管理要求
- 每个中间产物都是版本化的，记录上游依赖
- 用户修改时只失效受影响的下游版本
- 支持版本间快速切换（不重新计算）
- 支持回滚到任意历史版本

### 失败恢复要求
- 失败时能定位到具体模块和原因
- 支持模块级重试（不重新执行上游）
- 诊断包包含完整的错误信息和恢复建议
- 支持从任意失败点恢复

## 实现方案

### 1. 增强 Run Orchestrator (`src/server/modules/run_orchestrator.py`)

**新增功能：**

#### 1.1 完整的运行状态机
```python
class RunState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    AWAITING_USER = "awaiting_user"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_MANUAL = "failed_manual"

class RunRecord:
    run_id: str
    project_id: str
    run_type: str  # "full_pipeline", "regenerate_narration", "regenerate_audio", "regenerate_shorter"
    state: RunState
    started_at: datetime
    ended_at: Optional[datetime]
    task_states: Dict[str, TaskStateRecord]  # stage_name -> state
    error_info: Optional[ErrorInfo]
    recovery_suggestions: List[str]
```

#### 1.2 模块级重试机制
```python
async def run_with_retry(
    self,
    stage_name: str,
    stage_func: Callable,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> TaskStateRecord:
    """执行单个阶段，支持重试"""
    for attempt in range(max_retries):
        try:
            result = await stage_func()
            return TaskStateRecord(
                stage_name=stage_name,
                status="succeeded",
                attempt=attempt + 1
            )
        except RetryableError as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
                continue
            else:
                return TaskStateRecord(
                    stage_name=stage_name,
                    status="failed_retryable",
                    error=str(e),
                    attempt=attempt + 1
                )
        except Exception as e:
            return TaskStateRecord(
                stage_name=stage_name,
                status="failed_manual",
                error=str(e),
                attempt=attempt + 1
            )
```

#### 1.3 恢复执行流程
```python
async def resume_from_failure(
    self,
    project_id: str,
    run_id: str,
    failed_stage: str
) -> RunRecord:
    """从失败点恢复执行"""
    # 1. 加载上一次运行的状态
    # 2. 验证上游产物是否有效
    # 3. 从失败阶段重新开始
    # 4. 跳过已成功的阶段
```

#### 1.4 三类再生成的编排
```python
async def regenerate_narration(self, project_id: str) -> RunRecord:
    """仅重写旁白"""
    # 1. 验证 timeline 版本有效
    # 2. 重新生成 narration
    # 3. 重新生成 export
    # 4. 更新版本依赖

async def regenerate_audio(self, project_id: str, new_bgm: Optional[str] = None) -> RunRecord:
    """仅更换 BGM"""
    # 1. 验证 timeline 和 narration 版本有效
    # 2. 重新生成 audio_mix
    # 3. 重新生成 export
    # 4. 更新版本依赖

async def regenerate_shorter(self, project_id: str, target_duration: int) -> RunRecord:
    """压缩时长"""
    # 1. 验证 story 和 highlights 版本有效
    # 2. 重新生成 timeline（压缩）
    # 3. 重新生成 narration
    # 4. 重新生成 audio_mix
    # 5. 重新生成 export
    # 6. 更新版本依赖
```

### 2. 增强 Artifact Store (`src/server/modules/artifact_store.py`)

**新增功能：**

#### 2.1 版本历史管理
```python
class ArtifactVersionHistory:
    artifact_type: str
    project_id: str
    versions: List[ArtifactVersion]  # 按时间排序
    active_version_id: str
    
    def get_version_history(self) -> List[ArtifactVersion]:
        """获取完整版本历史"""
        
    def switch_to_version(self, version_id: str) -> ArtifactVersion:
        """切换到指定版本"""
        
    def get_version_diff(self, v1_id: str, v2_id: str) -> Dict:
        """比较两个版本的差异"""
```

#### 2.2 依赖追踪与缓存失效
```python
class DependencyGraph:
    """管理产物间的依赖关系"""
    
    def add_dependency(self, downstream: str, upstream: str):
        """记录依赖关系"""
        
    def invalidate_downstream(self, artifact_id: str) -> List[str]:
        """失效所有下游产物，返回失效的产物列表"""
        
    def get_affected_stages(self, artifact_id: str) -> List[str]:
        """获取受影响的处理阶段"""
        
    def validate_upstream(self, artifact_id: str) -> bool:
        """验证上游产物是否有效"""
```

#### 2.3 版本复用与增量更新
```python
class VersionReuse:
    """支持版本复用，避免重复计算"""
    
    def can_reuse_version(
        self,
        artifact_type: str,
        upstream_versions: Dict[str, str]
    ) -> Optional[str]:
        """检查是否存在可复用的版本"""
        
    def mark_reused(self, version_id: str, reused_from: str):
        """标记版本为复用"""
```

### 3. 完善 Diagnostic Reporter (`src/server/modules/diagnostic_reporter.py`)

**新增功能：**

#### 3.1 详细的诊断包
```python
class DiagnosticBundle:
    run_id: str
    project_id: str
    run_summary: RunSummary
    
    # 各阶段的诊断信息
    input_validation_report: InputValidationReport
    story_parsing_diagnostics: StoryParsingDiagnostics
    media_analysis_diagnostics: MediaAnalysisDiagnostics
    alignment_diagnostics: AlignmentDiagnostics
    edit_planning_diagnostics: EditPlanningDiagnostics
    narration_diagnostics: NarrationDiagnostics
    audio_diagnostics: AudioDiagnostics
    rendering_diagnostics: RenderingDiagnostics
    
    # 错误和恢复信息
    error_timeline: List[ErrorEvent]
    recovery_suggestions: List[RecoverySuggestion]
    
    # 性能指标
    performance_metrics: PerformanceMetrics
    
    # 完整日志
    runtime_logs: str
```

#### 3.2 错误定位与恢复建议
```python
class ErrorAnalyzer:
    """分析错误原因并生成恢复建议"""
    
    def analyze_error(self, error: Exception, context: Dict) -> ErrorAnalysis:
        """分析错误原因"""
        # 1. 识别错误类型（RetryableError, ResourceError, ValidationError 等）
        # 2. 定位错误发生的模块和阶段
        # 3. 收集相关的上下文信息
        # 4. 生成恢复建议
        
    def generate_recovery_suggestions(self, error_analysis: ErrorAnalysis) -> List[str]:
        """根据错误分析生成恢复建议"""
        # 例如：
        # - "内存不足，建议启用轻量模式"
        # - "媒体文件损坏，建议检查文件完整性"
        # - "网络超时，建议重试或使用本地模型"
```

#### 3.3 诊断输出格式
```python
class DiagnosticReporter:
    def generate_report(self, run_record: RunRecord) -> DiagnosticBundle:
        """生成完整诊断包"""
        
    def export_report(self, bundle: DiagnosticBundle, format: str = "json") -> str:
        """导出诊断包（JSON、HTML、Markdown）"""
        
    def generate_recovery_manifest(self, bundle: DiagnosticBundle) -> Dict:
        """生成恢复清单，指导用户如何恢复"""
```

### 4. 数据库扩展 (`src/storage/schemas.py`)

**新增表：**

```python
# 运行记录
class RunRecord(Base):
    __tablename__ = "run_records"
    run_id: str
    project_id: str
    run_type: str  # full_pipeline, regenerate_narration, regenerate_audio, regenerate_shorter
    state: str
    started_at: datetime
    ended_at: Optional[datetime]
    error_info: Optional[str]  # JSON

# 任务状态
class TaskStateRecord(Base):
    __tablename__ = "task_states"
    task_id: str
    run_id: str
    stage_name: str
    status: str  # running, succeeded, degraded, failed_retryable, failed_manual
    started_at: datetime
    ended_at: Optional[datetime]
    attempt: int
    error_message: Optional[str]

# 版本历史
class VersionHistory(Base):
    __tablename__ = "version_histories"
    history_id: str
    project_id: str
    artifact_type: str
    version_id: str
    created_at: datetime
    is_active: bool
    reused_from: Optional[str]

# 依赖关系
class ArtifactDependency(Base):
    __tablename__ = "artifact_dependencies"
    dependency_id: str
    project_id: str
    downstream_artifact_id: str
    upstream_artifact_id: str
    upstream_artifact_type: str
    created_at: datetime

# 诊断记录
class DiagnosticRecord(Base):
    __tablename__ = "diagnostic_records"
    diagnostic_id: str
    run_id: str
    project_id: str
    diagnostic_bundle: str  # JSON
    created_at: datetime
```

### 5. API 端点扩展 (`src/server/api/projects.py`)

**新增端点：**

```python
# 版本管理
GET /api/projects/{project_id}/versions/{artifact_type}
    # 获取版本历史

POST /api/projects/{project_id}/versions/{artifact_type}/{version_id}/switch
    # 切换到指定版本

GET /api/projects/{project_id}/versions/{artifact_type}/{v1_id}/diff/{v2_id}
    # 比较两个版本

# 局部再生成
POST /api/projects/{project_id}/regenerate/narration
    # 仅重写旁白

POST /api/projects/{project_id}/regenerate/audio
    # 仅更换 BGM

POST /api/projects/{project_id}/regenerate/shorter
    # 压缩时长

# 恢复与诊断
POST /api/projects/{project_id}/runs/{run_id}/resume
    # 从失败点恢复

GET /api/projects/{project_id}/runs/{run_id}/diagnostics
    # 获取诊断包

GET /api/projects/{project_id}/runs
    # 获取所有运行记录

POST /api/projects/{project_id}/runs/{run_id}/retry/{stage_name}
    # 重试指定阶段
```

### 6. 类型系统扩展 (`src/shared/types.py`)

**新增类型：**

```python
class RunType(str, Enum):
    FULL_PIPELINE = "full_pipeline"
    REGENERATE_NARRATION = "regenerate_narration"
    REGENERATE_AUDIO = "regenerate_audio"
    REGENERATE_SHORTER = "regenerate_shorter"

class TaskStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    DEGRADED = "degraded"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_MANUAL = "failed_manual"

class ErrorType(str, Enum):
    RETRYABLE = "retryable"
    RESOURCE = "resource"
    VALIDATION = "validation"
    DEPENDENCY = "dependency"
    MANUAL = "manual"

class RecoverySuggestion(BaseModel):
    error_type: ErrorType
    suggestion: str
    action: str  # retry, regenerate, manual_fix, etc.
    priority: int  # 1-5, 5 is highest

class PerformanceMetrics(BaseModel):
    total_duration_seconds: float
    stage_durations: Dict[str, float]
    memory_peak_mb: float
    disk_usage_mb: float
```

## 实现步骤

### Step 1: 增强 Run Orchestrator (1-2 天)
- 实现完整的运行状态机
- 实现模块级重试机制
- 实现恢复执行流程
- 实现三类再生成的编排逻辑

### Step 2: 增强 Artifact Store (1-2 天)
- 实现版本历史管理
- 实现依赖追踪与缓存失效
- 实现版本复用与增量更新
- 添加数据库表和查询方法

### Step 3: 完善 Diagnostic Reporter (1 天)
- 实现详细的诊断包生成
- 实现错误分析和恢复建议
- 实现诊断输出格式（JSON、HTML、Markdown）

### Step 4: 扩展 API 和类型系统 (1 天)
- 添加新的 API 端点
- 添加新的 Pydantic 类型
- 更新数据库 schema

### Step 5: 集成测试 (1-2 天)
- 编写 Phase 5 集成测试
- 测试三类再生成流程
- 测试失败恢复流程
- 测试版本切换流程

### Step 6: 端到端测试与优化 (1 天)
- 完整流程测试
- 性能优化
- 文档完善

## 关键文件

**需要修改的文件：**
- `src/server/modules/run_orchestrator.py` - 增强运行编排
- `src/server/modules/artifact_store.py` - 增强版本管理
- `src/server/modules/diagnostic_reporter.py` - 完善诊断输出
- `src/server/api/projects.py` - 添加新 API 端点
- `src/shared/types.py` - 添加新类型
- `src/storage/schemas.py` - 添加新数据库表

**需要创建的文件：**
- `tests/integration/test_phase5_flow.py` - Phase 5 集成测试
- `tests/unit/test_run_orchestrator_enhanced.py` - 运行编排单元测试
- `tests/unit/test_artifact_store_enhanced.py` - 版本管理单元测试
- `tests/unit/test_diagnostic_reporter.py` - 诊断输出单元测试

## 验收标准

- [ ] 能进行至少 1 次局部再生成（三类都支持）
- [ ] 版本间可快速切换（不重新计算）
- [ ] 失败时能定位到具体模块和原因
- [ ] 支持模块级重试（不重新执行上游）
- [ ] 诊断包包含完整的错误信息和恢复建议
- [ ] 支持从任意失败点恢复
- [ ] 所有 Phase 5 集成测试通过
- [ ] 性能指标达到目标（处理时长 ≤ 120 分钟）

## 风险与缓解

| 风险 | 缓解策略 |
|------|---------|
| 版本依赖追踪复杂 | 使用有向无环图（DAG）管理依赖，充分测试 |
| 恢复逻辑容易出错 | 详细的状态机设计，充分的单元和集成测试 |
| 诊断信息过多 | 分层诊断（简要、详细、完整），支持过滤 |
| 性能下降 | 版本复用避免重复计算，增量更新优化 |

