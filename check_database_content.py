# check_database_content.py - 检查数据库内容

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from vector_database import VectorDatabaseManager

def check_database_content():
    """检查数据库中的内容"""
    print("🔍 检查向量数据库内容")
    print("=" * 50)
    
    db_manager = VectorDatabaseManager()
    db_manager.initialize_collection()
    
    # 获取数据库统计
    stats = db_manager.get_database_stats()
    print(f"📊 数据库统计:")
    print(f"   - 集合名称: {stats['collection_name']}")
    print(f"   - 文档总数: {stats['total_documents']}")
    print(f"   - 状态: {stats['status']}")
    
    # 检查Belgium相关的数据
    print(f"\n🇧🇪 检查Belgium相关数据:")
    belgium_results = db_manager.query_database("Belgium", n_results=10)
    
    for i, result in enumerate(belgium_results, 1):
        triple = result['triple']
        schema = result['schema']
        similarity = 1 - result['distance']
        
        print(f"   {i}. 三元组: {triple}")
        print(f"      Schema: {schema}")
        print(f"      相似度: {similarity:.4f}")
        print(f"      文档: {result['document'][:100]}...")
        print()
    
    # 检查Amsterdam Airport相关的数据
    print(f"\n✈️ 检查Amsterdam Airport相关数据:")
    airport_results = db_manager.query_database("Amsterdam Airport", n_results=10)
    
    for i, result in enumerate(airport_results, 1):
        triple = result['triple']
        schema = result['schema']
        similarity = 1 - result['distance']
        
        print(f"   {i}. 三元组: {triple}")
        print(f"      Schema: {schema}")
        print(f"      相似度: {similarity:.4f}")
        print(f"      文档: {result['document'][:100]}...")
        print()
    
    # 检查leader关系的数据
    print(f"\n👑 检查包含leader关系的数据:")
    leader_results = db_manager.query_database("leader president king", n_results=10)
    
    for i, result in enumerate(leader_results, 1):
        triple = result['triple']
        schema = result['schema']
        similarity = 1 - result['distance']
        
        print(f"   {i}. 三元组: {triple}")
        print(f"      Schema: {schema}")
        print(f"      相似度: {similarity:.4f}")
        print()
    
    # 检查location关系的数据
    print(f"\n📍 检查包含location关系的数据:")
    location_results = db_manager.query_database("location country place", n_results=10)
    
    for i, result in enumerate(location_results, 1):
        triple = result['triple']
        schema = result['schema']
        similarity = 1 - result['distance']
        
        print(f"   {i}. 三元组: {triple}")
        print(f"      Schema: {schema}")
        print(f"      相似度: {similarity:.4f}")
        print()

def analyze_data_quality():
    """分析数据质量"""
    print(f"\n📈 数据质量分析")
    print("=" * 50)
    
    db_manager = VectorDatabaseManager()
    db_manager.initialize_collection()
    
    # 获取所有数据进行分析
    all_results = db_manager.query_database("", n_results=50)  # 获取更多数据
    
    # 统计关系类型
    relation_counts = {}
    schema_counts = {}
    
    for result in all_results:
        triple = result['triple']
        schema = result['schema']
        
        rel = triple[1]
        rel_type = schema[1]
        
        relation_counts[rel] = relation_counts.get(rel, 0) + 1
        schema_counts[rel_type] = schema_counts.get(rel_type, 0) + 1
    
    print(f"🔗 关系类型分布 (Top 10):")
    sorted_relations = sorted(relation_counts.items(), key=lambda x: x[1], reverse=True)
    for rel, count in sorted_relations[:10]:
        print(f"   {rel}: {count} 次")
    
    print(f"\n📋 Schema关系类型分布:")
    sorted_schemas = sorted(schema_counts.items(), key=lambda x: x[1], reverse=True)
    for schema_type, count in sorted_schemas:
        print(f"   {schema_type}: {count} 次")
    
    # 检查是否有Belgium的leader信息
    print(f"\n🔍 专项检查:")
    
    belgium_leader_found = False
    amsterdam_location_found = False
    
    for result in all_results:
        triple = result['triple']
        sub, rel, obj = triple
        
        if 'belgium' in sub.lower() and 'leader' in rel.lower():
            print(f"   ✅ 找到Belgium领导信息: {triple}")
            belgium_leader_found = True
        
        if 'amsterdam' in sub.lower() and 'location' in rel.lower():
            print(f"   ✅ 找到Amsterdam位置信息: {triple}")
            amsterdam_location_found = True
    
    if not belgium_leader_found:
        print(f"   ❌ 未找到Belgium的leader信息")
    
    if not amsterdam_location_found:
        print(f"   ❌ 未找到Amsterdam Airport的location信息")

def suggest_improvements():
    """建议改进方案"""
    print(f"\n💡 改进建议")
    print("=" * 50)
    
    print("基于数据库内容分析，建议以下改进:")
    print()
    print("1. 📊 数据完整性问题:")
    print("   - 如果缺少Belgium的leader信息，需要补充相关数据")
    print("   - 如果缺少Amsterdam Airport的location信息，需要添加位置数据")
    print()
    print("2. 🔍 检索策略改进:")
    print("   - 增加同义词扩展 (leader -> president, king, prime minister)")
    print("   - 增加实体别名处理 (Amsterdam Airport -> Amsterdam_Airport_Schiphol)")
    print()
    print("3. 🧠 答案提取改进:")
    print("   - 基于关系语义而不是简单的位置提取")
    print("   - 增加答案验证机制")
    print()
    print("4. 📈 质量评估:")
    print("   - 建立答案质量评估指标")
    print("   - 添加人工标注的测试集")

if __name__ == '__main__':
    check_database_content()
    analyze_data_quality()
    suggest_improvements()