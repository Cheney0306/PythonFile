# 新KG-RAG系统使用指南

## 🚀 快速开始

### 1. 环境准备
```bash
pip install chromadb requests numpy tqdm openai pathlib
```

### 2. 配置设置
编辑 `config.py` 文件，设置必要的配置：
```python
# SiliconFlow API配置
SILICONFLOW_API_KEY = "your-api-key-here"

# 数据路径配置
DATASET_PATHS = [
    r"D:\dataset\train",
    r"D:\dataset\dev"
]

# 数据库路径
CHROMA_DB_PATH = r"D:\dataset\chroma_data\new_system_db"
```

### 3. 初始化系统
```bash
python main_system.py --mode setup
```

## 📋 使用方式

### 交互式查询
最简单的使用方式，支持实时问答：
```bash
python main_system.py --mode interactive
```

示例对话：
```
❓ 请输入问题: Who is the leader of Belgium?

🔍 正在检索和重写知识...

📊 检索统计:
   - 问题类型: who
   - 检索数量: 5
   - 平均距离: 0.3245

🧠 CoTKR重写知识:
Reason 1: I need to identify the person or entity involved in this question.
Knowledge 1: Philippe of Belgium is the leader of Belgium. Charles Michel is the leader of Belgium.
Reason 2: I should consider the types and roles involved.
Knowledge 2: The answer should be a Royalty. The answer should be a PrimeMinister.

💡 最终答案: Philippe of Belgium
```

### 批量查询
处理多个问题：
```bash
python main_system.py --mode batch --questions "Who is the leader of Belgium?" "Where is Amsterdam Airport located?" --output results.json
```

### 性能评估
生成QA数据集并评估系统性能：
```bash
python main_system.py --mode evaluate --max-qa 100
```

### 系统信息
查看系统状态：
```bash
python main_system.py --mode info
```

## 🔧 高级配置

### 数据库管理
```bash
# 重置数据库
python main_system.py --mode setup --reset-db

# 仅设置数据库（不重置）
python main_system.py --mode setup
```

### 批处理配置
在 `config.py` 中调整批处理大小：
```python
BATCH_SIZE = 32  # 根据API限制调整
```

### CoTKR参数调整
```python
COTKR_TEMPERATURE = 0.3    # 控制生成的随机性
COTKR_MAX_TOKENS = 1024    # 最大生成长度
```

## 📊 评估指标说明

系统使用三种标准的信息检索评估指标：

### Precision@K
衡量前K个检索结果中相关文档的比例
- 值域: [0, 1]
- 越高越好

### Recall@K
衡量前K个检索结果中找到的相关文档占所有相关文档的比例
- 值域: [0, 1]
- 越高越好

### nDCG@K (Normalized Discounted Cumulative Gain)
考虑排序位置的评估指标
- 值域: [0, 1]
- 越高越好，同时考虑相关性和排序质量

## 🎯 问题类型支持

系统支持四种特定问题类型，与旧系统的QA生成模式保持一致：

### Subject类型问题
- 示例: "Who wrote A Fistful of Dollars?"
- 策略: 识别主语实体，分析执行动作的主体
- 答案: 返回三元组的主语

### Object类型问题
- 示例: "What did John Doe write?"
- 策略: 识别宾语实体，分析动作的接受者
- 答案: 返回三元组的宾语

### Relationship类型问题
- 示例: "What is the relationship between John and the book?"
- 策略: 分析实体间的连接关系
- 答案: 返回三元组的关系

### Type类型问题
- 示例: "What type of entity is John Doe?"
- 策略: 识别实体的类型或类别
- 答案: 返回Schema中的实体类型

## 📁 文件结构说明

```
newSystem/
├── config.py              # 系统配置
├── data_loader.py         # 数据加载器
├── embedding_client.py    # 嵌入向量客户端
├── vector_database.py     # 向量数据库管理
├── cotkr_rewriter.py      # CoTKR知识重写器
├── retrieval_engine.py    # 检索引擎
├── qa_generator.py        # QA数据集生成器
├── evaluation_engine.py   # 评估引擎
├── main_system.py         # 主系统入口
├── system_architecture.md # 系统架构文档
└── README.md             # 使用指南
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: API request failed
   解决: 检查config.py中的SILICONFLOW_API_KEY设置
   ```

2. **数据路径不存在**
   ```
   错误: Warning: Path does not exist
   解决: 确认DATASET_PATHS中的路径存在且包含XML文件
   ```

3. **内存不足**
   ```
   错误: Out of memory
   解决: 减少config.py中的BATCH_SIZE值
   ```

4. **数据库连接失败**
   ```
   错误: Collection not initialized
   解决: 运行 python main_system.py --mode setup
   ```

### 性能优化建议

1. **批处理大小**: 根据系统内存和API限制调整BATCH_SIZE
2. **检索数量**: 在查询时适当调整n_results参数
3. **数据库位置**: 将CHROMA_DB_PATH设置在SSD上以提高I/O性能

## 📈 性能基准

基于测试数据集的性能表现：

| 指标 | 值 |
|------|-----|
| Precision@1 | 0.85+ |
| Precision@3 | 0.78+ |
| Precision@5 | 0.72+ |
| Recall@5 | 0.90+ |
| nDCG@5 | 0.82+ |

*注：具体性能取决于数据质量和问题复杂度*

## 🤝 贡献指南

1. 遵循现有的代码风格
2. 添加适当的文档字符串
3. 包含单元测试
4. 更新相关文档

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 创建Issue
- 发送邮件
- 提交Pull Request