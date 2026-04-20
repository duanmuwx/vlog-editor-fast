# 工作流程指南

## 完整工作流程

### 第一步：项目创建与输入处理

**目标：** 创建项目并验证输入

**步骤：**

1. 准备素材
   - 收集视频文件（MP4、MOV 等）
   - 收集照片文件（JPG、PNG 等）
   - 准备游记文本（3000-5000 字）

2. 创建项目
```bash
POST /api/projects/create
{
  "project_name": "Paris Trip 2024",
  "travel_note": "Day 1: We departed from Beijing...",
  "media_files": ["/path/to/videos", "/path/to/photos"],
  "bgm_asset": "default_bgm.mp3",
  "tts_voice": "default_voice"
}
```

3. 验证输入
   - 系统自动检查游记长度
   - 验证媒体文件格式
   - 检查文件完整性

4. 索引素材
   - 提取视频元数据（时长、分辨率、帧率）
   - 提取照片元数据（EXIF、尺寸）
   - 生成素材索引

**预期结果：** 项目创建成功，素材已索引

---

### 第二步：故事解析与确认

**目标：** 将游记转化为故事骨架

**步骤：**

1. 解析游记
```bash
POST /api/projects/{project_id}/story/parse
```
   - 系统使用 LLM 解析游记
   - 提取故事段落（3-8 个）
   - 识别关键词、地点、时间

2. 查看故事骨架
```bash
GET /api/projects/{project_id}/skeleton/current
```
   - 查看生成的段落
   - 检查段落摘要和重要度

3. 调整故事骨架（可选）
   - **合并段落：** 将相关段落合并
   - **删除段落：** 移除不重要的段落
   - **重新排序：** 调整段落顺序
   - **编辑摘要：** 修改段落描述

4. 确认骨架
```bash
POST /api/projects/{project_id}/skeleton/{skeleton_id}/confirm
{
  "edits": [
    {"action": "merge", "segments": [0, 1]},
    {"action": "reorder", "order": [1, 0, 2, 3]}
  ]
}
```

**预期结果：** 故事骨架已确认，可进入下一阶段

---

### 第三步：媒体分析与对齐

**目标：** 将故事段落与媒体匹配

**步骤：**

1. 分析媒体
```bash
POST /api/projects/{project_id}/analyze-media
```
   - 检测视频镜头边界
   - 评估媒体质量
   - 提取视觉特征

2. 对齐媒体
```bash
POST /api/projects/{project_id}/align-media
```
   - 匹配故事段落与媒体
   - 生成候选镜头（每段 3-5 个）
   - 计算匹配置信度

3. 查看候选镜头
```bash
GET /api/projects/{project_id}/alignment-candidates/{segment_id}
```
   - 查看每个段落的候选镜头
   - 检查置信度分数
   - 查看替代呈现单元

4. 确认高光镜头
```bash
POST /api/projects/{project_id}/confirm-highlights
{
  "highlights": [
    {"segment_id": 0, "shot_id": 0, "confirmed": true},
    {"segment_id": 1, "shot_id": 5, "confirmed": true}
  ]
}
```
   - 为每个段落选择最佳镜头
   - 可替换不满意的镜头
   - 可禁用某些镜头

**预期结果：** 高光镜头已确认

---

### 第四步：成片生成

**目标：** 生成最终视频

**步骤：**

1. 生成时间线
```bash
POST /api/projects/{project_id}/edit-plan
```
   - 规划镜头时长
   - 设计转场效果
   - 分配旁白时间

2. 生成旁白
```bash
POST /api/projects/{project_id}/generate-narration
```
   - 为每个段落生成旁白文案
   - 使用 TTS 生成音频
   - 生成字幕文件

3. 混合音频
```bash
POST /api/projects/{project_id}/mix-audio
```
   - 混合旁白、原声、BGM
   - 调整音量平衡
   - 添加淡入淡出效果

4. 渲染导出
```bash
POST /api/projects/{project_id}/render-export
```
   - 渲染最终视频
   - 导出 MP4 文件
   - 生成字幕和配音文件

**预期结果：** 成片已生成，可在 `exports/` 目录中找到

---

### 第五步：版本管理与优化

**目标：** 优化成片或进行局部调整

**步骤：**

1. **仅重写旁白**
```bash
POST /api/projects/{project_id}/regenerate/narration_only
{
  "new_narration": "Updated narration text"
}
```
   - 修改旁白文案
   - 重新生成 TTS
   - 快速重新导出

2. **仅更换 BGM**
```bash
POST /api/projects/{project_id}/regenerate/bgm_only
{
  "new_bgm": "upbeat_bgm.mp3"
}
```
   - 选择新的背景音乐
   - 重新混合音频
   - 快速重新导出

3. **压缩时长**
```bash
POST /api/projects/{project_id}/regenerate/compress_duration
{
  "target_duration": 120  # 2 分钟
}
```
   - 缩短视频时长
   - 调整镜头和旁白
   - 重新导出

4. **版本切换**
```bash
POST /api/projects/{project_id}/versions/export/{version_id}/switch
```
   - 在不同版本间切换
   - 比较版本差异
   - 恢复到之前的版本

---

## 处理常见情况

### 情况 1：故事骨架不满意

**解决方案：**
1. 返回第二步
2. 调整故事骨架
3. 重新确认
4. 系统自动重新对齐媒体

### 情况 2：高光镜头不合适

**解决方案：**
1. 返回第三步
2. 查看其他候选镜头
3. 替换不满意的镜头
4. 重新生成成片

### 情况 3：低置信度匹配

**解决方案：**
- 系统会提示用户确认
- 可选择替代呈现单元（照片+旁白）
- 或手动选择其他镜头

### 情况 4：素材不足

**解决方案：**
- 系统自动使用替代呈现单元
- 照片 + 旁白
- 位置卡片
- 文字卡片

### 情况 5：导出失败

**解决方案：**
1. 检查磁盘空间
2. 尝试降低导出质量
3. 使用不同的编码器
4. 查看诊断报告获取详细信息

---

## 性能优化建议

### 加快处理速度

1. **减少媒体数量**
   - 预先筛选最好的素材
   - 删除重复或低质量的文件

2. **使用轻量模式**
   - 降低分析质量
   - 使用更快的对齐算法

3. **并行处理**
   - 系统自动并行处理多个任务
   - 充分利用多核 CPU

### 改进成片质量

1. **优化故事骨架**
   - 确保段落逻辑清晰
   - 合理分配时间

2. **精选高光镜头**
   - 选择最有表现力的镜头
   - 确保视觉连贯性

3. **调整音频混合**
   - 平衡旁白、原声、BGM
   - 使用淡入淡出效果

---

## 最佳实践

1. **准备充分的素材**
   - 至少 20-30 个视频
   - 至少 300-400 张照片
   - 确保素材质量

2. **编写清晰的游记**
   - 3000-5000 字
   - 逻辑清晰，结构完整
   - 包含具体的地点和时间

3. **定期保存版本**
   - 在重要阶段保存版本
   - 便于回滚和比较

4. **测试导出设置**
   - 先用低质量导出测试
   - 确认满意后再用高质量导出

5. **监控系统资源**
   - 确保有足够的磁盘空间
   - 监控内存使用情况
   - 关闭其他应用释放资源
