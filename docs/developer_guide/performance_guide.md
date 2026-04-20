# 性能优化指南

## 性能基准

### 北极星指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 标准项目处理时长 | ≤ 120 分钟 | - |
| 内存占用 | ≤ 2GB | - |
| 磁盘占用 | ≤ 5GB | - |
| API 响应时间 | ≤ 1 秒 | - |
| 压力测试通过率 | ≥ 95% | - |

### 标准项目定义

- 视频：30 个（总时长 90 分钟）
- 图片：400 张
- 游记：4000 字
- 设备：MacBook Air M1，8GB RAM

## 性能瓶颈分析

### 1. 故事解析（Story Parser）

**瓶颈：** LLM API 调用时间

**优化策略：**

```python
# 缓存 LLM 结果
class CachedStoryParser:
    def __init__(self):
        self.cache = {}
    
    def parse(self, narrative):
        cache_key = hash(narrative)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self.call_llm(narrative)
        self.cache[cache_key] = result
        return result
```

**预期改进：** 重复项目快 10 倍

### 2. 媒体分析（Media Analyzer）

**瓶颈：** 视频处理和特征提取

**优化策略：**

```python
# 并行处理多个文件
from concurrent.futures import ThreadPoolExecutor

class ParallelMediaAnalyzer:
    def analyze_batch(self, media_files):
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.analyze_file, media_files))
        return results
```

**预期改进：** 4 倍加速（4 核 CPU）

### 3. 对齐引擎（Alignment Engine）

**瓶颈：** 多模态匹配计算

**优化策略：**

```python
# 使用向量化操作
import numpy as np

class OptimizedAlignmentEngine:
    def compute_similarity_matrix(self, segments, shots):
        # 向量化计算，避免循环
        segment_features = np.array([s['features'] for s in segments])
        shot_features = np.array([s['features'] for s in shots])
        
        # 使用矩阵乘法而不是循环
        similarity = np.dot(segment_features, shot_features.T)
        return similarity
```

**预期改进：** 5-10 倍加速

### 4. 渲染导出（Renderer）

**瓶颈：** FFmpeg 编码时间

**优化策略：**

```python
# 使用硬件加速
class HardwareAcceleratedRenderer:
    def render(self, timeline):
        # 使用 GPU 加速编码
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', 'input.mp4',
            '-c:v', 'h264_nvenc',  # NVIDIA GPU
            '-c:a', 'aac',
            'output.mp4'
        ]
        # 或使用 Apple Video Toolbox
        # '-c:v', 'h264_videotoolbox'
```

**预期改进：** 2-3 倍加速

## 缓存策略

### 1. LLM 结果缓存

```python
class LLMCache:
    def __init__(self, cache_dir="~/.vlog-editor/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, narrative):
        cache_key = hashlib.md5(narrative.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None
    
    def set(self, narrative, result):
        cache_key = hashlib.md5(narrative.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(result, f)
```

### 2. 媒体特征缓存

```python
class MediaFeatureCache:
    def __init__(self, db_path="~/.vlog-editor/cache/features.db"):
        self.db = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS media_features (
                file_hash TEXT PRIMARY KEY,
                features TEXT,
                timestamp REAL
            )
        """)
    
    def get_features(self, media_file):
        file_hash = self.compute_file_hash(media_file)
        cursor = self.db.execute(
            "SELECT features FROM media_features WHERE file_hash = ?",
            (file_hash,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None
```

### 3. 版本缓存失效

```python
class VersionAwareCache:
    def invalidate_downstream(self, artifact_name, version_id):
        """Invalidate downstream artifacts when upstream changes."""
        downstream_map = {
            "story_skeleton": ["media_analysis", "alignment"],
            "media_analysis": ["alignment"],
            "alignment": ["highlights", "timeline"],
            "highlights": ["timeline", "narration"],
            "timeline": ["narration", "audio", "export"],
        }
        
        for downstream in downstream_map.get(artifact_name, []):
            self.invalidate_cache(downstream)
```

## 并行处理

### 1. 媒体文件并行处理

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class ParallelMediaProcessor:
    def process_media_batch(self, media_files, max_workers=4):
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_file, f): f 
                for f in media_files
            }
            
            for future in as_completed(future_to_file):
                media_file = future_to_file[future]
                try:
                    results[media_file] = future.result()
                except Exception as e:
                    logger.error(f"Error processing {media_file}: {e}")
        
        return results
```

### 2. 异步 API 调用

```python
import asyncio
from aiohttp import ClientSession

class AsyncLLMClient:
    async def parse_narratives(self, narratives):
        async with ClientSession() as session:
            tasks = [
                self.parse_narrative_async(session, n)
                for n in narratives
            ]
            results = await asyncio.gather(*tasks)
        return results
    
    async def parse_narrative_async(self, session, narrative):
        async with session.post(
            'https://api.kimi.ai/parse',
            json={"text": narrative}
        ) as resp:
            return await resp.json()
```

## 数据库查询优化

### 1. 索引优化

```python
# 创建必要的索引
class DatabaseOptimization:
    def create_indexes(self):
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_id 
            ON projects(project_id)
        """)
        
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_artifact_version 
            ON artifact_versions(artifact_name, version_id)
        """)
        
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_segment_project 
            ON story_segments(project_id, segment_id)
        """)
```

### 2. 查询优化

```python
# 使用 JOIN 而不是多次查询
class OptimizedQueries:
    def get_project_with_artifacts(self, project_id):
        # 不好的做法：多次查询
        # project = self.get_project(project_id)
        # artifacts = self.get_artifacts(project_id)
        
        # 好的做法：单次 JOIN 查询
        query = """
            SELECT p.*, a.artifact_name, a.version_id
            FROM projects p
            LEFT JOIN artifact_versions a ON p.project_id = a.project_id
            WHERE p.project_id = ?
        """
        return self.db.execute(query, (project_id,)).fetchall()
```

## 内存优化

### 1. 流式处理大文件

```python
class StreamingMediaProcessor:
    def process_large_video(self, video_file, chunk_size=1024*1024):
        """Process video in chunks to avoid loading entire file."""
        with open(video_file, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Process chunk
                self.process_chunk(chunk)
                
                # Explicitly free memory
                del chunk
```

### 2. 及时释放资源

```python
class ResourceManager:
    def process_project(self, project_id):
        try:
            # Load data
            data = self.load_project_data(project_id)
            
            # Process
            result = self.process_data(data)
            
            return result
        finally:
            # Explicitly free memory
            del data
            gc.collect()
```

## 性能监控

### 1. 性能指标收集

```python
import time
from functools import wraps

def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        logger.info(f"{func.__name__}: {end_time - start_time:.2f}s, "
                   f"Memory: {end_memory - start_memory:.2f}MB")
        
        return result
    return wrapper

@measure_performance
def expensive_operation():
    pass
```

### 2. 性能报告生成

```python
class PerformanceReporter:
    def generate_report(self, benchmark_results):
        report = {
            "timestamp": time.time(),
            "total_duration": sum(r["duration"] for r in benchmark_results),
            "avg_duration": np.mean([r["duration"] for r in benchmark_results]),
            "peak_memory": max(r["memory"] for r in benchmark_results),
            "bottlenecks": self.identify_bottlenecks(benchmark_results),
        }
        return report
    
    def identify_bottlenecks(self, results):
        """Identify slowest operations."""
        sorted_results = sorted(results, key=lambda x: x["duration"], reverse=True)
        return sorted_results[:5]  # Top 5 slowest
```

## 优化检查清单

- [ ] 启用 LLM 结果缓存
- [ ] 启用媒体特征缓存
- [ ] 实现并行媒体处理
- [ ] 优化数据库查询
- [ ] 创建必要的数据库索引
- [ ] 实现流式处理大文件
- [ ] 启用硬件加速（如可用）
- [ ] 监控性能指标
- [ ] 定期生成性能报告
- [ ] 识别和优化瓶颈

## 性能测试结果

运行以下命令生成性能报告：

```bash
pytest tests/performance/ -v --benchmark-only
```

报告将保存在 `performance_results/` 目录中。
