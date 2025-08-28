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

### 6. `generate_text_qa.py` - 基于文本生成QA数据集（原始系统）
**功能**: 使用原始RAG系统从XML文本数据生成问答对数据集
**用途**: 创建基准评估用的QA数据集
**流程**: Text → 原始检索 → CoTKR重写 → 传统Prompt → LLM → QA对

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

**调用链路**: `text_based_qa_generator.py` → `retrieval_engine.py` → `cotkr_rewriter.py` → OpenAI API
**数据库**: 原始向量数据库 (`new_kg_system_BAAI_bge-m3`)

### 6b. `generate_enhanced_qa.py` - 基于增强系统生成QA数据集 ⭐
**功能**: 使用增强RAG系统从XML文本数据生成问答对数据集
**用途**: 创建基于增强检索的QA数据集
**流程**: Text → 增强检索 → 多阶段重排 → 跳过重写 → One-shot Prompt → LLM → QA对

```bash
# 基本生成（使用增强系统）
python generate_enhanced_qa.py

# 测试模式
python generate_enhanced_qa.py --test-mode

# 限制处理数量
python generate_enhanced_qa.py --max-texts 50

# 显示生成示例
python generate_enhanced_qa.py --show-samples --test-mode
```

**调用链路**: `enhanced_qa_generator.py` → `enhanced_retrieval_engine.py` → OpenAI API
**数据库**: 增强向量数据库 (`enhanced_kg_system_BAAI_bge-m3`)
**特色**: 
- 多阶段检索重排
- 跳过重写模块，直接使用三元组
- 针对4种问题类型的One-shot提示
- 更高质量的QA对生成

### 7. `text_based_qa_generator.py` - 原始QA生成器核心
**功能**: 原始QA生成的核心逻辑实现
**用途**: 被`generate_text_qa.py`调用，不直接运行

### 7b. `enhanced_qa_generator.py` - 增强QA生成器核心 ⭐
**功能**: 增强QA生成的核心逻辑实现，包含One-shot提示策略
**用途**: 被`generate_enhanced_qa.py`调用，不直接运行
**特色**:
- 四种问题类型支持：关系(rel)、主语(sub)、宾语(obj)、类型(type)
- 针对性One-shot示例
- 跳过重写模块，直接使用检索结果
- 模拟QA生成（无需OpenAI API密钥即可测试）

### 8. `test_enhanced_qa_generation.py` - 增强QA生成测试
**功能**: 测试增强QA生成流程的各个步骤
**用途**: 验证增强QA生成器功能

```bash
# 运行完整测试
python test_enhanced_qa_generation.py
```

### 9. `simple_enhanced_qa_test.py` - 简单增强QA测试
**功能**: 简化的增强QA生成测试
**用途**: 快速验证基本功能

```bash
# 快速测试
python simple_enhanced_qa_test.py
```

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
- `qa_comparison_*.json` - 问答对比（JSON格式）⭐
- `qa_comparison_*.txt` - 问答对比（易读格式）⭐
- `qa_comparison_*.csv` - 问答对比（Excel格式）⭐
- `metrics_comparison_*.csv` - CSV对比表
- `evaluation_report_*.md` - Markdown报告
- `charts_*/` - 可视化图表

**新增功能**: 
- 🆕 **问答对比功能**: 自动保存问题和两个系统的答案对比
- 🆕 **多格式输出**: JSON（程序处理）、TXT（人工阅读）、CSV（Excel查看）
- 🆕 **改进幅度计算**: 自动计算性能改进百分比

**调用链路**: `retrieval_engine.py` + `enhanced_retrieval_engine.py` → 评估指标计算

### 8b. `rag_vs_llm_evaluation.py` - RAG系统与纯LLM对比评估 🆚
**功能**: 对比增强RAG系统与纯LLM的答案质量
**用途**: 验证RAG系统相对于纯LLM的优势
**流程**: 问题 → RAG系统答案 + 纯LLM答案 → 答案质量对比

```bash
# 快速评估（20个问题）
python rag_vs_llm_evaluation.py --mode quick

# 快速评估（自定义数量）
python rag_vs_llm_evaluation.py --mode quick --sample-size 50

# 完整评估（所有问题，需要大量API调用）
python rag_vs_llm_evaluation.py --mode full

# 指定数据集路径
python rag_vs_llm_evaluation.py --mode quick --qa-path custom_qa_datasets
```

**评估指标**:
- 精确匹配 (Exact Match)
- 包含匹配 (Contains Match)
- 词汇重叠 (Word Overlap)
- 综合分数 (Composite Score)

**输出文件**:
- `rag_vs_llm_full_results_*.json` - 完整结果
- `rag_vs_llm_summary_*.json` - 汇总结果
- `rag_vs_llm_qa_comparison_*.json` - 问答对比（JSON格式）⭐
- `rag_vs_llm_qa_comparison_*.txt` - 问答对比（易读格式）⭐
- `rag_vs_llm_qa_comparison_*.csv` - 问答对比（Excel格式）⭐
- `rag_vs_llm_report_*.md` - Markdown报告

**新增功能**: 
- 🆕 **RAG vs LLM问答对比**: 详细对比每个问题的RAG和LLM答案
- 🆕 **胜负统计**: 自动统计RAG系统相对于LLM的胜负情况
- 🆕 **分数差异分析**: 计算各项指标的具体差异值

**调用链路**: `enhanced_retrieval_engine.py` + OpenAI API → 答案质量评估
**注意**: 需要OpenAI API密钥，完整评估可能产生较高费用

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

### 14. `test_qa_comparison_enhanced.py` - 增强问答对比测试 ⭐
**功能**: 测试增强系统与原始系统的问答对比功能
**用途**: 验证问答对比功能，生成对比报告

```bash
# 测试问答对比功能
python test_qa_comparison_enhanced.py
```

### 15. `test_rag_vs_llm_qa_comparison.py` - RAG vs LLM问答对比测试 🆚
**功能**: 测试RAG系统与纯LLM的问答对比功能
**用途**: 验证RAG vs LLM对比功能，生成详细对比分析

```bash
# 测试RAG vs LLM问答对比功能
python test_rag_vs_llm_qa_comparison.py
```

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

3. QA数据集生成（原始系统）
   generate_text_qa.py → text_based_qa_generator.py → retrieval_engine.py → cotkr_rewriter.py → OpenAI API

4. QA数据集生成（增强系统）⭐
   generate_enhanced_qa.py → enhanced_qa_generator.py → enhanced_retrieval_engine.py → OpenAI API

5. 系统评估
   retrieval_evaluation_system.py → retrieval_engine.py + enhanced_retrieval_engine.py

6. RAG vs LLM对比
   rag_vs_llm_evaluation.py → enhanced_retrieval_engine.py + OpenAI API

7. 结果查看
   evaluation_viewer.py → evaluation/*.json
```

### QA生成流程对比
```
原始系统QA生成流程:
Text → 基础向量检索 → CoTKR重写 → 传统Prompt构建 → LLM生成 → QA对

增强系统QA生成流程:
Text → 多阶段检索 → 重排序 → 跳过重写 → One-shot Prompt构建 → LLM生成 → 高质量QA对
     ↓              ↓         ↓           ↓
   语义检索      实体/关系/类型   直接使用    针对4种问题类型
   +重排        多信号融合      三元组      的专门示例
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

**使用原始系统生成（传统方法）**:
```bash
# 1. 确保原始数据库已初始化
python initialize_database.py

# 2. 生成QA数据集（原始系统）
python generate_text_qa.py --test-mode

# 3. 检查生成结果
ls qa_datasets/
```

**使用增强系统生成（推荐方法）** ⭐:
```bash
# 1. 确保增强数据库已初始化
python initialize_enhanced_database.py

# 2. 生成QA数据集（增强系统）
python generate_enhanced_qa.py --test-mode

# 3. 检查生成结果
ls qa_datasets/

# 4. 可选：测试增强生成流程
python test_enhanced_qa_generation.py
```

**两种方法的区别**:
- **原始系统**: Text → 基础检索 → CoTKR重写 → 传统Prompt → QA对
- **增强系统**: Text → 多阶段检索重排 → 跳过重写 → One-shot Prompt → 高质量QA对

**增强系统优势**:
- 更准确的检索结果（多阶段重排）
- 更高质量的QA对（One-shot提示）
- 支持4种问题类型（关系、主语、宾语、类型）
- 更快的生成速度（跳过重写步骤）

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

### 场景4: 我想比较RAG系统与纯LLM的答案质量 🆚
```bash
# 1. 确保增强数据库已初始化
python initialize_enhanced_database.py

# 2. 快速对比测试（需要OpenAI API密钥）
python rag_vs_llm_evaluation.py --mode quick --sample-size 10

# 3. 测试问答对比功能
python test_rag_vs_llm_qa_comparison.py

# 4. 查看对比结果
# 结果会自动保存到 evaluation/ 目录
# 包含详细的问答对比文件

# 5. 完整对比评估（谨慎使用，费用较高）
python rag_vs_llm_evaluation.py --mode full
```

**RAG vs LLM对比优势**:
- 验证RAG系统的实际价值
- 量化知识检索的贡献
- 识别LLM的知识盲区
- 为系统改进提供方向
- 🆕 **详细问答对比**: 逐题对比RAG和LLM的答案质量
- 🆕 **胜负统计**: 自动统计RAG系统的优势领域

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

## 🎯 增强QA生成系统详解

### 📋 四种问题类型支持

增强QA生成系统支持四种不同类型的问题生成，每种都有专门的One-shot示例：

#### 1. **关系提问 (rel)**
- **目标**: 询问两个实体之间的关系
- **示例**: 
  ```
  Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
  Question: What is the relationship between Amsterdam Airport Schiphol and Haarlemmermeer?
  Answer: location
  ```

#### 2. **主语提问 (sub)**
- **目标**: 询问具有某种关系的主体实体
- **示例**:
  ```
  Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
  Question: What is located in Haarlemmermeer?
  Answer: Amsterdam Airport Schiphol
  ```

#### 3. **宾语提问 (obj)**
- **目标**: 询问主体实体的关系对象
- **示例**:
  ```
  Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
  Question: Where is Amsterdam Airport Schiphol located?
  Answer: Haarlemmermeer
  ```

#### 4. **类型提问 (type)**
- **目标**: 询问实体的类别或类型
- **示例**:
  ```
  Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
  Schema: (Airport, location, City)
  Question: What is Amsterdam Airport Schiphol?
  Answer: Airport
  ```

### 🚀 增强系统优势

1. **多阶段检索**: 先语义检索，再多信号重排
2. **跳过重写**: 直接使用原始三元组，避免信息损失
3. **One-shot提示**: 针对每种问题类型的专门示例
4. **质量保证**: 更准确、更自然的问答对
5. **类型多样**: 自动生成多种类型的问题

### 🔧 使用建议

**开发测试阶段**:
```bash
# 快速测试功能
python simple_enhanced_qa_test.py

# 详细流程测试
python test_enhanced_qa_generation.py

# 小规模生成测试
python generate_enhanced_qa.py --test-mode
```

**生产使用阶段**:
```bash
# 生成完整数据集
python generate_enhanced_qa.py --max-texts 1000

# 生成特定数量
python generate_enhanced_qa.py --max-texts 500 --output-file custom_qa_dataset.json
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
5. **增强QA生成失败**: 确保增强数据库已初始化
6. **OpenAI API密钥未设置**: 增强QA生成器会自动使用模拟生成进行测试
7. **RAG vs LLM评估失败**: 确保设置了有效的OpenAI API密钥
8. **LLM调用费用过高**: 使用小样本测试，避免完整评估

### 调试命令
```bash
# 测试API连接
python initialize_database.py --test-connection

# 检查数据库状态
python check_database_content.py

# 修复数据格式
python fix_qa_dataset.py

# 测试增强QA生成
python simple_enhanced_qa_test.py

# 检查增强数据库状态
python initialize_enhanced_database.py --reset

# 测试RAG vs LLM对比
python test_rag_vs_llm.py
```

### 增强QA生成故障排除
```bash
# 问题：增强检索失败
# 解决：检查增强数据库是否已初始化
python initialize_enhanced_database.py

# 问题：QA生成质量不佳
# 解决：检查One-shot示例和prompt构造
python test_enhanced_qa_generation.py

# 问题：生成速度慢
# 解决：减少处理文本数量或检索结果数量
python generate_enhanced_qa.py --test-mode --max-texts 10
```

### 问答对比功能故障排除 ⭐
```bash
# 问题：问答对比文件未生成
# 解决：检查评估结果结构和字段名称
python test_qa_comparison_enhanced.py

# 问题：RAG vs LLM对比失败
# 解决：检查OpenAI API密钥设置
python test_rag_vs_llm_qa_comparison.py

# 问题：CSV文件中文显示乱码
# 解决：使用UTF-8-BOM编码，在Excel中正确打开

# 问题：胜负统计计算错误
# 解决：检查评分指标和胜负判定逻辑
```

---

## 🆕 最新功能亮点 (2025-08-28)

### 问答对比功能 ⭐
- **双重对比支持**: 增强系统 vs 原始系统 + RAG系统 vs 纯LLM
- **多格式输出**: JSON（程序处理）+ TXT（人工阅读）+ CSV（Excel分析）
- **详细分析**: 胜负统计、改进幅度、分数差异
- **自动集成**: 评估时自动生成，无需额外操作

### 核心优势
1. **直观对比**: 清晰展示系统改进效果
2. **量化分析**: 精确的数值对比和统计
3. **多维度评估**: 支持不同问题类型的分析
4. **易于使用**: 一键生成，多格式查看

### 使用建议
- 开发阶段：使用测试脚本快速验证功能
- 评估阶段：运行完整评估获得详细对比
- 分析阶段：结合TXT和CSV文件进行深度分析
- 报告阶段：利用Excel制作可视化图表

---

*最后更新: 2025-08-28*