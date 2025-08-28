# 检索系统评估指南

## 🎯 评估系统功能

我们的评估系统提供了全面的性能对比分析，支持多种输出格式和可视化。

### 📊 评估指标
- **Precision@K**: 前K个结果中相关结果的比例
- **Recall@K**: 前K个结果覆盖的相关结果比例  
- **nDCG@K**: 归一化折扣累积增益

### 🔄 对比系统
- **原始系统**: 使用基础嵌入策略的RAG系统
- **增强系统**: 使用自然语言模板和多阶段重排的RAG系统

## 🚀 快速开始

### 1. 运行完整评估
```bash
python retrieval_evaluation_system.py
```

### 2. 运行快速评估（20个样本）
```bash
python retrieval_evaluation_system.py --mode quick
```

### 3. 自定义评估
```bash
# 指定样本数量和K值
python retrieval_evaluation_system.py --mode custom --sample-size 50 --k-values 1 3 5

# 指定输出目录
python retrieval_evaluation_system.py --mode custom --output-dir my_evaluation
```

## 📁 输出文件结构

评估完成后，会在 `evaluation/` 目录下生成以下文件：

```
evaluation/
├── full_evaluation_results_20241127_143022.json     # 完整评估结果
├── evaluation_summary_20241127_143022.json          # 汇总指标
├── metrics_comparison_20241127_143022.csv           # CSV格式对比
├── evaluation_report_20241127_143022.md             # Markdown报告
├── detailed_results_20241127_143022.json            # 详细结果（可选）
└── charts_20241127_143022/                          # 可视化图表
    ├── metrics_comparison.png                       # 指标对比柱状图
    ├── k_trend_analysis.png                         # K值趋势图
    └── improvement_analysis.png                     # 改进幅度图
```

## 📊 结果查看

### 1. 列出所有评估结果
```bash
python evaluation_viewer.py --action list
```

### 2. 查看特定评估结果
```bash
python evaluation_viewer.py --action view --index 1
```

### 3. 对比多个评估结果
```bash
python evaluation_viewer.py --action compare
```

### 4. 导出到Excel
```bash
python evaluation_viewer.py --action export --output comparison.xlsx
```

## 📈 输出示例

### 控制台输出
```
📊 评估报告 (共 100 个问题)
================================================================================

🔍 原始系统:
----------------------------------------

  K=1:
    PRECISION@1: 0.6500 (±0.4787)
    RECALL@1: 0.4200 (±0.3891)
    NDCG@1: 0.6100 (±0.4234)

  K=3:
    PRECISION@3: 0.5833 (±0.3456)
    RECALL@3: 0.7200 (±0.2987)
    NDCG@3: 0.6789 (±0.2876)

🚀 增强系统:
----------------------------------------

  K=1:
    PRECISION@1: 0.7200 (±0.4123)
    RECALL@1: 0.5100 (±0.3567)
    NDCG@1: 0.6900 (±0.3789)

  K=3:
    PRECISION@3: 0.6567 (±0.3234)
    RECALL@3: 0.8100 (±0.2456)
    NDCG@3: 0.7456 (±0.2345)

📈 改进幅度:
----------------------------------------

  K=1:
    PRECISION@1: +10.77%
    RECALL@1: +21.43%
    NDCG@1: +13.11%

  K=3:
    PRECISION@3: +12.58%
    RECALL@3: +12.50%
    NDCG@3: +9.82%
```

### Markdown报告示例
```markdown
# 检索系统评估报告

**生成时间**: 20241127_143022
**评估问题数**: 100
**嵌入模型**: BAAI/bge-m3

## 📊 系统性能对比

### K=1 指标对比

| 指标 | 原始系统 | 增强系统 | 改进幅度 |
|------|----------|----------|----------|
| PRECISION@1 | 0.6500 | 0.7200 | +10.77% |
| RECALL@1 | 0.4200 | 0.5100 | +21.43% |
| NDCG@1 | 0.6100 | 0.6900 | +13.11% |
```

### CSV格式
```csv
System,Metric,K,Mean,Std,Count
原始系统,PRECISION,1,0.6500,0.4787,100
原始系统,RECALL,1,0.4200,0.3891,100
原始系统,NDCG,1,0.6100,0.4234,100
增强系统,PRECISION,1,0.7200,0.4123,100
增强系统,RECALL,1,0.5100,0.3567,100
增强系统,NDCG,1,0.6900,0.3789,100
```

## 🔧 配置选项

### config.py 中的评估配置
```python
# 评估配置
EVALUATION_OUTPUT_DIR = "evaluation"  # 评估结果输出目录
EVALUATION_SAMPLE_SIZE = 100          # 默认评估样本数量
EVALUATION_K_VALUES = [1, 3, 5, 10]   # 默认K值
SAVE_DETAILED_RESULTS = True          # 是否保存详细结果
SAVE_SUMMARY_CHARTS = True            # 是否保存图表
```

### 自定义配置
```python
# 修改默认配置
EVALUATION_SAMPLE_SIZE = 200          # 增加样本数量
EVALUATION_K_VALUES = [1, 5, 10, 20]  # 自定义K值
SAVE_SUMMARY_CHARTS = False           # 禁用图表生成（如果没有matplotlib）
```

## 📊 可视化图表

### 1. 指标对比柱状图 (metrics_comparison.png)
- 显示不同K值下两个系统的Precision、Recall、nDCG对比
- 使用柱状图形式，便于直观比较

### 2. K值趋势图 (k_trend_analysis.png)
- 显示随着K值增加，各指标的变化趋势
- 帮助理解系统在不同检索深度下的表现

### 3. 改进幅度图 (improvement_analysis.png)
- 显示增强系统相对于原始系统的改进百分比
- 绿色表示改进，红色表示退步

## 🎯 使用场景

### 1. 系统开发阶段
```bash
# 快速验证改进效果
python retrieval_evaluation_system.py --mode quick

# 查看结果
python evaluation_viewer.py --action view --index 1
```

### 2. 正式评估阶段
```bash
# 完整评估
python retrieval_evaluation_system.py --mode full

# 生成报告
python evaluation_viewer.py --action export
```

### 3. 持续监控
```bash
# 定期评估
python retrieval_evaluation_system.py --mode custom --sample-size 50

# 对比历史结果
python evaluation_viewer.py --action compare
```

## 💡 最佳实践

### 1. 评估前准备
- 确保两个系统的数据库都已初始化
- 准备足够的QA测试数据
- 检查API配额和网络连接

### 2. 结果分析
- 关注多个指标的综合表现，不要只看单一指标
- 注意标准差，了解结果的稳定性
- 对比不同K值下的表现趋势

### 3. 持续改进
- 定期进行评估，跟踪性能变化
- 保存历史评估结果，便于长期分析
- 基于评估结果调整系统参数

## 🚨 常见问题

### Q1: 评估运行很慢怎么办？
A: 使用快速评估模式或减少样本数量
```bash
python retrieval_evaluation_system.py --mode quick
# 或
python retrieval_evaluation_system.py --mode custom --sample-size 20
```

### Q2: 图表生成失败
A: 安装matplotlib或禁用图表生成
```bash
pip install matplotlib
# 或在config.py中设置 SAVE_SUMMARY_CHARTS = False
```

### Q3: 内存不足
A: 减少样本数量或批处理大小
```python
EVALUATION_SAMPLE_SIZE = 50
BATCH_SIZE = 16
```

### Q4: 找不到QA数据
A: 确保qa_datasets目录中有QA数据文件
```bash
# 生成QA数据
python generate_text_qa.py --test-mode
```

这个评估系统为你提供了全面的性能分析工具，帮助你量化和跟踪RAG系统的改进效果！