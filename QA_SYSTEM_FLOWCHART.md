# KG-RAG 问答系统流程图

## 完整问答系统架构流程

```mermaid
graph TD
    A[用户输入问题] --> B{问题预处理}
    B --> C[向量化问题]
    C --> D[向量数据库检索]
    
    D --> E[获取Top-K相关文档]
    E --> F{检索结果检查}
    F -->|有结果| G[CoTKR知识重写]
    F -->|无结果| H[返回无信息答案]
    
    G --> I{问题类型检测}
    I -->|Subject问题| J[主语重写策略]
    I -->|Object问题| K[宾语重写策略]
    I -->|Relation问题| L[关系重写策略]
    I -->|Type问题| M[类型重写策略]
    
    J --> N[生成思维链推理]
    K --> N
    L --> N
    M --> N
    
    N --> O[答案提取]
    O --> P[返回最终答案]
    H --> P
    
    P --> Q[用户获得答案]
    
    style A fill:#e1f5fe
    style P fill:#c8e6c9
    style Q fill:#c8e6c9
    style G fill:#fff3e0
    style N fill:#f3e5f5
```

## 详细组件流程

### 1. 数据准备阶段

```mermaid
graph LR
    A[XML数据集] --> B[数据加载器]
    B --> C[提取三元组]
    C --> D[提取Schema]
    D --> E[文本嵌入]
    E --> F[向量数据库存储]
    
    style A fill:#ffebee
    style F fill:#e8f5e8
```

### 2. 问答核心流程

```mermaid
flowchart TD
    Start([用户问题输入]) --> Input[问题: "Who is the leader of Belgium?"]
    
    Input --> Embed[SiliconFlow嵌入模型<br/>BAAI/bge-m3]
    Embed --> Vector[问题向量化]
    
    Vector --> Search[ChromaDB向量检索<br/>Top-5相似文档]
    Search --> Retrieved[检索结果:<br/>1. (Belgium, capital, Brussels)<br/>2. (Iraq, leader, Haider_al-Abadi)<br/>3. (Pakistan, leader, Anwar_Zaheer_Jamali)]
    
    Retrieved --> Detect[问题类型检测<br/>结果: Subject类型]
    
    Detect --> CoTKR[CoTKR知识重写]
    CoTKR --> Reasoning[思维链推理:<br/>Reason 1: 询问主语实体<br/>Knowledge 1: 检索到的知识<br/>Reason 2: 识别实体类型<br/>Knowledge 2: 实体类型信息<br/>Reason 3: 基于模式识别主语]
    
    Reasoning --> Extract[答案提取<br/>基于Subject类型返回主语]
    Extract --> Answer[最终答案: "Belgium"]
    
    Answer --> End([返回给用户])
    
    style Start fill:#e3f2fd
    style End fill:#e8f5e8
    style CoTKR fill:#fff3e0
    style Reasoning fill:#f3e5f5
    style Answer fill:#c8e6c9
```

### 3. CoTKR重写策略详解

```mermaid
graph TD
    A[检索到的三元组] --> B{问题类型}
    
    B -->|Subject| C[主语重写策略]
    B -->|Object| D[宾语重写策略]
    B -->|Relation| E[关系重写策略]
    B -->|Type| F[类型重写策略]
    
    C --> C1[Reason 1: 询问执行动作的主语]
    C1 --> C2[Knowledge 1: 三元组自然语言化]
    C2 --> C3[Reason 2: 识别主语实体类型]
    C3 --> C4[Knowledge 2: 主语类型信息]
    C4 --> C5[Reason 3: 基于模式识别主语]
    
    D --> D1[Reason 1: 询问接受动作的宾语]
    D1 --> D2[Knowledge 1: 三元组自然语言化]
    D2 --> D3[Reason 2: 识别宾语实体类型]
    D3 --> D4[Knowledge 2: 宾语类型信息]
    D4 --> D5[Reason 3: 基于模式识别宾语]
    
    E --> E1[Reason 1: 询问实体间关系]
    E1 --> E2[Knowledge 1: 三元组自然语言化]
    E2 --> E3[Reason 2: 考虑关系类型]
    E3 --> E4[Knowledge 2: 关系类型信息]
    E4 --> E5[Reason 3: 识别具体关系]
    
    F --> F1[Reason 1: 询问实体类型或类别]
    F1 --> F2[Knowledge 1: 三元组自然语言化]
    F2 --> F3[Knowledge 2: 实体类型映射]
    F3 --> F4[Reason 2: 识别被询问的实体类型]
    F4 --> F5[Reason 3: 确定请求的实体类型]
    
    C5 --> G[生成思维链推理文本]
    D5 --> G
    E5 --> G
    F5 --> G
    
    style A fill:#ffebee
    style G fill:#e8f5e8
    style C fill:#e3f2fd
    style D fill:#fff3e0
    style E fill:#f3e5f5
    style F fill:#e0f2f1
```

### 4. 答案提取流程

```mermaid
graph TD
    A[CoTKR重写知识] --> B[检索结果三元组]
    B --> C{问题类型}
    
    C -->|Subject| D[返回三元组主语<br/>sub.replace('_', ' ')]
    C -->|Object| E[返回三元组宾语<br/>obj.replace('_', ' ')]
    C -->|Relation| F[返回三元组关系<br/>rel.replace('_', ' ')]
    C -->|Type| G{实体匹配}
    
    G -->|匹配主语| H[返回主语类型<br/>sub_type]
    G -->|匹配宾语| I[返回宾语类型<br/>obj_type]
    G -->|默认| J[返回主语类型<br/>sub_type]
    
    D --> K[最终答案]
    E --> K
    F --> K
    H --> K
    I --> K
    J --> K
    
    style A fill:#ffebee
    style K fill:#c8e6c9
```

## 系统组件架构

```mermaid
graph TB
    subgraph "用户接口层"
        UI1[simple_qa.py<br/>简单问答接口]
        UI2[qa_system_demo.py<br/>演示系统]
        UI3[interactive_qa<br/>交互式问答]
    end
    
    subgraph "核心引擎层"
        RE[retrieval_engine.py<br/>检索引擎]
        CR[cotkr_rewriter.py<br/>CoTKR重写器]
    end
    
    subgraph "数据管理层"
        VDB[vector_database.py<br/>向量数据库管理]
        EC[embedding_client.py<br/>嵌入客户端]
        DL[data_loader.py<br/>数据加载器]
    end
    
    subgraph "外部服务"
        SF[SiliconFlow API<br/>嵌入服务]
        CD[ChromaDB<br/>向量数据库]
        DS[Dataset<br/>XML数据集]
    end
    
    UI1 --> RE
    UI2 --> RE
    UI3 --> RE
    
    RE --> CR
    RE --> VDB
    
    CR --> RE
    VDB --> EC
    VDB --> CD
    
    EC --> SF
    DL --> DS
    DL --> VDB
    
    style UI1 fill:#e3f2fd
    style UI2 fill:#e3f2fd
    style UI3 fill:#e3f2fd
    style RE fill:#fff3e0
    style CR fill:#f3e5f5
    style VDB fill:#e0f2f1
    style SF fill:#ffebee
    style CD fill:#ffebee
```

## 问题类型处理示例

### Subject类型问题
```
问题: "Who is the leader of Belgium?"
检索: (Belgium, capital, Brussels), (Iraq, leader, Haider_al-Abadi)
重写: 识别询问主语实体，基于关系模式确定主语
答案: "Belgium" (返回主语)
```

### Object类型问题
```
问题: "Where is Amsterdam Airport located?"
检索: (Amsterdam_Airport_Schiphol, location, Netherlands)
重写: 识别询问宾语实体，基于关系确定位置
答案: "Netherlands" (返回宾语)
```

### Relation类型问题
```
问题: "What is the relationship between Amsterdam Airport and Netherlands?"
检索: (Amsterdam_Airport_Schiphol, location, Netherlands)
重写: 识别询问实体间关系
答案: "location" (返回关系)
```

### Type类型问题
```
问题: "What type of entity is Belgium?"
检索: (Belgium, capital, Brussels)
重写: 识别询问实体类型，匹配实体确定类型
答案: "Country" (返回实体类型)
```

## 性能指标

```mermaid
graph LR
    A[输入问题] --> B[响应时间<br/>~2-3秒]
    B --> C[检索准确率<br/>基于向量相似度]
    C --> D[答案准确率<br/>基于CoTKR重写质量]
    D --> E[系统吞吐量<br/>支持并发查询]
    
    style A fill:#e3f2fd
    style E fill:#c8e6c9
```

## 配置参数

| 参数 | 值 | 说明 |
|------|----|----|
| 嵌入模型 | BAAI/bge-m3 | SiliconFlow提供 |
| 检索数量 | Top-5 | 默认检索5个相关文档 |
| 向量数据库 | ChromaDB | 本地向量存储 |
| 问题类型 | 4种 | sub, obj, rel, type |
| 重写策略 | CoTKR | 思维链知识重写 |

这个问答系统通过完整的RAG流程，能够准确理解用户问题，检索相关知识，并通过CoTKR方法生成高质量的答案。