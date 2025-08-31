#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查增强嵌入系统检索数据格式脚本
展示从enhanced_embedding_system.py嵌入的数据库中检索得到的数据结构和内容
"""

import json
from enhanced_embedding_system import EnhancedVectorDatabaseManager
from typing import Dict, List

def print_separator(title: str):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_retrieval_result(result: Dict, index: int):
    """格式化打印单个检索结果"""
    print(f"\n📄 结果 #{index}")
    print("-" * 40)
    
    # 基本信息
    print(f"🆔 ID: {result['id']}")
    print(f"📊 重排分数: {result.get('rerank_score', 'N/A'):.4f}")
    print(f"📏 原始距离: {result.get('distance', 'N/A'):.4f}")
    
    # 三元组信息
    triple = result['triple']
    schema = result['schema']
    print(f"🔗 三元组: ({triple[0]}, {triple[1]}, {triple[2]})")
    print(f"📋 模式: ({schema[0]}, {schema[1]}, {schema[2]})")
    
    # 生成的文档文本
    print(f"📝 生成文档: {result['document'][:100]}...")
    
    # 详细分数（如果有）
    if 'detailed_scores' in result:
        print("🎯 详细分数:")
        for score_type, score_value in result['detailed_scores'].items():
            print(f"   - {score_type}: {score_value:.4f}")
    
    # 元数据信息
    metadata = result.get('metadata', {})
    print("📊 元数据摘要:")
    print(f"   - 清理后主语: {metadata.get('sub_clean', 'N/A')}")
    print(f"   - 清理后关系: {metadata.get('rel_clean', 'N/A')}")
    print(f"   - 清理后宾语: {metadata.get('obj_clean', 'N/A')}")
    print(f"   - 实体组合: {metadata.get('entities', 'N/A')}")
    print(f"   - 关系上下文: {metadata.get('relation_context', 'N/A')}")
    print(f"   - 来源文件: {metadata.get('source_file', 'N/A')}")

def inspect_database_structure():
    """检查数据库结构"""
    print_separator("数据库结构检查")
    
    # 初始化增强系统
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_db.initialize_collection()
    
    # 获取数据库统计
    stats = enhanced_db.get_database_stats()
    print("📊 数据库统计信息:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    return enhanced_db

def test_single_retrieval(enhanced_db: EnhancedVectorDatabaseManager, query: str, n_results: int = 3):
    """测试单个查询的检索结果"""
    print_separator(f"查询测试: '{query}'")
    
    # 执行多阶段检索
    results = enhanced_db.multi_stage_retrieval(query, n_results=n_results, rerank_top_k=10)
    
    if not results:
        print("❌ 没有找到检索结果")
        return
    
    print(f"✅ 找到 {len(results)} 个结果")
    
    # 打印每个结果
    for i, result in enumerate(results, 1):
        print_retrieval_result(result, i)

def test_stage1_vs_stage2(enhanced_db: EnhancedVectorDatabaseManager, query: str):
    """对比第一阶段和第二阶段检索结果"""
    print_separator(f"阶段对比: '{query}'")
    
    # 第一阶段检索
    print("🔍 第一阶段检索 (基础向量检索):")
    stage1_results = enhanced_db._stage1_retrieval(query, n_results=5)
    
    if stage1_results:
        for i, result in enumerate(stage1_results[:3], 1):
            print(f"   {i}. {result['triple']} (相似度: {result['stage1_score']:.4f})")
    
    # 第二阶段重排
    print("\n🎯 第二阶段重排 (多策略重排):")
    stage2_results = enhanced_db._stage2_reranking(query, stage1_results)
    
    if stage2_results:
        for i, result in enumerate(stage2_results[:3], 1):
            print(f"   {i}. {result['triple']} (重排分数: {result['rerank_score']:.4f})")
            scores = result['detailed_scores']
            print(f"      详细: 实体={scores['entity_match']:.3f}, 关系={scores['relation_match']:.3f}, "
                  f"类型={scores['type_match']:.3f}, 语义={scores['semantic_similarity']:.3f}")

def inspect_metadata_structure(enhanced_db: EnhancedVectorDatabaseManager):
    """检查元数据结构"""
    print_separator("元数据结构检查")
    
    # 获取一个样本结果来检查元数据结构
    sample_results = enhanced_db.multi_stage_retrieval("sample query", n_results=1)
    
    if not sample_results:
        print("❌ 无法获取样本数据")
        return
    
    sample_metadata = sample_results[0].get('metadata', {})
    
    print("📋 元数据字段结构:")
    for key, value in sample_metadata.items():
        value_type = type(value).__name__
        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"   - {key} ({value_type}): {value_preview}")

def export_sample_data(enhanced_db: EnhancedVectorDatabaseManager, filename: str = "sample_retrieval_data.json"):
    """导出样本检索数据到JSON文件"""
    print_separator("导出样本数据")
    
    sample_queries = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport located?",
        "What type is Belgium?"
    ]
    
    export_data = {
        "database_stats": enhanced_db.get_database_stats(),
        "sample_retrievals": {}
    }
    
    for query in sample_queries:
        results = enhanced_db.multi_stage_retrieval(query, n_results=2)
        export_data["sample_retrievals"][query] = results
    
    # 保存到文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 样本数据已导出到: {filename}")
    print(f"📊 包含 {len(sample_queries)} 个查询的检索结果")

def main():
    """主函数"""
    print("🔍 增强嵌入系统检索数据检查器")
    print("=" * 60)
    
    try:
        # 1. 检查数据库结构
        enhanced_db = inspect_database_structure()
        
        # 2. 检查元数据结构
        inspect_metadata_structure(enhanced_db)
        
        # 3. 测试几个查询
        test_queries = [
            "Who is the leader of Belgium?",
            "Where is Amsterdam Airport Schiphol located?",
            "What type of entity is Belgium?"
        ]
        
        for query in test_queries:
            test_single_retrieval(enhanced_db, query, n_results=3)
        
        # 4. 对比阶段检索
        test_stage1_vs_stage2(enhanced_db, "Who is the leader of Belgium?")
        
        # 5. 导出样本数据
        export_sample_data(enhanced_db)
        
        print_separator("检查完成")
        print("✅ 所有检查已完成")
        print("📁 查看 sample_retrieval_data.json 获取详细的JSON格式数据")
        
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()