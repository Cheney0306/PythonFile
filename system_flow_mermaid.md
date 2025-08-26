# 新KG-RAG系统流程图 (Mermaid)

## 完整系统架构流程图

```mermaid
graph TB
    subgraph "数据层 (Data Layer)"
        A[XML知识文件<br/>data_loader.py] --> B[知识条目解析<br/>Triple + Schema + Text]
    end
    
    subgraph "存储层 (Storage Layer)"
        B --> C[嵌入向量化<br/>embedding_client.py<br/>SiliconFlow API]
        C --> D[向量数据库<br/>vector_database.py<br/>ChromaDB]
    end
    
    subgraph "检索层 (Retrieval Layer)"
        E[用户问题<br/>User Question] --> F[检索引擎<br/>retrieval_engine.py]
        F --> G[向量相似度检索<br/>Vector Similarity Search]
        D --> G
        G --> H[Top-K 三元组<br/>Retrieved Triples]
    end
    
    subgraph "CoTKR重写层 (CoTKR Rewriting Layer)"
        H --> I[CoTKR重写器<br/>cotkr_rewriter.py]
        I --> J[问题类型检测<br/>Question Type Detection]
        J --> K[思维链推理生成<br/>Chain-of-Thought Reasoning]
        K --> L[知识重写<br/>Knowledge Rewriting]
        L --> M[答案提取<br/>Answer Extraction]
    end
    
    subgraph "评估层 (Evaluation Layer)"
        N[QA生成器<br/>qa_generator.py] --> O[QA数据集<br/>Question-Answer Pairs]
        O --> P[评估引擎<br/>evaluation_engine.py]
        P --> Q[性能指标<br/>Precision@K, Recall@K, nDCG@K]
    end
    
    subgraph "应用层 (Application Layer)"
        R[主系统<br/>main_system.py] --> F
        R --> N
        R --> P
        S[交互式查询<br/>Interactive Mode] --> R
        T[批量查询<br/>Batch Mode] --> R
        U[性能评估<br/>Evaluation Mode] --> R
    end
    
    M --> V[最终答案<br/>Final Answer]
    
    style I fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style F fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style D fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style R fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

## 核心组件交互图

```mermaid
graph LR
    subgraph "核心处理流程"
        A[用户问题] --> B[RetrievalEngine<br/>检索引擎]
        B --> C[VectorDatabase<br/>向量检索]
        C --> D[CoTKRRewriter<br/>知识重写]
        D --> E[最终答案]
    end
    
    subgraph "支持组件"
        F[DataLoader<br/>数据加载] --> C
        G[EmbeddingClient<br/>向量化] --> C
        H[QAGenerator<br/>QA生成] --> I[EvaluationEngine<br/>评估引擎]
        I --> B
    end
    
    subgraph "系统管理"
        J[MainSystem<br/>主系统] --> B
        J --> H
        J --> I
        K[Config<br/>配置管理] --> J
    end
    
    style D fill:#ffeb3b,stroke:#f57f17,stroke-width:3px
    style B fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
```

## CoTKR重写流程详图

```mermaid
graph TD
    A[检索到的三元组] --> B[CoTKRRewriter]
    C[用户问题] --> B
    
    B --> D{问题类型检测}
    
    D -->|who| E[Who类型处理<br/>识别人物关系]
    D -->|where| F[Where类型处理<br/>查找位置信息]
    D -->|what| G[What类型处理<br/>分析询问内容]
    D -->|when| H[When类型处理<br/>查找时间信息]
    D -->|how_many| I[Count类型处理<br/>统计计数]
    D -->|general| J[通用处理<br/>综合分析]
    
    E --> K[生成思维链推理]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[重写知识<br/>Reason 1: ...<br/>Knowledge 1: ...<br/>Reason 2: ...]
    
    L --> M[答案提取<br/>基于重写知识提取答案]
    
    M --> N[最终答案]
    
    style B fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style K fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style L fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

## 系统运行模式图

```mermaid
graph TB
    A[main_system.py] --> B{运行模式选择}
    
    B -->|setup| C[数据库设置模式<br/>初始化向量数据库<br/>加载知识数据]
    B -->|interactive| D[交互式查询模式<br/>实时问答对话]
    B -->|batch| E[批量查询模式<br/>处理多个问题]
    B -->|evaluate| F[评估模式<br/>生成QA数据集<br/>计算性能指标]
    B -->|info| G[信息模式<br/>显示系统状态]
    
    C --> H[VectorDatabase<br/>ChromaDB管理]
    D --> I[RetrievalEngine<br/>实时检索重写]
    E --> I
    F --> J[QAGenerator + EvaluationEngine<br/>性能评估]
    G --> K[系统状态信息]
    
    style A fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style I fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    style J fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```

## 数据流向图

```mermaid
flowchart LR
    subgraph "输入数据"
        A[XML文件] --> B[三元组数据<br/>(sub, rel, obj)]
        A --> C[Schema数据<br/>(sub_type, rel_type, obj_type)]
        A --> D[文本数据<br/>Text Content]
    end
    
    subgraph "向量化处理"
        B --> E[文本表示<br/>sub rel obj. Types: sub_type rel_type obj_type]
        C --> E
        E --> F[SiliconFlow API<br/>BAAI/bge-m3]
        F --> G[向量嵌入<br/>Embeddings]
    end
    
    subgraph "存储检索"
        G --> H[ChromaDB<br/>向量数据库]
        I[用户问题] --> J[问题向量化]
        J --> K[相似度检索]
        H --> K
        K --> L[Top-K结果]
    end
    
    subgraph "知识重写"
        L --> M[CoTKR处理]
        I --> M
        M --> N[思维链推理]
        N --> O[重写知识]
        O --> P[答案提取]
    end
    
    P --> Q[最终答案]
    
    style F fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    style M fill:#e1f5fe,stroke:#0277bd,stroke-width:3px
    style H fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

## 评估流程图

```mermaid
graph TD
    A[知识条目] --> B[QAGenerator<br/>问答对生成]
    B --> C[QA数据集<br/>Questions + Ground Truth]
    
    C --> D[EvaluationEngine<br/>批量查询]
    D --> E[RetrievalEngine<br/>系统响应]
    E --> F[结果收集]
    
    F --> G[计算Precision@K]
    F --> H[计算Recall@K]
    F --> I[计算nDCG@K]
    
    G --> J[评估报告]
    H --> J
    I --> J
    
    J --> K[按问题类型分组统计]
    J --> L[整体性能指标]
    
    style D fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style E fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    style J fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

## 文件依赖关系图

```mermaid
graph TB
    A[config.py<br/>配置文件] --> B[main_system.py<br/>主系统]
    A --> C[embedding_client.py<br/>嵌入客户端]
    A --> D[vector_database.py<br/>向量数据库]
    A --> E[qa_generator.py<br/>QA生成器]
    
    F[data_loader.py<br/>数据加载器] --> D
    C --> D
    
    G[cotkr_rewriter.py<br/>CoTKR重写器] --> H[retrieval_engine.py<br/>检索引擎]
    D --> H
    
    E --> I[evaluation_engine.py<br/>评估引擎]
    H --> I
    
    B --> H
    B --> E
    B --> I
    B --> D
    
    J[test_new_system.py<br/>系统测试] --> B
    K[quick_demo.py<br/>快速演示] --> B
    L[visualize_system_flow.py<br/>可视化工具] --> B
    
    style A fill:#ffecb3,stroke:#ff8f00,stroke-width:2px
    style B fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style G fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style H fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```