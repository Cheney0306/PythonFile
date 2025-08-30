# 增强的RAG vs LLM评估系统使用指南

## 🎯 新增功能

本次更新为 `rag_vs_llm_evaluation.py` 添加了以下重要功能：

### 1. 检索性能埋点
- **Precision@k**: 检索结果中相关文档的比例
- **Recall@k**: 检索到的相关文档占总相关文档的比例  
- **nDCG@k**: 归一化折损累积增益，考虑排序质量

支持的k值：1, 3, 5

### 2. 简化问答记录
生成 `.jsonl` 格式的简化记录文件，每行包含：
```json
{
  "question": "问题内容",
  "expected_answer": "标准答案", 
  "rag_answer": "RAG系统答案",
  "llm_answer": "纯LLM答案"
}
```

## 🚀 使用方法

### 快速评估（推荐）
```bash
python rag_vs_llm_evaluation.py --mode quick --sample-size 20
```

### 完整评估
```bash
python rag_vs_llm_evaluation.py --mode full --qa-path qa_datasets
```

### 测试新功能
```bash
python test_enhanced_rag_vs_llm_evaluation.py
```

## 📊 输出文件说明

运行评估后会生成以下文件：

### 1. 完整结果文件
- **文件名**: `rag_vs_llm_full_results_{timestamp}.json`
- **内容**: 包含所有详细评估数据，包括检索指标

### 2. 汇总结果文件  
- **文件名**: `rag_vs_llm_summary_{timestamp}.json`
- **内容**: 统计汇总信息，包括检索性能统计

### 3. 简化问答记录 ⭐ 新增
- **文件名**: `simple_qa_records_{timestamp}.jsonl`
- **格式**: 每行一个JSON对象
- **用途**: 便于后续分析和处理

### 4. 问答对比文件
- **JSON格式**: `rag_vs_llm_qa_comparison_{timestamp}.json`
- **文本格式**: `rag_vs_llm_qa_comparison_{timestamp}.txt`
- **CSV格式**: `rag_vs_llm_qa_comparison_{timestamp}.csv`

### 5. Markdown报告
- **文件名**: `rag_vs_llm_report_{timestamp}.md`
- **内容**: 包含检索指标的美观报告

## 📈 检索指标说明

### Precision@k
- **定义**: 前k个检索结果中相关文档的比例
- **计算**: 相关文档数 / k
- **范围**: [0, 1]，越高越好

### Recall@k  
- **定义**: 前k个检索结果中检索到的相关文档占总相关文档的比例
- **计算**: 检索到的相关文档数 / 总相关文档数
- **范围**: [0, 1]，越高越好

### nDCG@k
- **定义**: 归一化折损累积增益，考虑文档排序位置
- **特点**: 排序越靠前的相关文档权重越高
- **范围**: [0, 1]，越高越好

## 🔧 相关性判断机制

系统使用以下方法判断检索文档的相关性：

1. **文本提取**: 从检索项中提取文本内容
2. **词汇重叠**: 计算与期望答案的词汇重叠度
3. **阈值判断**: 重叠度 > 0.1 视为相关文档
4. **分数计算**: 基于重叠度计算连续相关性分数

## 📋 示例输出

### 控制台报告
```
🎯 RAG检索性能指标:
----------------------------------------
  Precision@1: 0.3333 (±0.4714)
  Precision@3: 0.1111 (±0.1571)  
  Precision@5: 0.2000 (±0.1633)
  Recall@1: 0.3333 (±0.4714)
  Recall@3: 0.3333 (±0.4714)
  Recall@5: 0.6667 (±0.4714)
  nDCG@1: 0.3333 (±0.4714)
  nDCG@3: 0.3333 (±0.4714)
  nDCG@5: 0.5004 (±0.4082)
```

### 简化问答记录示例
```jsonl
{"question": "Who is the leader of Belgium?", "expected_answer": "Alexander De Croo", "rag_answer": "Philippe of Belgium", "llm_answer": "King Philippe"}
{"question": "What is the capital of Netherlands?", "expected_answer": "Amsterdam", "rag_answer": "Eberhard van der Laan", "llm_answer": "Amsterdam"}
```

## ⚙️ 配置选项

### 检索指标配置
可以在 `calculate_retrieval_metrics` 方法中修改：
- `k_values`: 要计算的k值列表，默认 [1, 3, 5]
- 相关性阈值: 默认 0.1，可根据需要调整

### 输出目录
默认输出到 `evaluation/` 目录，可通过参数修改：
```python
evaluator.save_evaluation_results(results, output_dir="custom_output")
```

## 🔍 故障排除

### 1. 检索指标全为0
- **原因**: 检索文档与期望答案相关性太低
- **解决**: 检查数据质量或调整相关性阈值

### 2. 简化记录文件为空
- **原因**: 评估过程中出现异常
- **解决**: 检查日志输出，确认评估正常完成

### 3. LLM调用失败
- **原因**: API密钥未设置或网络问题
- **解决**: 检查 `config.py` 中的 `OPENAI_API_KEY` 设置

## 📚 相关文件

- `rag_vs_llm_evaluation.py`: 主评估系统
- `test_enhanced_rag_vs_llm_evaluation.py`: 测试脚本
- `enhanced_retrieval_engine.py`: RAG检索引擎
- `config.py`: 配置文件

## 🎉 总结

新增的埋点功能让你能够：
1. **深入分析**: 了解RAG系统的检索性能
2. **便捷处理**: 获得简化的问答记录用于后续分析
3. **全面评估**: 从检索到生成的端到端性能评估

这些改进让评估系统更加完善，为RAG系统优化提供更多数据支持！