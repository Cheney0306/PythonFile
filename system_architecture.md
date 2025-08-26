# 新KG-RAG系统架构文档

## 系统概述

新的知识图谱RAG系统集成了CoTKR（Chain-of-Thought Knowledge Rewriting）技术，实现了更智能的知识检索和重写功能。与原系统相比，新系统移除了预处理阶段的查询重写，直接使用原始问题进行向量检索，然后在后处理阶段使用CoTKR方法重写检索到的知识。

## 系统架构图

```mermaid
graph TB
    subgraph "数据层"
        A[XML知识文件] --> B[KnowledgeDataLoader]
        B --> C[知识条目<br/>Triple + Schema + Text]
    end
    
    subgraph "存储层"
        C --> D[EmbeddingClient<br/>SiliconFlow API]
        D --> E[向量嵌入]
        E --> F[ChromaDB<br/>向量数据库]
    end
    
    subgraph "检索层"
        G[用户问题] --> H[RetrievalEngine]
        H --> I[向量相似度检索]
        F --> I
        I --> J[检索结果<br/>Top-K 三元组]
    end
    
    subgraph "重写层"
        J --> K[CoTKRRewriter]
        K --> L[问题类型检测]
        L --> M[思维链推理生成]
        M --> N[重写知识]
        N --> O[答案提取]
    end
    
    subgraph "评估层"
        P[QAGenerator] --> Q[QA数据集]
        Q --> R[EvaluationEngine]
        R --> S[Precision@K<br/>Recall@K<br/>nDCG@K]
    end
    
    subgraph "应用层"
        T[MainSystem] --> H
        T --> P
        T --> R
        U[交互式查询] --> T
        V[批量查询] --> T
        W[性能评估] --> T
    end
    
    style K fill:#e1f5fe
    style H fill:#f3e5f5
    style F fill:#e8f5e8
    style T fill:#fff3e0
```

## 核心组件详解

### 1. 数据加载层 (data_loader.py)
- **功能**: 解析XML格式的知识文件，提取三元组、Schema和文本信息
- **输入**: XML知识文件
- **输出**: 结构化的知识条目列表
- **特点**: 支持批量处理，包含错误处理机制

### 2. 嵌入客户端 (embedding_client.py)
- **功能**: 调用SiliconFlow API获取文本的向量表示
- **模型**: BAAI/bge-m3
- **特点**: 
  - 支持批量处理
  - 包含重试机制
  - 自动日志记录
  - 智能错误处理

### 3. 向量数据库 (vector_database.py)
- **功能**: 管理向量存储和检索
- **技术**: ChromaDB持久化存储
- **特点**:
  - 余弦相似度检索
  - 元数据存储（三元组、Schema信息）
  - 批量插入优化

### 4. CoTKR重写器 (cotkr_rewriter.py)
- **功能**: 基于思维链的知识重写
- **核心特性**:
  - 问题类型自动检测 (who/what/where/when/how_many/general)
  - 针对不同问题类型的专门重写策略
  - 思维链推理生成
  - 智能答案提取

### 5. 检索引擎 (retrieval_engine.py)
- **功能**: 系统的核心检索组件
- **流程**:
  1. 接收原始问题
  2. 向量相似度检索
  3. CoTKR知识重写
  4. 答案提取
- **输出**: 包含检索结果、重写知识和最终答案的完整响应

### 6. QA生成器 (qa_generator.py)
- **功能**: 基于知识条目生成问答对
- **支持模式**:
  - OpenAI API生成（需要API密钥）
  - 模板生成（备选方案）
- **输出**: JSON格式的QA数据集

### 7. 评估引擎 (evaluation_engine.py)
- **功能**: 系统性能评估
- **评估指标**:
  - Precision@K
  - Recall@K
  - nDCG@K
- **特点**: 支持按问题类型分组评估

### 8. 主系统 (main_system.py)
- **功能**: 系统入口和协调器
- **运行模式**:
  - 交互式查询
  - 批量查询
  - 性能评估
  - 数据库设置

### 9. 配置文件 (config.py)
- **功能**: 集中管理系统配置
- **包含**: API密钥、数据路径、模型参数等

## 系统工作流程

### 1. 初始化流程
```
1. 加载配置 (config.py)
2. 初始化各组件
3. 设置向量数据库
4. 加载知识数据 (如果数据库为空)
5. 向量化并存储知识条目
```

### 2. 查询流程
```
用户问题 → 向量检索 → CoTKR重写 → 答案提取 → 返回结果
```

### 3. 评估流程
```
生成QA数据集 → 批量查询 → 计算评估指标 → 生成报告
```

## 与原系统的主要区别

| 方面 | 原系统 | 新系统 |
|------|--------|--------|
| 查询重写 | 预处理阶段重写查询 | 后处理阶段重写知识 |
| 重写方法 | 简单的查询扩展 | CoTKR思维链推理 |
| 问题类型 | 通用处理 | 针对性处理策略 |
| 知识表示 | 复杂的文本拼接 | 简洁的三元组表示 |
| 推理能力 | 基础检索 | 思维链推理 |

## 性能优势

1. **更准确的答案**: CoTKR方法提供结构化的推理过程
2. **更好的可解释性**: 思维链展示推理步骤
3. **类型化处理**: 针对不同问题类型优化
4. **简化的向量化**: 避免复杂的预处理重写
5. **更强的泛化能力**: 适应各种问题类型

## 使用示例

### 交互式使用
```bash
python main_system.py --mode interactive
```

### 批量查询
```bash
python main_system.py --mode batch --questions "Who is the leader of Belgium?" "Where is Amsterdam Airport?"
```

### 性能评估
```bash
python main_system.py --mode evaluate --max-qa 100
```

### 数据库重置
```bash
python main_system.py --mode setup --reset-db
```

## 扩展性

系统设计具有良好的模块化结构，支持：
- 新的嵌入模型集成
- 不同的向量数据库后端
- 自定义的重写策略
- 新的评估指标
- 多语言支持

## 依赖项

- chromadb: 向量数据库
- requests: HTTP客户端
- numpy: 数值计算
- tqdm: 进度条
- openai: QA生成（可选）
- pathlib: 路径处理