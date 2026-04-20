# 测试指南

## 测试框架概览

项目使用 pytest 作为测试框架，包含以下测试类型：

- **单元测试** - 测试单个模块的功能
- **集成测试** - 测试模块间的交互
- **性能测试** - 测试系统性能指标
- **压力测试** - 测试系统在极限条件下的表现
- **端到端测试** - 测试完整的用户工作流程

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定类型的测试

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 性能测试
pytest tests/performance/ -v -m performance

# 压力测试
pytest tests/stress/ -v -m stress

# 端到端测试
pytest tests/e2e/ -v -m e2e
```

### 运行特定测试文件

```bash
pytest tests/unit/test_project_manager.py -v
```

### 运行特定测试用例

```bash
pytest tests/unit/test_project_manager.py::TestProjectManager::test_create_project -v
```

## 测试覆盖率

### 生成覆盖率报告

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### 查看覆盖率报告

```bash
# 生成 HTML 报告
open htmlcov/index.html

# 或查看终端输出
pytest --cov=src --cov-report=term-missing
```

### 覆盖率目标

- 整体代码覆盖率：≥ 80%
- 新代码覆盖率：≥ 90%
- 关键路径覆盖率：100%

## 性能测试

### 运行性能基准测试

```bash
pytest tests/performance/ -v --benchmark-only
```

### 生成性能报告

```bash
pytest tests/performance/ -v
# 报告保存在 performance_results/ 目录
```

### 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 项目创建 | < 1s | 创建项目并索引素材 |
| 故事解析 | < 10s | 解析游记为段落 |
| 媒体分析 | < 5s | 分析 30 个视频 |
| 对齐引擎 | < 3s | 匹配段落与媒体 |
| 成片生成 | < 15s | 生成时间线和旁白 |
| 完整流程 | < 120min | 标准项目处理时长 |

## 压力测试

### 运行压力测试

```bash
pytest tests/stress/ -v -m stress
```

### 压力测试场景

1. **大规模媒体处理**
   - 100+ 个视频文件
   - 1000+ 张图片
   - 验证内存管理

2. **长篇幅游记**
   - 10000+ 字游记
   - 验证 LLM 解析能力

3. **并发请求**
   - 5+ 个项目同时处理
   - 验证 API 并发能力

4. **资源受限**
   - 模拟低内存环境
   - 验证降级策略

## 端到端测试

### 运行端到端测试

```bash
pytest tests/e2e/ -v -m e2e
```

### 测试场景

1. **标准工作流程** - 从导入到成片的完整流程
2. **故事骨架调整** - 用户修改段落后重新对齐
3. **高光确认与替代呈现** - 处理素材不足的情况
4. **局部再生成** - 三类再生成都能成功
5. **低置信处理** - 显式提示和人工确认
6. **导出失败恢复** - 支持重新导出

## 编写新测试

### 单元测试模板

```python
import pytest
from src.server.modules.project_manager import ProjectManager

class TestProjectManager:
    @pytest.fixture
    def project_manager(self):
        return ProjectManager()
    
    def test_create_project(self, project_manager):
        # Arrange
        project_name = "Test Project"
        
        # Act
        result = project_manager.create_project(project_name)
        
        # Assert
        assert result is not None
        assert result.name == project_name
```

### 集成测试模板

```python
import pytest
from src.server.api.projects import router

class TestProjectFlow:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from src.server.main import app
        return TestClient(app)
    
    def test_complete_workflow(self, client):
        # Create project
        response = client.post("/api/projects/create", json={...})
        assert response.status_code == 200
        
        # Parse story
        response = client.post(f"/api/projects/{project_id}/story/parse")
        assert response.status_code == 200
```

### 性能测试模板

```python
import pytest
from tests.performance.benchmark_runner import BenchmarkRunner

class TestPerformance:
    @pytest.fixture
    def benchmark_runner(self):
        return BenchmarkRunner()
    
    def test_operation_performance(self, benchmark_runner):
        benchmark = benchmark_runner.start_benchmark("operation_name")
        
        # Perform operation
        time.sleep(0.1)
        
        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("operation_name", benchmark)
        
        assert benchmark["duration"] < 1.0
```

## 测试最佳实践

### 1. 使用 Fixtures

```python
@pytest.fixture
def sample_project():
    """Create a sample project for testing."""
    project = create_test_project()
    yield project
    cleanup_test_project(project)
```

### 2. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("input1", "output1"),
    ("input2", "output2"),
])
def test_function(input, expected):
    assert function(input) == expected
```

### 3. Mock 外部依赖

```python
from unittest.mock import patch

@patch('src.server.modules.story_parser.call_llm_api')
def test_story_parsing(mock_llm):
    mock_llm.return_value = {"segments": [...]}
    result = parse_story("narrative")
    assert len(result) > 0
```

### 4. 测试异常处理

```python
def test_invalid_input():
    with pytest.raises(ValueError):
        function_that_raises()
```

### 5. 使用标记分类测试

```python
@pytest.mark.unit
def test_unit_test():
    pass

@pytest.mark.integration
def test_integration_test():
    pass

@pytest.mark.slow
def test_slow_test():
    pass
```

## 持续集成

### GitHub Actions 配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src
      - run: pytest tests/performance/ -v
```

## 故障排除

### 问题：测试超时

**解决方案：**
```bash
pytest --timeout=300  # 设置 5 分钟超时
```

### 问题：内存不足

**解决方案：**
```bash
pytest -n auto  # 使用 xdist 并行运行
```

### 问题：测试不稳定

**解决方案：**
- 检查是否有竞态条件
- 确保 fixtures 正确清理
- 使用 `pytest-repeat` 重复运行

```bash
pytest --count=10  # 运行 10 次
```

## 性能优化建议

1. **使用 pytest-xdist 并行运行测试**
```bash
pytest -n auto
```

2. **使用 pytest-benchmark 进行基准测试**
```bash
pytest --benchmark-only
```

3. **缓存测试数据**
```python
@pytest.fixture(scope="session")
def large_dataset():
    return load_large_dataset()
```

4. **跳过慢速测试**
```bash
pytest -m "not slow"
```

## 测试报告

### 生成 HTML 报告

```bash
pytest --html=report.html --self-contained-html
```

### 生成 JUnit XML 报告

```bash
pytest --junit-xml=report.xml
```

### 生成覆盖率报告

```bash
pytest --cov=src --cov-report=html
```
