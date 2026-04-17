# 第一阶段实现计划：基础设施与输入处理

## Context

第一阶段是整个系统的基础。目标是建立项目管理框架、输入校验机制和素材索引系统，为后续的故事解析、媒体分析等模块奠定基础。

当前项目仅有文档，无实现代码。本阶段需要从零开始搭建技术栈、初始化项目结构、实现三个核心模块。

---

## 实现目标

**验收标准**：
- 能创建项目并导入素材
- 能识别并报告输入风险
- 能生成完整的素材索引

**关键产物**：
- `ProjectInputContract` 数据模型
- `InputValidationReport` 校验结果
- `asset_index` 素材索引

---

## 技术栈初始化

### 1.1 项目结构创建

```
vlog-editor-fast/
├── src/
│   ├── server/                 # Python 后端服务
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 应用入口
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── project.py      # 项目相关模型
│   │   │   ├── media.py        # 媒体相关模型
│   │   │   └── validation.py   # 校验相关模型
│   │   ├── modules/            # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── project_manager.py
│   │   │   ├── input_validator.py
│   │   │   └── asset_indexer.py
│   │   ├── storage/            # 存储层
│   │   │   ├── __init__.py
│   │   │   ├── database.py     # SQLite 初始化
│   │   │   └── schemas.py      # 数据库 schema
│   │   ├── api/                # API 路由
│   │   │   ├── __init__.py
│   │   │   └── projects.py     # 项目相关端点
│   │   └── config.py           # 配置管理
│   ├── client/                 # 前端（暂不实现）
│   └── shared/                 # 共享类型
│       ├── __init__.py
│       └── types.py            # 共享数据类型
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_project_manager.py
│   │   ├── test_input_validator.py
│   │   └── test_asset_indexer.py
│   └── integration/
│       └── test_phase1_flow.py
├── pyproject.toml              # Python 项目配置
├── requirements.txt            # 依赖列表
└── .env.example                # 环境变量示例
```

### 1.2 依赖安装

**Python 依赖**（requirements.txt）：
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
python-dotenv==1.0.0
pillow==10.1.0
opencv-python==4.8.1.78
librosa==0.10.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

**初始化步骤**：
1. 创建 `pyproject.toml` 和 `requirements.txt`
2. 创建虚拟环境并安装依赖
3. 初始化 Git 忽略文件

---

## 核心模块实现

### 2.1 数据模型定义

**文件**：`src/server/models/project.py`、`src/server/models/media.py`、`src/server/models/validation.py`

**关键模型**：

```python
# ProjectInputContract - 项目输入合约
class ProjectInputContract(BaseModel):
    project_name: str
    travel_note: str
    media_files: List[str]  # 文件路径列表
    bgm_asset: Optional[str] = None
    tts_voice: Optional[str] = None
    metadata_pack: Optional[Dict] = None  # GPS、EXIF 等

# MediaFileInfo - 媒体文件信息
class MediaFileInfo(BaseModel):
    file_path: str
    file_type: str  # 'video', 'photo'
    file_size: int
    duration: Optional[float] = None  # 视频时长（秒）
    resolution: Optional[Tuple[int, int]] = None
    creation_time: Optional[datetime] = None
    has_audio: Optional[bool] = None

# InputValidationReport - 输入校验报告
class InputValidationReport(BaseModel):
    project_id: str
    is_valid: bool
    validation_timestamp: datetime
    errors: List[str]  # 致命错误
    warnings: List[str]  # 警告
    media_summary: Dict  # 媒体统计
    metadata_coverage: Dict  # 元数据覆盖率
    recommendations: List[str]  # 建议

# AssetIndex - 素材索引
class AssetIndex(BaseModel):
    project_id: str
    total_videos: int
    total_photos: int
    total_duration: float  # 秒
    indexed_at: datetime
    media_items: List[MediaFileInfo]
    metadata_availability: Dict  # 各类元数据的可用性
```

### 2.2 Project Manager 模块

**文件**：`src/server/modules/project_manager.py`

**职责**：
- 创建项目工作区
- 管理项目配置
- 初始化项目元数据

**关键方法**：
```python
class ProjectManager:
    def create_project(self, input_contract: ProjectInputContract) -> str:
        """创建项目，返回 project_id"""
        
    def get_project_config(self, project_id: str) -> ProjectConfig:
        """获取项目配置"""
        
    def update_project_config(self, project_id: str, config: ProjectConfig) -> None:
        """更新项目配置"""
```

**实现要点**：
- 生成唯一的 `project_id`（UUID）
- 创建项目工作目录：`~/.vlog-editor/projects/{project_id}/`
- 初始化项目元数据文件
- 记录项目创建时间和输入合约

### 2.3 Input Validator 模块

**文件**：`src/server/modules/input_validator.py`

**职责**：
- 校验输入数据的完整性和有效性
- 识别风险和问题
- 生成校验报告

**校验规则**（来自 PRD）：

| 检查项 | 规则 | 错误/警告 |
|--------|------|---------|
| 游记长度 | ≥150 字 | 错误 |
| 游记长度 | <150 字 | 警告（切换简化叙事） |
| 视频数量 | ≥5 个 | 警告 |
| 照片数量 | ≥50 张 | 警告 |
| 总时长 | ≥10 分钟 | 错误 |
| 文件格式 | 支持的格式 | 错误 |
| 文件可访问性 | 文件存在且可读 | 错误 |
| 元数据 | EXIF、GPS、时间戳 | 警告（覆盖率统计） |

**关键方法**：
```python
class InputValidator:
    def validate(self, input_contract: ProjectInputContract) -> InputValidationReport:
        """执行完整的输入校验"""
        
    def check_narrative_length(self, text: str) -> Tuple[bool, str]:
        """检查游记长度"""
        
    def check_media_files(self, file_paths: List[str]) -> Tuple[bool, List[str]]:
        """检查媒体文件的存在性和格式"""
        
    def analyze_metadata_coverage(self, media_files: List[str]) -> Dict:
        """分析元数据覆盖率"""
```

### 2.4 Asset Indexer 模块

**文件**：`src/server/modules/asset_indexer.py`

**职责**：
- 扫描媒体文件
- 提取文件元数据
- 生成素材索引

**关键方法**：
```python
class AssetIndexer:
    def index_assets(self, project_id: str, media_files: List[str]) -> AssetIndex:
        """生成完整的素材索引"""
        
    def extract_video_metadata(self, file_path: str) -> MediaFileInfo:
        """提取视频元数据（时长、分辨率、音频）"""
        
    def extract_photo_metadata(self, file_path: str) -> MediaFileInfo:
        """提取照片元数据（分辨率、创建时间、EXIF）"""
        
    def extract_exif_data(self, file_path: str) -> Dict:
        """提取 EXIF 数据（GPS、时间戳等）"""
```

**实现要点**：
- 使用 OpenCV 提取视频元数据
- 使用 Pillow 提取照片元数据
- 使用 librosa 检测音频
- 缓存索引结果到 SQLite

---

## 数据库设计

**文件**：`src/server/storage/schemas.py`

**核心表**：

```sql
-- projects 表
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft'  -- draft, ready, running, ...
);

-- project_configs 表
CREATE TABLE project_configs (
    config_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE,
    travel_note TEXT NOT NULL,
    bgm_asset TEXT,
    tts_voice TEXT,
    metadata_pack JSON,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- media_files 表
CREATE TABLE media_files (
    file_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,  -- 'video', 'photo'
    file_size INTEGER,
    duration REAL,  -- 视频时长
    resolution TEXT,  -- "1920x1080"
    creation_time TIMESTAMP,
    has_audio BOOLEAN,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- validation_reports 表
CREATE TABLE validation_reports (
    report_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    is_valid BOOLEAN,
    errors JSON,
    warnings JSON,
    media_summary JSON,
    metadata_coverage JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- asset_indexes 表
CREATE TABLE asset_indexes (
    index_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE,
    total_videos INTEGER,
    total_photos INTEGER,
    total_duration REAL,
    metadata_availability JSON,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

---

## API 设计

**文件**：`src/server/api/projects.py`

**关键端点**：

```python
# POST /api/projects/create
# 创建项目
# 请求体：ProjectInputContract
# 响应：{ project_id, validation_report, asset_index }

# GET /api/projects/{project_id}
# 获取项目信息
# 响应：{ project_id, project_name, status, created_at, config, validation_report, asset_index }

# POST /api/projects/{project_id}/validate
# 重新校验项目输入
# 响应：{ validation_report }

# GET /api/projects/{project_id}/assets
# 获取素材索引
# 响应：{ asset_index }
```

---

## 实现步骤

### Step 1: 项目初始化（1-2 天）
- [ ] 创建项目结构
- [ ] 配置 `pyproject.toml` 和 `requirements.txt`
- [ ] 初始化 Git 忽略文件
- [ ] 创建虚拟环境并安装依赖

### Step 2: 数据模型定义（1 天）
- [ ] 定义 Pydantic 模型
- [ ] 定义数据库 schema
- [ ] 创建数据库初始化脚本

### Step 3: 存储层实现（1-2 天）
- [ ] 实现 SQLite 连接和初始化
- [ ] 实现数据库操作（CRUD）
- [ ] 添加事务管理

### Step 4: Project Manager 实现（1 天）
- [ ] 实现项目创建逻辑
- [ ] 实现项目配置管理
- [ ] 添加单元测试

### Step 5: Input Validator 实现（1-2 天）
- [ ] 实现校验规则
- [ ] 实现元数据覆盖率分析
- [ ] 生成校验报告
- [ ] 添加单元测试

### Step 6: Asset Indexer 实现（2 天）
- [ ] 实现视频元数据提取
- [ ] 实现照片元数据提取
- [ ] 实现 EXIF 数据提取
- [ ] 生成素材索引
- [ ] 添加单元测试

### Step 7: FastAPI 应用和 API 实现（1-2 天）
- [ ] 创建 FastAPI 应用
- [ ] 实现 API 端点
- [ ] 添加错误处理
- [ ] 添加日志记录

### Step 8: 集成测试（1-2 天）
- [ ] 编写端到端测试
- [ ] 测试完整的项目创建流程
- [ ] 测试校验和索引流程

### Step 9: 文档和示例（1 天）
- [ ] 编写 API 文档
- [ ] 创建使用示例
- [ ] 编写开发指南

**总计**：10-15 天

---

## 验证方案

### 单元测试
- 每个模块的核心逻辑都有测试
- 数据模型的序列化/反序列化测试
- 校验规则的边界情况测试

### 集成测试
- 完整的项目创建流程
- 输入校验和素材索引的协作
- 数据库操作的正确性

### 端到端测试
- 使用真实的旅行媒体样本
- 验证生成的索引和报告的准确性
- 验证 API 的可用性

### 验收标准检查
```bash
# 1. 能创建项目
curl -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -d '{...}'

# 2. 能获取校验报告
curl http://localhost:8000/api/projects/{project_id}/validate

# 3. 能获取素材索引
curl http://localhost:8000/api/projects/{project_id}/assets

# 4. 检查数据库中的数据
sqlite3 ~/.vlog-editor/projects/{project_id}/project.db "SELECT * FROM media_files;"
```

---

## 关键决策

1. **Python + FastAPI**：选择 Python 是因为 AI/ML 生态完善，FastAPI 提供高效的 IPC 通信
2. **SQLite**：本地存储，无需外部数据库，便于项目隔离
3. **Pydantic**：强类型检查，自动序列化/反序列化
4. **分层架构**：模型层、业务逻辑层、存储层、API 层分离，便于测试和维护

---

## 风险与缓解

| 风险 | 缓解策略 |
|------|---------|
| 元数据提取失败 | 使用 try-catch，记录错误，继续处理其他文件 |
| 大文件处理性能 | 使用流式处理，避免一次性加载整个文件 |
| 数据库并发访问 | 使用 SQLAlchemy 的连接池和事务管理 |
| 文件路径问题 | 规范化路径，处理相对路径和绝对路径 |

