# 选择性QA生成功能指南

## 🎯 功能概述

针对你发现的"类型问题效果很差"的问题，我们为增强QA生成器添加了**选择性问题类型生成**功能，让你可以：

- ✅ 排除效果差的类型问题
- ✅ 只生成特定类型的问题
- ✅ 灵活组合不同的问题类型
- ✅ 自动生成包含类型信息的文件名

---

## 📋 问题类型说明

| 类型 | 代码 | 说明 | 示例问题 | 推荐程度 |
|------|------|------|----------|----------|
| 主语问题 | `sub` | 询问执行动作的主体 | "Who is the leader of Belgium?" | ⭐⭐⭐⭐⭐ |
| 宾语问题 | `obj` | 询问动作的对象或位置 | "Where is Amsterdam Airport located?" | ⭐⭐⭐⭐⭐ |
| 关系问题 | `rel` | 询问实体间的关系 | "What is the relationship between Belgium and Brussels?" | ⭐⭐⭐⭐ |
| 类型问题 | `type` | 询问实体的类型 | "What type of entity is Belgium?" | ⭐⭐ (效果差) |

---

## 🚀 使用方法

### 1. 排除类型问题 (推荐)

```bash
# 测试模式，排除类型问题
python generate_enhanced_qa.py --exclude-type --test-mode --show-samples

# 处理100个文本，排除类型问题
python generate_enhanced_qa.py --exclude-type --max-texts 100

# 全量处理，排除类型问题
python generate_enhanced_qa.py --exclude-type
```

### 2. 只生成基础问题类型

```bash
# 只生成 sub, obj, rel 三种类型
python generate_enhanced_qa.py --only-basic --test-mode

# 等价于 --exclude-type
python generate_enhanced_qa.py --only-basic --max-texts 50
```

### 3. 自定义问题类型组合

```bash
# 只生成主语问题
python generate_enhanced_qa.py --question-types sub --test-mode

# 只生成主语和宾语问题
python generate_enhanced_qa.py --question-types sub obj --max-texts 100

# 只生成关系问题
python generate_enhanced_qa.py --question-types rel --show-samples
```

### 4. 指定输出文件名

```bash
# 自定义文件名
python generate_enhanced_qa.py --exclude-type --output-file high_quality_qa.json

# 系统会自动生成包含类型信息的文件名
python generate_enhanced_qa.py --exclude-type --test-mode
# 输出: enhanced_qa_dataset_test_no_type.json
```

---

## 📁 输出文件命名规则

系统会根据你的配置自动生成文件名：

| 配置 | 文件名示例 |
|------|------------|
| 测试模式 + 排除类型 | `enhanced_qa_dataset_test_no_type.json` |
| 100个文本 + 只要sub,obj | `enhanced_qa_dataset_100_texts_sub_obj.json` |
| 全量 + 排除类型 | `enhanced_qa_dataset_all_texts_no_type.json` |
| 全量 + 所有类型 | `enhanced_qa_dataset_all_texts.json` |

---

## 🎯 推荐配置

### 高质量QA生成 (推荐)
```bash
python generate_enhanced_qa.py --exclude-type --max-texts 200 --show-samples
```

**优势:**
- 排除效果差的类型问题
- 专注于高质量的sub/obj/rel问题
- 提高整体QA数据集质量

### 特定用途生成

```bash
# 只要主语问题 (Who问题)
python generate_enhanced_qa.py --question-types sub --max-texts 100

# 只要位置问题 (Where问题)  
python generate_enhanced_qa.py --question-types obj --max-texts 100

# 只要关系问题
python generate_enhanced_qa.py --question-types rel --max-texts 100
```

---

## 📊 质量对比

### 修改前 (包含所有类型)
```
总QA对: 1000
- sub问题: 250 (质量: ⭐⭐⭐⭐⭐)
- obj问题: 250 (质量: ⭐⭐⭐⭐⭐)  
- rel问题: 250 (质量: ⭐⭐⭐⭐)
- type问题: 250 (质量: ⭐⭐) ← 拖累整体质量
```

### 修改后 (排除类型问题)
```
总QA对: 750
- sub问题: 250 (质量: ⭐⭐⭐⭐⭐)
- obj问题: 250 (质量: ⭐⭐⭐⭐⭐)
- rel问题: 250 (质量: ⭐⭐⭐⭐)
整体质量显著提升! 🎉
```

---

## 🔧 技术实现

### 核心修改

1. **EnhancedQAGenerator 构造函数**
   ```python
   def __init__(self, enabled_question_types: List[str] = None):
       # 支持自定义问题类型
   ```

2. **命令行参数扩展**
   ```python
   parser.add_argument('--question-types', nargs='+', choices=['sub', 'obj', 'rel', 'type'])
   parser.add_argument('--exclude-type', action='store_true')
   parser.add_argument('--only-basic', action='store_true')
   ```

3. **智能文件命名**
   - 自动在文件名中包含类型信息
   - 便于区分不同配置的输出

### 向后兼容

- 不传参数时，行为与原来完全一致
- 所有现有脚本无需修改
- 新功能完全可选

---

## 💡 使用建议

### 1. 首次使用
```bash
# 先用测试模式验证效果
python generate_enhanced_qa.py --exclude-type --test-mode --show-samples
```

### 2. 生产使用
```bash
# 生成高质量数据集
python generate_enhanced_qa.py --exclude-type --max-texts 500
```

### 3. 特定需求
```bash
# 如果只需要Who类型的问题
python generate_enhanced_qa.py --question-types sub --max-texts 200

# 如果只需要Where类型的问题  
python generate_enhanced_qa.py --question-types obj --max-texts 200
```

---

## 🎉 预期效果

通过排除类型问题，你应该能看到：

1. **QA质量提升**: 去除效果差的类型问题
2. **答案准确性提高**: 专注于系统擅长的问题类型
3. **评估分数改善**: 在RAG vs LLM评估中表现更好
4. **生成效率提升**: 减少无效的QA对生成

---

## 📞 故障排除

### 问题: 无效的问题类型
```
⚠ 警告: 无效的问题类型 ['invalid']，将被忽略
```
**解决**: 只使用 `sub`, `obj`, `rel`, `type` 四种类型

### 问题: 没有有效的问题类型
```
❌ 错误: 没有有效的问题类型，使用默认配置
```
**解决**: 至少指定一个有效的问题类型

### 问题: API密钥未设置
```
⚠ 警告: OpenAI API密钥未设置，将无法生成QA对
```
**解决**: 设置环境变量 `OPENAI_API_KEY`

---

这个功能应该能显著改善你的QA数据集质量！建议从 `--exclude-type` 开始使用。