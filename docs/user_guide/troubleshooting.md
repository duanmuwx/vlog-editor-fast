# 故障排除指南

## 常见问题与解决方案

### 项目创建问题

#### 问题：项目创建失败 - "Invalid input"

**症状：**
```
Error: Invalid input - narrative too short
```

**原因：**
- 游记长度不足 150 字
- 媒体文件数量不足

**解决方案：**
1. 确保游记至少 3000 字
2. 确保至少有 20 个视频或 300 张照片
3. 检查文件格式是否支持

```bash
# 检查游记长度
wc -c narrative.txt

# 检查媒体文件数量
ls -1 media/ | wc -l
```

#### 问题：项目创建失败 - "File not found"

**症状：**
```
Error: File not found - /path/to/media/video.mp4
```

**原因：**
- 文件路径不正确
- 文件已被删除或移动

**解决方案：**
1. 验证文件路径
2. 使用绝对路径而不是相对路径
3. 检查文件权限

```bash
# 验证文件存在
ls -la /path/to/media/video.mp4

# 检查文件权限
chmod 644 /path/to/media/video.mp4
```

---

### 故事解析问题

#### 问题：故事解析失败 - "LLM API error"

**症状：**
```
Error: LLM API error - Connection timeout
```

**原因：**
- KIMI_API_KEY 不正确
- 网络连接问题
- API 配额已用尽

**解决方案：**
1. 检查 API 密钥
```bash
echo $KIMI_API_KEY
```

2. 测试网络连接
```bash
curl -I https://api.kimi.ai
```

3. 检查 API 配额
   - 登录 Kimi 控制台
   - 查看 API 使用情况

4. 使用启发式回退
```python
# 系统会自动使用启发式方法
# 如果 LLM 失败，使用基于规则的解析
```

#### 问题：故事段落质量差

**症状：**
- 段落划分不合理
- 摘要不准确
- 重要度评分不对

**解决方案：**
1. 改进游记质量
   - 确保逻辑清晰
   - 使用清晰的段落分隔
   - 包含具体的时间和地点

2. 手动调整故事骨架
   - 合并相关段落
   - 删除不重要的段落
   - 重新排序

3. 重新解析
```bash
POST /api/projects/{project_id}/story/parse
```

---

### 媒体分析问题

#### 问题：媒体分析失败 - "Unsupported format"

**症状：**
```
Error: Unsupported format - .avi
```

**原因：**
- 文件格式不支持
- 文件已损坏

**解决方案：**
1. 转换文件格式
```bash
# 使用 FFmpeg 转换
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
```

2. 检查文件完整性
```bash
ffmpeg -v error -i input.mp4 -f null -
```

#### 问题：媒体分析耗时过长

**症状：**
- 分析 30 个视频需要 > 5 分钟
- 系统响应缓慢

**原因：**
- 视频文件过大
- 系统资源不足
- 分析质量设置过高

**解决方案：**
1. 使用轻量模式
```bash
POST /api/projects/{project_id}/analyze-media
{
  "quality": "low",
  "skip_detailed_analysis": true
}
```

2. 减少视频分辨率
```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
```

3. 增加系统资源
   - 关闭其他应用
   - 增加 RAM
   - 使用 SSD

---

### 对齐问题

#### 问题：对齐置信度低

**症状：**
```
Warning: Low confidence alignment for segment 2 (0.45)
```

**原因：**
- 媒体与故事不匹配
- 元数据缺失
- 媒体质量差

**解决方案：**
1. 检查媒体质量
   - 确保视频清晰
   - 确保照片相关

2. 添加元数据
   - 添加 GPS 信息
   - 添加时间戳
   - 添加描述

3. 手动选择镜头
   - 查看候选镜头
   - 选择最合适的
   - 或使用替代呈现单元

#### 问题：没有找到匹配的媒体

**症状：**
```
Error: No suitable media found for segment 3
```

**原因：**
- 媒体不足
- 媒体与故事不相关

**解决方案：**
1. 添加更多媒体
   - 补充相关视频或照片
   - 重新索引

2. 使用替代呈现单元
   - 照片 + 旁白
   - 位置卡片
   - 文字卡片

---

### 成片生成问题

#### 问题：旁白生成失败

**症状：**
```
Error: TTS generation failed - Voice not found
```

**原因：**
- TTS 音色不存在
- TTS 服务不可用

**解决方案：**
1. 检查可用的音色
```bash
GET /api/tts/voices
```

2. 使用默认音色
```bash
POST /api/projects/{project_id}/generate-narration
{
  "tts_voice": "default_voice"
}
```

#### 问题：导出失败 - "Insufficient disk space"

**症状：**
```
Error: Insufficient disk space - Need 5GB, have 2GB
```

**原因：**
- 磁盘空间不足

**解决方案：**
1. 清理磁盘
```bash
# 删除旧项目
rm -rf ~/.vlog-editor/projects/old_project_id

# 清理临时文件
rm -rf /tmp/vlog-*
```

2. 使用外部存储
   - 连接外部硬盘
   - 使用网络存储

3. 降低导出质量
```bash
POST /api/projects/{project_id}/render-export
{
  "quality": "medium",
  "bitrate": "2500k"
}
```

#### 问题：导出失败 - "FFmpeg error"

**症状：**
```
Error: FFmpeg error - Codec not found
```

**原因：**
- FFmpeg 未安装
- 编码器不可用

**解决方案：**
1. 安装 FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

2. 检查可用编码器
```bash
ffmpeg -codecs | grep h264
```

3. 使用替代编码器
```bash
POST /api/projects/{project_id}/render-export
{
  "codec": "h265"  # 或其他可用编码器
}
```

---

### 性能问题

#### 问题：处理时间过长

**症状：**
- 标准项目处理 > 120 分钟
- 系统响应缓慢

**原因：**
- 系统资源不足
- 媒体文件过大
- 分析质量过高

**解决方案：**
1. 检查系统资源
```bash
# 检查内存使用
free -h

# 检查 CPU 使用
top -b -n 1 | head -20

# 检查磁盘使用
df -h
```

2. 使用轻量模式
```bash
POST /api/projects/{project_id}/run
{
  "mode": "lightweight"
}
```

3. 优化媒体
   - 减少视频分辨率
   - 压缩文件大小
   - 删除不必要的文件

#### 问题：内存不足

**症状：**
```
Error: MemoryError - Cannot allocate memory
```

**原因：**
- 系统内存不足
- 内存泄漏

**解决方案：**
1. 增加系统内存
   - 升级 RAM
   - 关闭其他应用

2. 使用分批处理
```bash
POST /api/projects/{project_id}/analyze-media
{
  "batch_size": 10  # 每批处理 10 个文件
}
```

3. 启用虚拟内存
```bash
# Linux
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### 版本管理问题

#### 问题：版本切换失败

**症状：**
```
Error: Cannot switch to version v2 - Version not found
```

**原因：**
- 版本已被删除
- 版本 ID 不正确

**解决方案：**
1. 查看可用版本
```bash
GET /api/projects/{project_id}/versions/export
```

2. 使用正确的版本 ID
```bash
POST /api/projects/{project_id}/versions/export/{version_id}/switch
```

#### 问题：恢复失败

**症状：**
```
Error: Cannot recover from failure - Recovery point not found
```

**原因：**
- 恢复点已过期
- 中间产物已删除

**解决方案：**
1. 查看诊断报告
```bash
GET /api/projects/{project_id}/runs/{run_id}/diagnostics
```

2. 从最近的检查点恢复
```bash
POST /api/projects/{project_id}/runs/{run_id}/resume
```

3. 重新运行失败的阶段
```bash
POST /api/projects/{project_id}/runs/{run_id}/retry/{stage_name}
```

---

## 获取帮助

### 查看日志

```bash
# 查看项目日志
cat ~/.vlog-editor/projects/{project_id}/logs/project.log

# 查看 API 日志
tail -f ~/.vlog-editor/logs/api.log

# 查看系统日志
journalctl -u vlog-editor -f
```

### 生成诊断报告

```bash
# 生成完整诊断报告
GET /api/projects/{project_id}/diagnostics

# 生成性能报告
GET /api/projects/{project_id}/diagnostics?type=performance

# 生成错误报告
GET /api/projects/{project_id}/diagnostics?type=errors
```

### 联系支持

- GitHub Issues: https://github.com/your-repo/vlog-editor-fast/issues
- 文档: https://docs.vlog-editor.com
- 社区论坛: https://community.vlog-editor.com
