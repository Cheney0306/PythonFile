# 基于三元组的相关性判断修改总结

## 📋 修改概述

已成功将计算 Top-K 指标时的相关性判断逻辑从基于文本重叠改为**基于三元组匹配**的方法，提供更准确的相关性评估。

## 🎯 修改动机

在QA数据集中保存了生成每个问答对所用到的三元组，因此可以通过比较检索到的三元组与原始三元组的匹配程度来更准确地判断相关性。

## 🔧 具体修改

### 1. 修改文件: `rag_vs_llm_evaluation.py`

#### 修改 `calculate_retrieval_metrics` 方法
- **新增参数**: `original_triple: List[str] = None`
- **新增方法**: `_calculate_triple_relevance()` 和 `_calculate_text_relevance()`

#### 相关性判断逻辑
```python
def _calculate_triple_relevance(self, retrieved_triple: List[str], original_triple: List[str]) -> Tuple[float, int]:
    """
    基于三元组计算相关性分数
    - 3个元素完全匹配: 完全相关 (relevance=1.0, is_relevant=1)
    - 2个元素匹配: 部分相关 (relevance=0.6, is_relevant=1)  
    - 1个或0个元素匹配: 不相关 (relevance=0.0, is_relevant=0)
    """
```

#### 修改 `evaluate_single_question` 方法
- 从QA项目中提取 `original_triple` 信息
- 将原始三元组传递给 `calculate_retrieval_metrics`

### 2. 修改文件: `test_reranking_methods.py`

#### 修改方法签名
- `test_single_question()`: 新增 `original_triple` 参数
- `calculate_precision_at_k()`: 新增 `original_triple` 参数
- `calculate_recall_at_k()`: 新增 `original_triple` 参数
- `calculate_ndcg_at_k()`: 新增 `original_triple` 参数

#### 新增相关性判断方法
```python
def _calculate_triple_relevance_score(self, retrieved_triple: List[str], original_triple: List[str]) -> float:
    """
    基于三元组计算相关性分数
    - 3个元素完全匹配: 完全相关 (1.0)
    - 2个元素匹配: 部分相关 (0.6)  
    - 1个或0个元素匹配: 不相关 (0.0)
    """
```

#### 修改 `run_comparison` 方法
- 从QA项目中提取 `original_triple` 信息
- 将原始三元组传递给 `test_single_question`

## ✅ 验证结果

### 1. 三元组相关性计算测试
```
完全匹配分数: 1.0  # ['A', 'B', 'C'] vs ['A', 'B', 'C']
部分匹配分数: 0.6  # ['A', 'B', 'C'] vs ['A', 'B', 'D'] 
不匹配分数: 0.0    # ['A', 'B', 'C'] vs ['X', 'Y', 'Z']
```

### 2. 功能验证
- ✅ RAG vs LLM 评估器正常工作
- ✅ 重排方法对比器正常工作
- ✅ 基于三元组的相关性判断正常工作
- ✅ 回退到文本相关性判断正常工作

## 🎯 相关性判断逻辑

### 基于三元组的相关性判断 (优先)
1. **完全相关 (1.0)**: 检索到的三元组与原始三元组3个元素完全匹配
2. **部分相关 (0.6)**: 检索到的三元组与原始三元组2个元素匹配
3. **不相关 (0.0)**: 检索到的三元组与原始三元组1个或0个元素匹配

### 基于文本的相关性判断 (回退)
- 当没有原始三元组信息时，回退到基于文本重叠的相关性判断
- 保持与原有逻辑的兼容性

## 📊 影响范围

### 改进的指标计算
- **Precision@K**: 更准确地识别相关文档
- **Recall@K**: 更准确地计算召回率
- **nDCG@K**: 基于三元组匹配程度的分级相关性分数

### 保持兼容性
- ✅ 当没有原始三元组信息时，自动回退到文本相关性判断
- ✅ 所有现有的评估流程保持不变
- ✅ 输出格式保持不变

## 🚀 使用方法

### RAG vs LLM 评估
```python
from rag_vs_llm_evaluation import RAGvsLLMEvaluator

evaluator = RAGvsLLMEvaluator()

# QA项目需要包含 'triple' 字段
qa_item = {
    'question': 'Which airport has a runway named "7/25"?',
    'expected_answer': 'Alpena County Regional Airport',
    'triple': ['Alpena_County_Regional_Airport', 'runwayName', '7/25']
}

result = evaluator.evaluate_single_question(qa_item)
# 自动使用基于三元组的相关性判断
```

### 重排方法对比
```python
from test_reranking_methods import RerankingMethodComparator

comparator = RerankingMethodComparator()

# 加载包含三元组信息的QA数据集
questions = comparator.load_qa_questions(max_questions=100)

# 运行对比测试 (自动使用基于三元组的相关性判断)
results = comparator.run_comparison(questions)
```

## 📝 注意事项

1. **数据格式**: QA数据集需要包含 `triple` 字段才能使用基于三元组的相关性判断
2. **兼容性**: 没有三元组信息时会自动回退到文本相关性判断
3. **准确性**: 基于三元组的方法比基于文本重叠的方法更准确
4. **性能**: 三元组匹配计算速度很快，不会显著影响性能

## 🔄 回滚方法

如需回滚到原有的文本相关性判断，可以：
1. 在调用相关方法时不传递 `original_triple` 参数
2. 或者修改 `_calculate_triple_relevance` 方法直接返回文本相关性结果

## 📈 预期改进

- **更准确的评估**: 基于结构化三元组匹配比文本重叠更准确
- **更细粒度的相关性**: 支持完全相关(1.0)、部分相关(0.6)、不相关(0.0)三个级别
- **更好的排序质量**: nDCG@K 指标能更好地反映检索结果的排序质量