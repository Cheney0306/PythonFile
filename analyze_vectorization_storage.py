#!/usr/bin/env python3
# analyze_vectorization_storage.py - 分析向量化和存储过程

import json
from enhanced_embedding_system import EnhancedVectorDatabaseManager
from data_loader import KnowledgeDataLoader

def analyze_vectorization_process():
    """分析向量化过程"""
    print("🔍 分析增强系统的向量化和存储过程")
    print("=" * 60)
    
    # 创建增强数据库管理器
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_db.initialize_collection()
    
    # 获取一些示例数据
    loader = KnowledgeDataLoader()
    entries = loader.get_knowledge_entries()[:3]  # 只取前3个作为示例
    
    print("📊 向量化过程分析:")
    print("-" * 40)
    
    for i, entry in enumerate(entries, 1):
        print(f"\n示例 {i}:")
        print(f"原始条目: {entry['id']}")
        print(f"三元组: {entry['triple']}")
        print(f"Schema: {entry['schema']}")
        
        # 1. 生成增强文本 (这个会被向量化)
        enhanced_text = enhanced_db.enhanced_triple_to_text(entry['triple'], entry['schema'])
        print(f"\n🎯 被向量化的文本:")
        print(f"  '{enhanced_text}'")
        
        # 2. 生成元数据 (这个不会被向量化，只是存储)
        metadata = enhanced_db.create_enhanced_metadata(entry)
        print(f"\n📋 存储的元数据 (不被向量化):")
        for key, value in metadata.items():
            if key not in ['source_file', 'text']:  # 跳过长字段
                print(f"  {key}: {value}")

def analyze_chromadb_storage():
    """分析ChromaDB的存储结构"""
    print(f"\n🗄️ ChromaDB存储结构分析:")
    print("=" * 40)
    
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_db.initialize_collection()
    
    # 获取数据库中的一些记录
    try:
        results = enhanced_db.collection.get(limit=3, include=['embeddings', 'documents', 'metadatas'])
        
        if results and results['ids']:
            for i in range(len(results['ids'])):
                print(f"\n记录 {i+1}:")
                print(f"  ID: {results['ids'][i]}")
                
                # 文档 (被向量化的文本)
                if 'documents' in results and results['documents']:
                    doc = results['documents'][i]
                    print(f"  文档 (被向量化): {doc[:100]}...")
                
                # 嵌入向量
                if 'embeddings' in results and results['embeddings']:
                    embedding = results['embeddings'][i]
                    print(f"  嵌入向量维度: {len(embedding)}")
                    print(f"  嵌入向量示例: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
                
                # 元数据 (不被向量化，但存储用于检索后处理)
                if 'metadatas' in results and results['metadatas']:
                    metadata = results['metadatas'][i]
                    print(f"  元数据字段数: {len(metadata)}")
                    print(f"  元数据示例:")
                    for key, value in list(metadata.items())[:5]:  # 只显示前5个
                        print(f"    {key}: {value}")
        else:
            print("  ❌ 数据库为空或无法访问")
            
    except Exception as e:
        print(f"  ❌ 访问数据库时出错: {e}")

def explain_vectorization_vs_metadata():
    """解释向量化 vs 元数据存储的区别"""
    print(f"\n💡 向量化 vs 元数据存储的区别:")
    print("=" * 40)
    
    explanation = {
        "向量化的内容": {
            "是什么": "增强文本 (enhanced_triple_to_text的输出)",
            "目的": "用于语义相似度搜索",
            "处理": "通过嵌入模型转换为高维向量",
            "示例": "An instance of a 'Airport' named 'Brussels Airport' has a relation 'runwayLength' with an instance of a 'number' which is '3638'.",
            "存储位置": "ChromaDB的embeddings字段",
            "用途": "计算查询与文档的相似度"
        },
        "元数据存储": {
            "是什么": "结构化的附加信息 (create_enhanced_metadata的输出)",
            "目的": "提供检索后的详细信息和过滤条件",
            "处理": "直接存储，不进行向量化",
            "示例": "{'sub': 'Brussels_Airport', 'rel': 'runwayLength', 'obj': '3638', 'entities': 'Brussels Airport 3638', ...}",
            "存储位置": "ChromaDB的metadatas字段",
            "用途": "检索后的信息提取、过滤、重排序"
        }
    }
    
    for category, details in explanation.items():
        print(f"\n📋 {category}:")
        for key, value in details.items():
            print(f"  {key}: {value}")

def analyze_retrieval_process():
    """分析检索过程中如何使用向量和元数据"""
    print(f"\n🔍 检索过程中向量和元数据的使用:")
    print("=" * 40)
    
    process_steps = [
        {
            "步骤": "1. 查询向量化",
            "描述": "用户查询通过同样的嵌入模型转换为向量",
            "使用": "向量",
            "目的": "与数据库中的文档向量进行比较"
        },
        {
            "步骤": "2. 相似度计算",
            "描述": "计算查询向量与所有文档向量的余弦相似度",
            "使用": "向量",
            "目的": "找到最相似的文档"
        },
        {
            "步骤": "3. 初步检索",
            "描述": "根据相似度分数返回Top-K个最相似的文档",
            "使用": "向量 + 文档文本",
            "目的": "获得候选结果集"
        },
        {
            "步骤": "4. 元数据过滤",
            "描述": "使用元数据进行进一步的过滤和重排序",
            "使用": "元数据",
            "目的": "基于实体类型、关系类型等进行精细化筛选"
        },
        {
            "步骤": "5. 结果构造",
            "描述": "使用元数据构造最终的检索结果",
            "使用": "元数据",
            "目的": "提供结构化的三元组、类型等信息"
        }
    ]
    
    for step in process_steps:
        print(f"\n{step['步骤']}")
        print(f"  描述: {step['描述']}")
        print(f"  使用: {step['使用']}")
        print(f"  目的: {step['目的']}")

def demonstrate_with_example():
    """用具体例子演示向量化和元数据的作用"""
    print(f"\n🎯 具体例子演示:")
    print("=" * 40)
    
    # 模拟一个查询
    query = "Where is Brussels Airport located?"
    
    print(f"查询: '{query}'")
    
    # 模拟检索过程
    print(f"\n检索过程:")
    print(f"1. 查询向量化:")
    print(f"   '{query}' → [0.123, -0.456, 0.789, ...] (1024维向量)")
    
    print(f"\n2. 与数据库中的文档向量比较:")
    print(f"   文档1: 'An instance of a Airport named Brussels Airport has a relation location with an instance of a City which is Brussels.'")
    print(f"   向量1: [0.134, -0.445, 0.801, ...] → 相似度: 0.89")
    print(f"   ")
    print(f"   文档2: 'An instance of a Airport named Amsterdam Airport has a relation location with an instance of a City which is Amsterdam.'")
    print(f"   向量2: [0.098, -0.523, 0.712, ...] → 相似度: 0.72")
    
    print(f"\n3. 返回最相似的文档 + 元数据:")
    print(f"   选中文档1，同时返回其元数据:")
    print(f"   {{'sub': 'Brussels_Airport', 'rel': 'location', 'obj': 'Brussels', 'sub_type': 'Airport', 'obj_type': 'City'}}")
    
    print(f"\n4. 使用元数据构造最终答案:")
    print(f"   从元数据中提取: obj = 'Brussels'")
    print(f"   最终答案: 'Brussels'")

def main():
    """主函数"""
    print("🔍 增强系统向量化和存储分析")
    print("=" * 60)
    
    # 1. 分析向量化过程
    analyze_vectorization_process()
    
    # 2. 分析ChromaDB存储结构
    analyze_chromadb_storage()
    
    # 3. 解释向量化vs元数据的区别
    explain_vectorization_vs_metadata()
    
    # 4. 分析检索过程
    analyze_retrieval_process()
    
    # 5. 具体例子演示
    demonstrate_with_example()
    
    print(f"\n✅ 分析完成！")
    print(f"\n🎯 关键结论:")
    print(f"   ✅ 只有增强文本被向量化")
    print(f"   ✅ 元数据不被向量化，但会存储在数据库中")
    print(f"   ✅ 向量用于语义相似度搜索")
    print(f"   ✅ 元数据用于检索后的信息提取和过滤")
    print(f"   ✅ 两者配合实现高效的语义检索")

if __name__ == '__main__':
    main()