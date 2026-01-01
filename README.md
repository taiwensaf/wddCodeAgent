# 工作流更新说明

## 改进内容

### 原流程问题
- 只处理规划出的**第一个任务**
- 其余任务被忽略
- 无法实现完整的多任务代码生成

### 新流程特性

#### 1. **多任务循环处理** (`agent_loop.py`)
- ✅ 遍历规划中的**所有任务**
- ✅ 对每个任务独立生成代码
- ✅ 将代码收集到 `task_modules` 列表

```python
for idx, task in enumerate(tasks):
    # 为每个任务生成代码
    code_result = code_generate(requirement, task_desc, model_name)
    task_modules.append({
        "task_name": task_name,
        "code": code,
        "filename": code_data.get("filename", f"{task_name}.py")
    })
```

#### 2. **代码汇总** (`coder.py`)
新增 `code_aggregate()` 函数，将所有任务代码合并为一个统一的项目文件：

```python
# 每个任务的代码按模块标记汇总
# Task 1: 模块A
[模块A代码]

# Task 2: 模块B
[模块B代码]

# Task 3: 模块C
[模块C代码]
```

#### 3. **一体化测试与调试**
- 汇总代码作为一个整体进行测试
- 如果测试失败，调试整个项目而非单个任务
- 调试后的代码自动重新保存和测试

#### 4. **改进的输出结构**
```
result = {
    "requirement": 原始需求,
    "plan": 规划结果（包含所有任务列表）,
    "generated_code": 汇总代码字符串,
    "generated_file": 保存的文件路径,
    "tests": 测试结果,
    "debug_history": 调试历史
}
```

## 使用示例

### 包含多个任务的需求
```bash
python cli.py "建立一个学生管理系统，包括：
1. 学生信息管理（增删改查）
2. 成绩管理（录入、计算、统计）
3. 班级管理（班级信息、学生分配）"
```

### 预期流程
```
[PLANNER] 规划出3个任务
[TASK 1/3] 处理任务: 学生信息管理 → 生成代码
[TASK 2/3] 处理任务: 成绩管理 → 生成代码
[TASK 3/3] 处理任务: 班级管理 → 生成代码
[INFO] 汇总代码已保存到: results/generated_code/project.py
[TESTER] 为汇总项目生成测试
[INFO] 执行测试...
```

## 核心函数变更

### 新增函数
- `code_aggregate(task_modules, project_name)` - 汇总多个任务代码
- `code_save_aggregated(aggregated_code, project_name)` - 保存汇总代码

### 修改函数
- `solve()` - 实现多任务循环和汇总逻辑

## 文件保存位置
- 汇总代码：`results/generated_code/{project_name}.py`
- 测试文件：`results/tests/test_*.py`
- 调试结果：保存在结果字典中

## 优势
1. **完整性** - 实现所有规划的任务
2. **整体性** - 作为一个项目进行测试和调试
3. **灵活性** - 支持任意数量的任务
4. **可追踪性** - 每个任务清晰标记，便于维护
