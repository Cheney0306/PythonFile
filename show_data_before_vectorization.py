#!/usr/bin/env python3
# show_data_before_vectorization.py - 展示增强系统数据在向量化前的格式

import json
from pathlib import Path
from data_loader import KnowledgeDataLoader
from enhanced_embedding_system import EnhancedVectorDatabaseManager

def show_original_xml_structure():
    """展示原始XML文件的结构"""
    print("📄 原始XML文件结构示例")
    print("=" * 50)
    
    xml_example = '''
<root>
    <entry id="1_Airport_0">
        <triples>
            <triple>
                <sub>Amsterdam_Airport_Schiphol</sub>
                <rel>location</rel>
                <obj>Haarlemmermeer</obj>
            </triple>
        </triples>
        <schemas>
            <schema>
                <sub>Airport</sub>
                <rel>location</rel>
                <obj>City</obj>
            </schema>
        </schemas>
        <text>
            Amsterdam Airport Schiphol is located in Haarlemmermeer. 
            It is one of the busiest airports in Europe.
        </text>
    </entry>
</root>
'''
    print(xml_example)

def show_parsed_data_structure():
    """展示解析后的数据结构"""
    print("\n📊 解析后的Python数据结构")
    print("=" * 50)
    
    # 加载实际数据
    loader = KnowledgeDataLoader()
    entries = loader.get_knowledge_entries()
    
    if entries:
        # 显示前3个条目的结构
        for i, entry in enumerate(entries[:3], 1):
            print(f"\n条目 {i}:")
            print(f"  ID: {entry['id']}")
            print(f"  三元组: {entry['triple']}")
            print(f"  Schema: {entry['schema']}")
            print(f"  文本: {entry['text'][:100]}..." if entry['text'] else "  文本: (无)")
            print(f"  源文件: {Path(entry['source_file']).name}")
    else:
        print("❌ 未找到数据条目")

def show_enhanced_text_conversion():
    """展示增强系统的文本转换过程"""
    print("\n🔄 增强系统文本转换过程")
    print("=" * 50)
    
    # 创建增强数据库管理器
    enhanced_db = EnhancedVectorDatabaseManager()
    
    # 示例数据
    example_entries = [
        {
            "id": "example_1",
            "triple": ("Amsterdam_Airport_Schiphol", "location", "Haarlemmermeer"),
            "schema": ("Airport", "location", "City"),
            "text": "Amsterdam Airport Schiphol is located in Haarlemmermeer.",
            "source_file": "example.xml"
        },
        {
            "id": "example_2", 
            "triple": ("Belgium", "leader", "Philippe_of_Belgium"),
            "schema": ("Country", "leader", "King"),
            "text": "Belgium is led by King Philippe.",
            "source_file": "example.xml"
        },
        {
            "id": "example_3",
            "triple": ("Brussels_Airport", "runwayLength", "3638"),
            "schema": ("Airport", "runwayLength", "number"),
            "text": "Brussels Airport has a runway length of 3638 meters.",
            "source_file": "example.xml"
        }
    ]
    
    for i, entry in enumerate(example_entries, 1):
        print(f"\n示例 {i}:")
        print(f"原始三元组: {entry['triple']}")
        print(f"Schema: {entry['schema']}")
        print(f"原始文本: {entry['text']}")
        
        # 转换为增强文本
        enhanced_text = enhanced_db.enhanced_triple_to_text(entry['triple'], entry['schema'])
        print(f"增强文本: {enhanced_text}")
        
        # 创建增强元数据
        enhanced_metadata = enhanced_db.create_enhanced_metadata(entry)
        print(f"增强元数据:")
        for key, value in enhanced_metadata.items():
            if key not in ['source_file', 'text']:  # 跳过长字段
                print(f"  {key}: {value}")

def show_vectorization_input():
    """展示向量化的输入数据"""
    print("\n🎯 向量化输入数据格式")
    print("=" * 50)
    
    # 加载实际数据
    loader = KnowledgeDataLoader()
    entries = loader.get_knowledge_entries()
    
    if not entries:
        print("❌ 未找到数据条目")
        return
    
    # 创建增强数据库管理器
    enhanced_db = EnhancedVectorDatabaseManager()
    
    # 显示前3个条目的向量化输入
    for i, entry in enumerate(entries[:3], 1):
        print(f"\n条目 {i} 的向量化输入:")
        print("-" * 30)
        
        # 原始数据
        print(f"原始三元组: {entry['triple']}")
        print(f"原始Schema: {entry['schema']}")
        
        # 增强文本（这是发送给嵌入模型的文本）
        enhanced_text = enhanced_db.enhanced_triple_to_text(entry['triple'], entry['schema'])
        print(f"发送给嵌入模型的文本:")
        print(f"  '{enhanced_text}'")
        
        # 元数据（存储在向量数据库中的附加信息）
        metadata = enhanced_db.create_enhanced_metadata(entry)
        print(f"存储的元数据字段:")
        for key in sorted(metadata.keys()):
            if key not in ['text', 'source_file']:  # 跳过长字段
                print(f"  {key}: {metadata[key]}")

def show_data_flow_summary():
    """展示数据流程总结"""
    print("\n📋 增强系统数据流程总结")
    print("=" * 50)
    
    flow_steps = [
        {
            "步骤": "1. XML解析",
            "输入": "XML文件 (entry节点)",
            "输出": "Python字典 {id, triple, schema, text, source_file}",
            "示例": "triple: ('Belgium', 'leader', 'Philippe_of_Belgium')"
        },
        {
            "步骤": "2. 文本增强",
            "输入": "三元组 + Schema",
            "输出": "自然语言模板句子",
            "示例": "An instance of a 'Country' named 'Belgium' has a relation 'leader' with an instance of a 'King' which is 'Philippe of Belgium'."
        },
        {
            "步骤": "3. 元数据增强", 
            "输入": "原始条目数据",
            "输出": "丰富的元数据字典",
            "示例": "sub_clean: 'Belgium', entities: 'Belgium Philippe of Belgium', relation_context: 'Country leader King'"
        },
        {
            "步骤": "4. 向量化",
            "输入": "增强文本",
            "输出": "嵌入向量 (1024维)",
            "示例": "[0.123, -0.456, 0.789, ...]"
        },
        {
            "步骤": "5. 存储",
            "输入": "向量 + 文本 + 元数据",
            "输出": "ChromaDB记录",
            "示例": "可通过语义相似度检索"
        }
    ]
    
    for step in flow_steps:
        print(f"\n{step['步骤']}")
        print(f"  输入: {step['输入']}")
        print(f"  输出: {step['输出']}")
        print(f"  示例: {step['示例']}")

def compare_original_vs_enhanced():
    """对比原始系统和增强系统的文本处理"""
    print("\n🔄 原始系统 vs 增强系统对比")
    print("=" * 50)
    
    # 示例三元组
    triple = ("Amsterdam_Airport_Schiphol", "location", "Haarlemmermeer")
    schema = ("Airport", "location", "City")
    
    print(f"示例三元组: {triple}")
    print(f"示例Schema: {schema}")
    
    # 原始系统处理 (简化版)
    original_text = f"{triple[0]} {triple[1]} {triple[2]}"
    print(f"\n原始系统文本: '{original_text}'")
    
    # 增强系统处理
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_text = enhanced_db.enhanced_triple_to_text(triple, schema)
    print(f"增强系统文本: '{enhanced_text}'")
    
    print(f"\n差异分析:")
    print(f"  原始系统: 简单拼接，缺乏语义结构")
    print(f"  增强系统: 自然语言模板，包含类型信息，更适合语义理解")

def main():
    """主函数"""
    print("🔍 增强RAG系统数据向量化前格式展示")
    print("=" * 60)
    
    # 1. 展示原始XML结构
    show_original_xml_structure()
    
    # 2. 展示解析后的数据结构
    show_parsed_data_structure()
    
    # 3. 展示增强文本转换
    show_enhanced_text_conversion()
    
    # 4. 展示向量化输入
    show_vectorization_input()
    
    # 5. 展示数据流程总结
    show_data_flow_summary()
    
    # 6. 对比原始vs增强系统
    compare_original_vs_enhanced()
    
    print(f"\n✅ 数据格式展示完成！")
    print(f"\n💡 关键要点:")
    print(f"   - 原始数据来自XML文件的entry节点")
    print(f"   - 包含三元组(triple)、类型(schema)、文本(text)")
    print(f"   - 增强系统使用自然语言模板转换三元组")
    print(f"   - 丰富的元数据支持多维度检索")
    print(f"   - 最终向量化的是增强后的自然语言文本")

if __name__ == '__main__':
    main()