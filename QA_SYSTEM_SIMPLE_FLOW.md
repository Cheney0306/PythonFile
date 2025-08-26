# KG-RAG 问答系统简化流程图

## 🎯 核心问答流程

```
用户问题输入
    ↓
问题向量化 (BAAI/bge-m3)
    ↓
向量数据库检索 (ChromaDB Top-5)
    ↓
获取相关三元组和Schema
    ↓
问题类型检测/指定
    ↓
┌─────────────────────────────────────┐
│            CoTKR 重写策略            │
├─────────┬─────────┬─────────┬───────┤
│ Subject │ Object  │Relation │ Type  │
│  重写   │  重写   │  重写   │ 重写  │
└─────────┴─────────┴─────────┴───────┘
    ↓
生成思维链推理文本
    ↓
基于问题类型提取答案
    ↓
返回最终答案给用户
```

## 🔍 详细执行示例

### 示例1: Subject类型问题
```
输入: "Who is the leader of Belgium?"
  ↓
向量化: [0.1, 0.3, -0.2, ...] (768维向量)
  ↓
检索结果:
  1. (Belgium, capital, Brussels) - 相似度: 0.59
  2. (Iraq, leader, Haider_al-Abadi) - 相似度: 0.45
  3. (Pakistan, leader, Anwar_Zaheer_Jamali) - 相似度: 0.43
  ↓
问题类型: Subject (询问主语)
  ↓
CoTKR重写:
  Reason 1: 询问执行动作的主语实体
  Knowledge 1: Belgium has capital Brussels. Iraq is led by Haider al-Abadi...
  Reason 2: 识别主语实体类型 (Country, GovernmentAgency)
  Reason 3: 基于问题模式识别主语
  ↓
答案提取: 返回三元组主语 → "Belgium"
```

### 示例2: Object类型问题
```
输入: "Where is Amsterdam Airport located?"
  ↓
检索结果: (Amsterdam_Airport_Schiphol, location, Netherlands)
  ↓
问题类型: Object (询问宾语)
  ↓
CoTKR重写: 识别询问位置信息的宾语实体
  ↓
答案提取: 返回三元组宾语 → "Netherlands"
```

## 🏗️ 系统组件层次

```
┌─────────────────────────────────────────────────────────┐
│                    用户接口层                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
│  │ simple_qa   │ │qa_system_   │ │ interactive_qa  │    │
│  │    .py      │ │  demo.py    │ │                 │    │
│  └─────────────┘ └─────────────┘ └─────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   核心引擎层                             │
│  ┌─────────────────────┐ ┌─────────────────────────┐    │
│  │ retrieval_engine.py │ │  cotkr_rewriter.py      │    │
│  │   (检索引擎)        │ │   (CoTKR重写器)         │    │
│  └─────────────────────┘ └─────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据管理层                             │
│ ┌─────────────┐┌─────────────┐┌─────────────────────┐   │
│ │vector_      ││embedding_   ││   data_loader.py    │   │
│ │database.py  ││client.py    ││                     │   │
│ └─────────────┘└─────────────┘└─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   外部服务层                             │
│ ┌─────────────┐┌─────────────┐┌─────────────────────┐   │
│ │SiliconFlow  ││  ChromaDB   ││   XML Dataset       │   │
│ │    API      ││             ││                     │   │
│ └─────────────┘└─────────────┘└─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🔄 四种问题类型处理流程

### 1. Subject类型 (sub)
```
问题特征: "Who...", "What... wrote/created/founded..."
处理策略: 
  → 识别询问主语实体
  → 分析主语与其他实体的关系
  → 返回三元组的主语部分
示例: "Who wrote this book?" → 返回作者名
```

### 2. Object类型 (obj)  
```
问题特征: "Where...", "What did...", "What country..."
处理策略:
  → 识别询问宾语实体
  → 分析主语的属性或关系对象
  → 返回三元组的宾语部分
示例: "Where is the airport?" → 返回位置
```

### 3. Relation类型 (rel)
```
问题特征: "What is the relationship...", "How are... connected"
处理策略:
  → 识别询问实体间关系
  → 分析连接两个实体的关系类型
  → 返回三元组的关系部分
示例: "What connects A and B?" → 返回关系类型
```

### 4. Type类型 (type)
```
问题特征: "What type of entity...", "What kind of..."
处理策略:
  → 识别询问实体类型
  → 基于Schema信息确定实体类别
  → 返回实体的类型信息
示例: "What type is Belgium?" → 返回"Country"
```

## ⚡ 性能特点

| 特性 | 描述 |
|------|------|
| **响应速度** | 2-3秒 (包含向量检索+CoTKR重写) |
| **准确率** | 基于向量相似度和CoTKR推理质量 |
| **并发支持** | 支持多用户同时查询 |
| **扩展性** | 可轻松添加新的问题类型 |
| **数据源** | 支持XML格式的知识图谱数据 |

## 🛠️ 配置参数

```python
# 核心配置
EMBEDDING_MODEL = "BAAI/bge-m3"        # 嵌入模型
RETRIEVAL_TOP_K = 5                    # 检索数量
QUESTION_TYPES = ['sub', 'obj', 'rel', 'type']  # 问题类型
VECTOR_DB = "ChromaDB"                 # 向量数据库
REWRITE_METHOD = "CoTKR"               # 重写方法

# API配置
SILICONFLOW_API_KEY = "your-key"       # SiliconFlow API密钥
OPENAI_API_KEY = "your-key"            # OpenAI API密钥 (可选)
```

## 🎯 使用方式

### 1. 简单问答
```bash
python simple_qa.py
# 输入问题，获得答案
```

### 2. 演示模式
```bash
python qa_system_demo.py
# 查看完整演示流程
```

### 3. 快速测试
```bash
python qa_system_demo.py quick
# 快速测试几个问题
```

### 4. 编程接口
```python
from retrieval_engine import RetrievalEngine

engine = RetrievalEngine()
result = engine.retrieve_and_rewrite("Who is the leader of Belgium?")
print(result['final_answer'])
```

## 📊 系统优势

1. **智能问题理解**: 自动检测四种问题类型
2. **精确知识检索**: 基于向量相似度的精准检索
3. **思维链推理**: CoTKR方法提供可解释的推理过程
4. **灵活扩展**: 模块化设计，易于添加新功能
5. **高效处理**: 优化的向量检索和缓存机制

这个问答系统通过完整的RAG流程，能够理解用户问题，检索相关知识，并生成准确、可解释的答案。