# 数据字典与产物 Schema

## 1. 文档定义

本文档定义 V1 系统内部的核心数据结构、产物格式和版本管理机制。所有数据结构采用 JSON 格式表示。

---

## 2. 核心数据结构

### 2.1 故事段落（StorySegment）

```json
{
  "segment_id": "seg_001",
  "project_id": "proj_001",
  "index": 0,
  "summary": "第一天的旅程开始，从机场出发到酒店入住",
  "full_text": "今天一大早就出发去机场，经过3小时的飞行，终于到达了目的地。出了机场后，我们直接前往酒店...",
  "time_range": {
    "start": "2026-04-01T09:00:00Z",
    "end": "2026-04-01T14:30:00Z"
  },
  "importance": "high",
  "is_highlighted": true,
  "user_marked_must_keep": false,
  "low_confidence_warning": null,
  "created_at": "2026-04-17T10:00:00Z",
  "modified_at": "2026-04-17T10:30:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `segment_id` | string | 段落唯一标识 |
| `project_id` | string | 所属项目 ID |
| `index` | integer | 段落在故事中的顺序（0-based） |
| `summary` | string | 段落摘要（50-100 字） |
| `full_text` | string | 段落的完整文本 |
| `time_range.start` | ISO 8601 | 段落起始时间 |
| `time_range.end` | ISO 8601 | 段落结束时间 |
| `importance` | enum | 重要度：`high`、`medium`、`low` |
| `is_highlighted` | boolean | 是否标记为高光 |
| `user_marked_must_keep` | boolean | 用户是否标记为"必须保留" |
| `low_confidence_warning` | object \| null | 低置信警告（见 2.6） |
| `created_at` | ISO 8601 | 创建时间 |
| `modified_at` | ISO 8601 | 最后修改时间 |

---

### 2.2 镜头候选（ClipCandidate）

```json
{
  "clip_id": "clip_001",
  "segment_id": "seg_001",
  "project_id": "proj_001",
  "media_file_id": "media_001",
  "file_path": "/path/to/video_001.mp4",
  "media_type": "video",
  "time_range": {
    "start": "00:15",
    "end": "00:45"
  },
  "duration_seconds": 30,
  "match_confidence": 0.85,
  "match_reason": "视觉相似度高，时间对齐",
  "visual_features": {
    "scene_tags": ["airport", "outdoor", "daytime"],
    "people_detected": true,
    "motion_level": "medium"
  },
  "user_disabled": false,
  "user_marked_memorial": false,
  "is_selected": true,
  "created_at": "2026-04-17T10:15:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `clip_id` | string | 镜头唯一标识 |
| `segment_id` | string | 所属段落 ID |
| `project_id` | string | 所属项目 ID |
| `media_file_id` | string | 媒体文件 ID |
| `file_path` | string | 媒体文件路径 |
| `media_type` | enum | 媒体类型：`video`、`photo` |
| `time_range.start` | string | 镜头起始时间（HH:MM:SS 格式） |
| `time_range.end` | string | 镜头结束时间 |
| `duration_seconds` | number | 镜头时长（秒） |
| `match_confidence` | number | 匹配置信度（0-1） |
| `match_reason` | string | 匹配原因 |
| `visual_features.scene_tags` | array | 场景标签 |
| `visual_features.people_detected` | boolean | 是否检测到人物 |
| `visual_features.motion_level` | enum | 运动水平：`low`、`medium`、`high` |
| `user_disabled` | boolean | 用户是否禁用此镜头 |
| `user_marked_memorial` | boolean | 用户是否标记为"纪念性必保留" |
| `is_selected` | boolean | 是否被选中为最终镜头 |
| `created_at` | ISO 8601 | 创建时间 |

---

### 2.3 诊断信息（DiagnosticMessage）

```json
{
  "diagnostic_id": "diag_001",
  "segment_id": "seg_001",
  "project_id": "proj_001",
  "issue_type": "low_confidence_match",
  "confidence_score": 0.45,
  "root_cause": "missing_gps_data",
  "user_message": "这个段落的匹配置信度较低（0.45），因为缺少 GPS 数据。建议：检查素材的位置信息，或手动调整候选镜头。",
  "suggested_action": "manual_adjustment",
  "timestamp": "2026-04-17T10:30:00Z",
  "is_acknowledged": false
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `diagnostic_id` | string | 诊断信息唯一标识 |
| `segment_id` | string | 所属段落 ID |
| `project_id` | string | 所属项目 ID |
| `issue_type` | enum | 问题类型：`low_confidence_match`、`insufficient_assets`、`metadata_missing` 等 |
| `confidence_score` | number | 置信度分数（0-1） |
| `root_cause` | enum | 根本原因：`missing_gps_data`、`missing_video`、`low_structure_note` 等 |
| `user_message` | string | 给用户看的易读文案 |
| `suggested_action` | enum | 建议动作：`manual_adjustment`、`skip_segment`、`use_alternative` 等 |
| `timestamp` | ISO 8601 | 诊断时间 |
| `is_acknowledged` | boolean | 用户是否已确认此诊断 |

---

### 2.4 项目配置（ProjectConfig）

```json
{
  "project_id": "proj_001",
  "user_selections": {
    "bgm_asset": "/path/to/bgm.mp3",
    "bgm_name": "Summer Vibes",
    "tts_voice": "voice_id_001",
    "tts_voice_name": "女性 - 温柔",
    "output_format": "mp4_16_9"
  },
  "system_parameters": {
    "processing_mode": "standard",
    "performance_tier": "m1_optimized",
    "enable_gpu_acceleration": true,
    "lightweight_mode_enabled": false
  },
  "created_at": "2026-04-17T10:00:00Z",
  "modified_at": "2026-04-17T10:30:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `project_id` | string | 项目唯一标识 |
| `user_selections.bgm_asset` | string | BGM 文件路径 |
| `user_selections.bgm_name` | string | BGM 名称 |
| `user_selections.tts_voice` | string | TTS 音色 ID |
| `user_selections.tts_voice_name` | string | TTS 音色名称 |
| `user_selections.output_format` | enum | 输出格式：`mp4_16_9`、`mp4_9_16` 等 |
| `system_parameters.processing_mode` | enum | 处理模式：`standard`、`lightweight` |
| `system_parameters.performance_tier` | enum | 性能档位：`m1_optimized`、`cpu_only` 等 |
| `system_parameters.enable_gpu_acceleration` | boolean | 是否启用 GPU 加速 |
| `system_parameters.lightweight_mode_enabled` | boolean | 是否启用轻量模式 |
| `created_at` | ISO 8601 | 创建时间 |
| `modified_at` | ISO 8601 | 修改时间 |

---

### 2.5 项目元数据（ProjectMetadata）

```json
{
  "project_id": "proj_001",
  "project_name": "日本东京之旅",
  "created_at": "2026-04-17T10:00:00Z",
  "last_modified_at": "2026-04-17T12:30:00Z",
  "total_processing_time_seconds": 3600,
  "media_count": {
    "videos": 25,
    "photos": 450,
    "total": 475
  },
  "total_video_duration_seconds": 3600,
  "story_word_count": 4200,
  "story_segment_count": 8,
  "current_version": "v1.2",
  "status": "completed"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `project_id` | string | 项目唯一标识 |
| `project_name` | string | 项目名称 |
| `created_at` | ISO 8601 | 创建时间 |
| `last_modified_at` | ISO 8601 | 最后修改时间 |
| `total_processing_time_seconds` | number | 总处理时长（秒） |
| `media_count.videos` | integer | 视频文件数 |
| `media_count.photos` | integer | 照片文件数 |
| `media_count.total` | integer | 总文件数 |
| `total_video_duration_seconds` | number | 原始视频总时长（秒） |
| `story_word_count` | integer | 游记总字数 |
| `story_segment_count` | integer | 故事段落数 |
| `current_version` | string | 当前版本标识 |
| `status` | enum | 项目状态：`draft`、`running`、`completed`、`failed` 等 |

---

## 3. 版本管理（借鉴 Git）

### 3.1 版本对象（ArtifactVersion）

```json
{
  "version_id": "v1.0",
  "artifact_type": "story_version",
  "project_id": "proj_001",
  "producer_stage": "story_skeleton_confirmation",
  "producer_run_id": "run_001",
  "upstream_versions": {
    "story_parsing": "story_parsing_run_001"
  },
  "created_at": "2026-04-17T10:30:00Z",
  "status": "active",
  "storage_path": "/projects/proj_001/versions/story/v1.0.json",
  "content_hash": "abc123def456",
  "invalidated_by": null,
  "metadata": {
    "segment_count": 8,
    "user_modifications": ["merge_segments", "reorder"]
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `version_id` | string | 版本唯一标识（如 v1.0、v1.1） |
| `artifact_type` | enum | 产物类型：`story_version`、`highlight_selection_version`、`timeline_version` 等 |
| `project_id` | string | 所属项目 ID |
| `producer_stage` | string | 生成该版本的阶段 |
| `producer_run_id` | string | 生成该版本的运行实例 ID |
| `upstream_versions` | object | 上游依赖版本映射 |
| `created_at` | ISO 8601 | 创建时间 |
| `status` | enum | 版本状态：`active`、`superseded`、`invalidated` |
| `storage_path` | string | 版本文件存储路径 |
| `content_hash` | string | 版本内容的哈希值（用于检测变化） |
| `invalidated_by` | string \| null | 失效原因或替换来源 |
| `metadata` | object | 版本元数据（如段落数、用户修改类型） |

### 3.2 版本依赖关系

```
asset_index (v1.0)
    ↓
story_parsing (v1.0) ← story_version (v1.0) ← story_skeleton_confirmation
    ↓
media_analysis (v1.0)
    ↓
alignment (v1.0) ← highlight_selection_version (v1.0) ← highlight_confirmation
    ↓
edit_planning (v1.0)
    ↓
narration_pack (v1.0)
    ↓
audio_mix_pack (v1.0)
    ↓
export_bundle (v1.0)
```

**版本失效规则**：
- 当上游版本变化时，所有依赖该版本的下游版本都应失效
- 例如：如果 `story_version` 从 v1.0 更新到 v1.1，则 `alignment`、`highlight_selection_version`、`edit_planning` 等都应失效

### 3.3 版本切换与恢复

```json
{
  "version_switch_record": {
    "from_version": "v1.0",
    "to_version": "v1.1",
    "switch_type": "regenerate_narration",
    "switched_at": "2026-04-17T13:00:00Z",
    "reason": "用户选择仅重写旁白"
  }
}
```

---

## 4. 用户决策记录（UserDecision）

```json
{
  "decision_id": "decision_001",
  "project_id": "proj_001",
  "node_name": "story_skeleton_confirmation",
  "decision_type": "merge_segments",
  "decision_payload": {
    "segment_ids": ["seg_001", "seg_002"],
    "new_segment_id": "seg_001_merged"
  },
  "based_on_version": "v1.0",
  "operator": "user",
  "decided_at": "2026-04-17T10:45:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `decision_id` | string | 决策唯一标识 |
| `project_id` | string | 所属项目 ID |
| `node_name` | enum | 所属交互节点：`story_skeleton_confirmation`、`highlight_confirmation` 等 |
| `decision_type` | enum | 决策类型：`merge_segments`、`delete_segment`、`reorder`、`accept_clip` 等 |
| `decision_payload` | object | 决策的具体内容（结构因 `decision_type` 而异） |
| `based_on_version` | string | 用户决策所基于的版本标识 |
| `operator` | enum | 操作者：`user`、`system` |
| `decided_at` | ISO 8601 | 决策时间 |

---

### 5. 替代呈现单元（AlternativeRenderUnit）

```json
{
  "unit_id": "alt_001",
  "segment_id": "seg_001",
  "project_id": "proj_001",
  "render_type": "photo_with_narration_transition",
  "photos": [
    {
      "photo_id": "photo_001",
      "file_path": "/path/to/photo_001.jpg",
      "duration_seconds": 3
    },
    {
      "photo_id": "photo_002",
      "file_path": "/path/to/photo_002.jpg",
      "duration_seconds": 3
    }
  ],
  "narration_transition": {
    "text": "接下来我们来到了...",
    "duration_seconds": 2
  },
  "reason": "insufficient_video_assets",
  "created_at": "2026-04-17T10:45:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `unit_id` | string | 替代呈现单元唯一标识 |
| `segment_id` | string | 所属段落 ID |
| `project_id` | string | 所属项目 ID |
| `render_type` | enum | 呈现类型：`photo_with_narration_transition`、`location_card`、`text_card` |
| `photos` | array | 照片列表（photo_with_narration_transition 和 location_card 适用） |
| `narration_transition` | object | 旁白过渡（photo_with_narration_transition 适用） |
| `location_info` | object | 地点信息（location_card 适用） |
| `text_content` | object | 文字内容（text_card 适用） |
| `reason` | enum | 使用替代呈现的原因：`insufficient_video_assets`、`low_confidence_match` 等 |
| `created_at` | ISO 8601 | 创建时间 |

#### 5.1 照片+旁白过渡（photo_with_narration_transition）

用于缺少视频镜头的段落，使用照片序列 + 旁白过渡。

```json
{
  "render_type": "photo_with_narration_transition",
  "photos": [
    {
      "photo_id": "photo_001",
      "file_path": "/path/to/photo_001.jpg",
      "duration_seconds": 3
    }
  ],
  "narration_transition": {
    "text": "接下来我们来到了...",
    "duration_seconds": 2
  }
}
```

#### 5.2 地点卡（location_card）

用于展示地点信息，包含地点名称、时间、可选的地点照片。

```json
{
  "render_type": "location_card",
  "location_info": {
    "location_name": "东京塔",
    "location_time": "2026-04-01 15:30",
    "latitude": 35.6762,
    "longitude": 139.7394,
    "description": "日本东京的标志性建筑"
  },
  "photos": [
    {
      "photo_id": "photo_location_001",
      "file_path": "/path/to/location_photo.jpg",
      "duration_seconds": 5
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `location_name` | string | 地点名称 |
| `location_time` | ISO 8601 | 到达地点的时间 |
| `latitude` | number | 纬度（可选） |
| `longitude` | number | 经度（可选） |
| `description` | string | 地点描述（可选） |

#### 5.3 文字卡（text_card）

用于展示文字信息，如段落摘要、引言、标题等。

```json
{
  "render_type": "text_card",
  "text_content": {
    "title": "第一天：启程",
    "subtitle": "从机场到酒店",
    "main_text": "今天一大早就出发去机场，经过3小时的飞行，终于到达了目的地。",
    "duration_seconds": 4,
    "background_color": "#ffffff",
    "text_color": "#000000",
    "font_size": "large"
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 标题（可选） |
| `subtitle` | string | 副标题（可选） |
| `main_text` | string | 主要文字内容 |
| `duration_seconds` | number | 文字卡显示时长（秒） |
| `background_color` | string | 背景颜色（十六进制） |
| `text_color` | string | 文字颜色（十六进制） |
| `font_size` | enum | 字体大小：`small`、`medium`、`large` |

---

## 6. 时间线（Timeline）

```json
{
  "timeline_id": "timeline_v1.0",
  "project_id": "proj_001",
  "version_id": "v1.0",
  "total_duration_seconds": 225,
  "segments": [
    {
      "segment_id": "seg_001",
      "start_time": 0,
      "end_time": 45,
      "clips": [
        {
          "clip_id": "clip_001",
          "start_time": 0,
          "end_time": 30,
          "transition": "fade"
        },
        {
          "clip_id": "clip_002",
          "start_time": 30,
          "end_time": 45,
          "transition": "cut"
        }
      ],
      "narration": {
        "text": "第一天的旅程开始...",
        "start_time": 0,
        "end_time": 15,
        "duration_seconds": 15
      }
    }
  ],
  "created_at": "2026-04-17T11:00:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `timeline_id` | string | 时间线唯一标识 |
| `project_id` | string | 所属项目 ID |
| `version_id` | string | 所属版本 ID |
| `total_duration_seconds` | number | 总时长（秒） |
| `segments` | array | 段落列表 |
| `segments[].segment_id` | string | 段落 ID |
| `segments[].start_time` | number | 段落在时间线中的起始时间（秒） |
| `segments[].end_time` | number | 段落在时间线中的结束时间（秒） |
| `segments[].clips` | array | 镜头列表 |
| `segments[].clips[].clip_id` | string | 镜头 ID |
| `segments[].clips[].start_time` | number | 镜头在时间线中的起始时间（秒） |
| `segments[].clips[].end_time` | number | 镜头在时间线中的结束时间（秒） |
| `segments[].clips[].transition` | enum | 过渡效果：`fade`、`cut`、`dissolve` 等 |
| `segments[].narration.text` | string | 旁白文本 |
| `segments[].narration.start_time` | number | 旁白起始时间（秒） |
| `segments[].narration.end_time` | number | 旁白结束时间（秒） |
| `segments[].narration.duration_seconds` | number | 旁白时长（秒，不超过 20 秒） |
| `created_at` | ISO 8601 | 创建时间 |

---

## 7. 音频混音计划（AudioMixPlan）

```json
{
  "audio_mix_id": "audio_v1.0",
  "project_id": "proj_001",
  "version_id": "v1.0",
  "tracks": [
    {
      "track_id": "narration",
      "type": "narration",
      "file_path": "/path/to/narration.mp3",
      "volume": 1.0
    },
    {
      "track_id": "ambient_sound",
      "type": "ambient",
      "segments": [
        {
          "segment_id": "seg_001",
          "file_path": "/path/to/ambient_001.mp3",
          "start_time": 0,
          "end_time": 10,
          "volume": 0.3
        }
      ]
    },
    {
      "track_id": "bgm",
      "type": "bgm",
      "file_path": "/path/to/bgm.mp3",
      "volume": 0.5
    }
  ],
  "created_at": "2026-04-17T11:30:00Z"
}
```

---

## 8. 导出产物（ExportBundle）

```json
{
  "export_id": "export_v1.0",
  "project_id": "proj_001",
  "version_id": "v1.0",
  "export_time": "2026-04-17T12:00:00Z",
  "outputs": {
    "video": {
      "file_path": "/exports/proj_001_v1.0.mp4",
      "format": "mp4",
      "resolution": "1920x1080",
      "duration_seconds": 225,
      "file_size_mb": 450
    },
    "subtitles": {
      "file_path": "/exports/proj_001_v1.0.srt",
      "format": "srt"
    },
    "narration": {
      "file_path": "/exports/proj_001_v1.0_narration.mp3",
      "format": "mp3"
    },
    "manifest": {
      "file_path": "/exports/proj_001_v1.0_manifest.json",
      "format": "json"
    }
  },
  "status": "success"
}
```

---

## 9. 数据存储结构

### 9.1 项目目录结构

```
/projects/
├── proj_001/
│   ├── config.json                    # 项目配置
│   ├── metadata.json                  # 项目元数据
│   ├── media/
│   │   ├── videos/
│   │   │   ├── video_001.mp4
│   │   │   └── ...
│   │   ├── photos/
│   │   │   ├── photo_001.jpg
│   │   │   └── ...
│   │   └── audio/
│   │       ├── bgm.mp3
│   │       └── ...
│   ├── versions/
│   │   ├── story/
│   │   │   ├── v1.0.json
│   │   │   └── v1.1.json
│   │   ├── highlight/
│   │   │   ├── v1.0.json
│   │   │   └── ...
│   │   ├── timeline/
│   │   │   └── v1.0.json
│   │   ├── audio/
│   │   │   └── v1.0.json
│   │   └── export/
│   │       ├── v1.0.mp4
│   │       ├── v1.0.srt
│   │       └── ...
│   ├── diagnostics/
│   │   ├── run_001_diagnostics.json
│   │   └── ...
│   └── cache/
│       ├── media_analysis_cache.json
│       └── ...
```

---

## 10. 数据库设计

### 10.1 数据库选择

V1 使用 **SQLite** 作为本地数据库，原因如下：
- 轻量级，无需额外服务
- 支持事务和 ACID 特性
- 跨平台兼容性好
- 适合单用户本地应用

### 10.2 数据库表结构

#### 表 1：projects（项目表）

```sql
CREATE TABLE projects (
  project_id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'draft',
  total_processing_time_seconds INTEGER DEFAULT 0,
  story_word_count INTEGER DEFAULT 0,
  story_segment_count INTEGER DEFAULT 0,
  current_version TEXT,
  UNIQUE(project_name)
);
```

#### 表 2：project_configs（项目配置表）

```sql
CREATE TABLE project_configs (
  config_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  bgm_asset TEXT,
  bgm_name TEXT,
  tts_voice TEXT,
  tts_voice_name TEXT,
  output_format TEXT DEFAULT 'mp4_16_9',
  processing_mode TEXT DEFAULT 'standard',
  performance_tier TEXT DEFAULT 'm1_optimized',
  enable_gpu_acceleration BOOLEAN DEFAULT 0,
  lightweight_mode_enabled BOOLEAN DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

#### 表 3：story_segments（故事段落表）

```sql
CREATE TABLE story_segments (
  segment_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  index_order INTEGER NOT NULL,
  summary TEXT,
  full_text TEXT,
  time_range_start TIMESTAMP,
  time_range_end TIMESTAMP,
  importance TEXT DEFAULT 'medium',
  is_highlighted BOOLEAN DEFAULT 0,
  user_marked_must_keep BOOLEAN DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

#### 表 4：clip_candidates（镜头候选表）

```sql
CREATE TABLE clip_candidates (
  clip_id TEXT PRIMARY KEY,
  segment_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  media_file_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  media_type TEXT,
  time_range_start TEXT,
  time_range_end TEXT,
  duration_seconds REAL,
  match_confidence REAL,
  match_reason TEXT,
  scene_tags TEXT,
  people_detected BOOLEAN,
  motion_level TEXT,
  user_disabled BOOLEAN DEFAULT 0,
  user_marked_memorial BOOLEAN DEFAULT 0,
  is_selected BOOLEAN DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (segment_id) REFERENCES story_segments(segment_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

#### 表 5：diagnostic_messages（诊断信息表）

```sql
CREATE TABLE diagnostic_messages (
  diagnostic_id TEXT PRIMARY KEY,
  segment_id TEXT,
  project_id TEXT NOT NULL,
  issue_type TEXT,
  confidence_score REAL,
  root_cause TEXT,
  user_message TEXT,
  suggested_action TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_acknowledged BOOLEAN DEFAULT 0,
  FOREIGN KEY (segment_id) REFERENCES story_segments(segment_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

#### 表 6：artifact_versions（产物版本表）

```sql
CREATE TABLE artifact_versions (
  version_id TEXT PRIMARY KEY,
  artifact_type TEXT NOT NULL,
  project_id TEXT NOT NULL,
  producer_stage TEXT,
  producer_run_id TEXT,
  upstream_versions TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'active',
  storage_path TEXT,
  content_hash TEXT,
  invalidated_by TEXT,
  metadata TEXT,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

#### 表 7：user_decisions（用户决策表）

```sql
CREATE TABLE user_decisions (
  decision_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  node_name TEXT,
  decision_type TEXT,
  decision_payload TEXT,
  based_on_version TEXT,
  operator TEXT DEFAULT 'user',
  decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

### 10.3 数据库初始化

系统启动时，自动检查数据库是否存在，如不存在则创建所有表。

### 10.4 数据持久化策略

- **配置数据**：实时写入数据库
- **版本数据**：每个版本生成时写入数据库
- **用户决策**：用户确认时立即写入数据库
- **诊断信息**：运行完成时写入数据库
- **中间产物**：以 JSON 文件形式存储在项目目录中，版本元数据存储在数据库中

---

## 11. 数据流与转换

### 10.1 从输入到输出的数据流

```
ProjectInputContract
    ↓
InputValidationReport
    ↓
AssetIndex
    ↓
StorySegment[] + DiagnosticMessage[]
    ↓
StoryVersion (用户确认)
    ↓
MediaAnalysisPack
    ↓
AlignmentVersion + ClipCandidate[]
    ↓
HighlightSelectionVersion (用户确认)
    ↓
Timeline
    ↓
NarrationPack
    ↓
AudioMixPlan
    ↓
ExportBundle
```

---

## 12. 数据一致性与验证

### 11.1 版本依赖验证

在加载任何版本前，系统必须验证：

1. 该版本的所有上游依赖版本是否仍然有效
2. 上游版本的内容哈希是否与记录一致
3. 如果上游版本已失效，则该版本也应失效

### 11.2 数据完整性检查

系统必须定期检查：

1. 所有引用的文件是否存在
2. 所有版本的存储路径是否正确
3. 所有用户决策是否被正确记录

---

## 13. 扩展性与兼容性

### 12.1 字段扩展规则

- 新增字段应添加到对象末尾，不应改变现有字段的位置
- 新增字段应有默认值，以保持向后兼容性
- 删除字段应标记为 `deprecated`，而不是直接删除

### 12.2 版本升级路径

- 当数据结构升级时，应提供迁移脚本
- 旧版本的数据应能被新版本的系统读取
- 新版本的数据应能被旧版本的系统忽略未知字段

---
