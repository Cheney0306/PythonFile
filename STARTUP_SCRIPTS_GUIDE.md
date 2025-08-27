# 🚀 新系统启动脚本完整指南

本文档详细介绍了newSystem文件夹下所有启动脚本的功能、用途和调用方法。

## 📋 目录

1. [系统初始化脚本](#系统初始化脚本)
2. [问答系统脚本](#问答系统脚本)
3. [QA数据集生成脚本](#qa数据集生成脚本)
4. [评估与对比脚本](#评估与对比脚本)
5. [测试与演示脚本](#测试与演示脚本)
6. [数据库管理脚本](#数据库管理脚本)
7. [工具脚本](#工具脚本)
8. [调用链路图](#调用链路图)

---

## 🔧 系统初始化脚本

### 1. `initialize_database.py` - 原始系统数据库初始化
**功能**: 初始化原始RAG系统的向量数据库
**用途**: 首次使用系统时必须运行，建立基础知识库

```bash
# 基本初始化
python initialize_database.py

# 重置数据库（删除现有数据）
python initialize_database.py --reset

# 限制处理条目数量（测试用）
python initialize_database.py --max-entries 100

# 测试API连接
python initialize_database.py --test-connection
```

**调用链路**: `data_loader.py` → `vector_database.py` → `embedding_client.py`

### 2. `initialize_enhanced_database.py` - 增强系统数据库初始化
**功能**: 初始化增强RAG系统的向量数据库，使用改进的嵌入策略
**用途**: 建立增强版知识库，支持多阶段检索

```bash
# 基本初始化
python initialize_enhanced_database.py

# 重置增强数据库
python initialize_enhanced_database.py --reset

# 静默模式（不显示详细进度）
python initialize_enhanced_database.py --quiet
```

**调用链路**: `enhanced_embedding_system.py` → `data_loader.py` → `embedding_client.py`

---

## 💬 问答系统脚本

### 3. `main_system.py` - 原始系统主入口
**功能**: 原始RAG系统的完整功能入口
**用途**: 运行完整的知识图谱RAG系统

```bash
# 启动系统（交互模式）
python main_system.py

# 重置数据库并启动
python main_system.py --reset-db

# 批量问答模式
python main_system.py --batch-mode --input questions.txt
```

**调用链路**: `retrieval_engine.py` → `vector_database.py` → `qa_generator.py`

### 4. `qa_system_demo.py` - 问答系统演示
**功能**: 完整的问答系统演示，展示RAG流程
**用途**: 演示系统功能，理解RAG工作原理

```bash
# 基本演示
python qa_system_demo.py

# 显示详细RAG流程
python qa_system_demo.py --show-details

# 交互模式
python qa_system_demo.py --interactive
```

### 5. `demo_enhanced_system.py` - 增强系统演示
**功能**: 演示增强系统的改进效果
**用途**: 对比原始系统和增强系统的差异

```bash
# 演示增强系统
python demo_enhanced_system.py

# 对比模式
python demo_enhanced_system.py --compare

# 详细分析模式
python demo_enhanced_system.py --detailed-analysis
```

---

## 📝 QA数据集生成脚本

### 6. `generate_text_qa.py` - 基于文本生成QA数据集
**功能**: 从XML文本数据生成问答对数据集
**用途**: 创建评估用的QA数据集

```bash
# 基本生成（处理全部文本）
python generate_text_qa.py

# 测试模式（处理5个文本）
python generate_text_qa.py --test-mode

# 限制处理数量
python generate_text_qa.py --max-texts 100

# 显示生成示例
python generate_text_qa.py --show-samples --test-mode

# 指定输出文件
python generate_text_qa.py --output-file my_qa_dataset.json

# 跳过已存在的文件
python generate_text_qa.py --skip-existing
```

**调用链路**: `text_based_qa_generator.py` → `retrieval_engine.py` → OpenAI API

### 7. `text_based_qa_generator.py` - QA生成器核心
**功能**: QA生成的核心逻辑实现
**用途**: 被其他脚本调用，不直接运行

---

## 📊 评估与对比脚本

### 8. `retrieval_evaluation_system.py` - 检索评估系统 ⭐
**功能**: 对比原始系统和增强系统的检索性能
**用途**: 系统性能评估，生成详细的对比报告

```bash
# 快速评估（20个问题）
python retrieval_evaluation_system.py --mode quick

# 完整评估（所有问题）
python retrieval_evaluation_system.py --mode full

# 自定义样本数量
python retrieval_evaluation_system.py --mode custom --sample-size 50

# 指定QA数据集路径
python retrieval_evaluation_system.py --qa-path custom_qa_datasets
```

**输出文件**:
- `evaluation_summary_*.json` - 评估摘要
- `full_evaluation_results_*.json` - 完整结果
- `metrics_comparison_*.csv` - CSV对比表
- `evaluation_report_*.md` - Markdown报告
- `charts_*/` - 可视化图表

**调用链路**: `retrieval_engine.py` + `enhanced_retrieval_engine.py` → 评估指标计算

### 9. `evaluation_viewer.py` - 评估结果查看器
**功能**: 查看、对比和导出评估结果
**用途**: 分析历史评估结果，生成报告

```bash
# 列出所有评估结果
python evaluation_viewer.py --action list

# 查看特定评估详情
python evaluation_viewer.py --action view --index 1

# 对比多个评估结果
python evaluation_viewer.py --action compare

# 导出Excel报告
python evaluation_viewer.py --action export

# 生成趋势分析
python evaluation_viewer.py --action trend
```

---

## 🧪 测试与演示脚本

### 10. `quick_demo.py` - 快速演示
**功能**: 系统基本功能的快速演示
**用途**: 验证系统安装和基本功能

```bash
# 快速演示
python quick_demo.py
```

### 11. `test_new_system.py` - 新系统测试
**功能**: 测试新系统的各项功能
**用途**: 功能验证和调试

### 12. `simple_enhanced_test.py` - 简单增强测试
**功能**: 测试增强系统的基本功能
**用途**: 验证增强系统工作正常

### 13. `quick_test_enhanced.py` - 快速增强测试
**功能**: 快速测试增强系统
**用途**: 开发调试用

---

## 🗄️ 数据库管理脚本

### 14. `check_database_content.py` - 数据库内容检查
**功能**: 检查向量数据库的内容和状态
**用途**: 诊断数据库问题，验证数据完整性

```bash
# 检查数据库内容
python check_database_content.py
```

**输出信息**:
- 数据库统计信息
- 样本数据展示
- 相似度查询测试

### 15. `supplement_missing_data.py` - 补充缺失数据
**功能**: 检查并补充数据库中缺失的数据
**用途**: 数据库维护和修复

---

## 🔧 工具脚本

### 16. `fix_qa_dataset.py` - QA数据集修复工具
**功能**: 修复QA数据集的JSON格式错误
**用途**: 数据清理和格式标准化

```bash
# 修复QA数据集
python fix_qa_dataset.py
```

### 17. `visualize_system_flow.py` - 系统流程可视化
**功能**: 生成系统架构和流程图
**用途**: 文档生成和系统理解

### 18. `visualize_qa_flowchart.py` - QA流程图生成
**功能**: 生成QA系统的流程图
**用途**: 文档和演示

---

## 🔄 调用链路图

### 完整系统启动流程
```
1. 数据库初始化
   initialize_database.py → data_loader.py → vector_database.py → embedding_client.py

2. 增强系统初始化  
   initialize_enhanced_database.py → enhanced_embedding_system.py → data_loader.py

3. QA数据集生成
   generate_text_qa.py → text_based_qa_generator.py → retrieval_engine.py → OpenAI API

4. 系统评估
   retrieval_evaluation_system.py → retrieval_engine.py + enhanced_retrieval_engine.py

5. 结果查看
   evaluation_viewer.py → evaluation/*.json
```

### 核心依赖关系
```
config.py (配置中心)
    ↓
embedding_client.py (嵌入服务)
    ↓
vector_database.py (向量数据库)
    ↓
retrieval_engine.py (检索引擎)
    ↓
qa_generator.py (QA生成)
```

---

## 🎯 常用场景指南

### 场景1: 我想生成QA问答对
```bash
# 1. 确保数据库已初始化
python initialize_database.py

# 2. 生成QA数据集
python generate_text_qa.py --test-mode

# 3. 检查生成结果
ls qa_datasets/
```

### 场景2: 我想运行问答系统
```bash
# 1. 初始化数据库（如果还没有）
python initialize_database.py

# 2. 运行问答演示
python qa_system_demo.py --interactive

# 或者运行完整系统
python main_system.py
```

### 场景3: 我想比较新旧系统性能并可视化
```bash
# 1. 初始化两个系统的数据库
python initialize_database.py
python initialize_enhanced_database.py

# 2. 修复QA数据集（如果需要）
python fix_qa_dataset.py

# 3. 运行评估对比
python retrieval_evaluation_system.py --mode quick

# 4. 查看评估结果
python evaluation_viewer.py --action list
python evaluation_viewer.py --action view --index 1

# 5. 导出Excel报告
python evaluation_viewer.py --action export
```

### 场景4: 我想检查系统状态
```bash
# 检查数据库内容
python check_database_content.py

# 快速系统测试
python quick_demo.py

# 增强系统测试
python demo_enhanced_system.py
```

---

## ⚠️ 注意事项

1. **首次使用**: 必须先运行数据库初始化脚本
2. **API密钥**: QA生成功能需要配置OpenAI API密钥
3. **依赖关系**: 确保所有依赖包已安装
4. **数据路径**: 检查config.py中的路径配置
5. **内存使用**: 大规模评估可能需要较多内存

---

## 📞 故障排除

### 常见问题
1. **数据库连接失败**: 检查ChromaDB路径和权限
2. **API调用失败**: 验证SiliconFlow API密钥
3. **JSON格式错误**: 运行`fix_qa_dataset.py`修复
4. **内存不足**: 减少批处理大小或样本数量

### 调试命令
```bash
# 测试API连接
python initialize_database.py --test-connection

# 检查数据库状态
python check_database_content.py

# 修复数据格式
python fix_qa_dataset.py
```

---

*最后更新: 2025-08-27*