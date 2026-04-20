# 快速开始指南

## 安装

### 系统要求
- Python 3.10+
- 8GB RAM（推荐）
- 10GB 磁盘空间（用于项目和中间产物）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-repo/vlog-editor-fast.git
cd vlog-editor-fast
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入 KIMI_API_KEY
```

## 基本使用

### 1. 启动服务

```bash
python -m src.server.main
```

服务将在 `http://localhost:8000` 启动。

### 2. 创建项目

```bash
curl -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My Travel Vlog",
    "travel_note": "Day 1: We departed from Beijing...",
    "media_files": ["/path/to/video1.mp4", "/path/to/photo1.jpg"],
    "bgm_asset": "default_bgm.mp3",
    "tts_voice": "default_voice"
  }'
```

### 3. 查看项目状态

```bash
curl http://localhost:8000/api/projects/{project_id}
```

### 4. 运行完整流程

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/run
```

## 工作流程

### Phase 1: 输入处理
- 创建项目
- 验证输入（游记长度、媒体数量、文件格式）
- 索引素材（提取元数据）

### Phase 2: 故事解析
- 解析游记为故事段落
- 用户确认和调整故事骨架
- 冻结故事版本

### Phase 3: 媒体分析与对齐
- 分析媒体文件（质量、特征）
- 将故事段落与媒体对齐
- 用户确认高光镜头

### Phase 4: 成片生成
- 生成时间线
- 生成旁白和字幕
- 混合音频
- 渲染导出

### Phase 5: 版本管理
- 支持局部再生成（仅旁白、仅 BGM、压缩时长）
- 版本切换
- 失败恢复

## 常见问题

### Q: 处理需要多长时间？
A: 标准项目（30 个视频、400 张图片、4000 字游记）通常需要 60-120 分钟。

### Q: 支持哪些视频格式？
A: 支持 MP4、MOV、AVI、MKV 等常见格式。

### Q: 可以离线使用吗？
A: 故事解析需要 LLM API，其他功能可以离线使用。

### Q: 如何处理低置信度匹配？
A: 系统会提示用户确认，或自动使用替代呈现单元（照片+旁白）。

## 故障排除

### 问题：LLM API 错误
**解决方案：**
- 检查 KIMI_API_KEY 是否正确
- 检查网络连接
- 查看日志文件获取详细错误信息

### 问题：内存不足
**解决方案：**
- 减少媒体文件数量
- 使用轻量模式（降低质量）
- 增加系统内存

### 问题：导出失败
**解决方案：**
- 检查磁盘空间
- 尝试降低导出质量
- 使用不同的编码器

## 获取帮助

- 查看 API 文档：`http://localhost:8000/docs`
- 查看诊断报告：`/api/projects/{project_id}/diagnostics`
- 查看日志：`~/.vlog-editor/projects/{project_id}/logs/`
