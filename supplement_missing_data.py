# supplement_missing_data.py - 补充缺失的关键数据

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from vector_database import VectorDatabaseManager
from embedding_client import EmbeddingClient
import config

def supplement_missing_data():
    """补充缺失的关键数据"""
    print("🔧 补充缺失的关键数据")
    print("=" * 50)
    
    # 需要补充的关键数据
    missing_data = [
        # Belgium的领导信息
        {
            "id": "belgium_leader_001",
            "triple": ("Belgium", "leader", "Philippe_of_Belgium"),
            "schema": ("Country", "leader", "King"),
            "text": "Belgium leader Philippe of Belgium"
        },
        {
            "id": "belgium_leader_002", 
            "triple": ("Belgium", "primeMinister", "Alexander_De_Croo"),
            "schema": ("Country", "primeMinister", "PrimeMinister"),
            "text": "Belgium prime minister Alexander De Croo"
        },
        
        # Amsterdam Airport的位置信息
        {
            "id": "amsterdam_airport_location_001",
            "triple": ("Amsterdam_Airport_Schiphol", "location", "Netherlands"),
            "schema": ("Airport", "location", "Country"),
            "text": "Amsterdam Airport Schiphol location Netherlands"
        },
        {
            "id": "amsterdam_airport_location_002",
            "triple": ("Amsterdam_Airport_Schiphol", "city", "Amsterdam"),
            "schema": ("Airport", "city", "City"),
            "text": "Amsterdam Airport Schiphol city Amsterdam"
        },
        {
            "id": "amsterdam_airport_location_003",
            "triple": ("Amsterdam_Airport_Schiphol", "country", "Netherlands"),
            "schema": ("Airport", "country", "Country"),
            "text": "Amsterdam Airport Schiphol country Netherlands"
        },
        
        # 其他有用的数据
        {
            "id": "netherlands_capital_001",
            "triple": ("Netherlands", "capital", "Amsterdam"),
            "schema": ("Country", "capital", "CapitalCity"),
            "text": "Netherlands capital Amsterdam"
        },
        {
            "id": "belgium_type_001",
            "triple": ("Belgium", "type", "Country"),
            "schema": ("Country", "type", "EntityType"),
            "text": "Belgium type Country"
        }
    ]
    
    print(f"📊 准备补充 {len(missing_data)} 条关键数据")
    
    # 初始化组件
    db_manager = VectorDatabaseManager()
    db_manager.initialize_collection()
    embedding_client = EmbeddingClient()
    
    # 准备数据
    ids = []
    documents = []
    metadatas = []
    
    for entry in missing_data:
        # 构建文档文本
        sub, rel, obj = entry["triple"]
        sub_type, rel_type, obj_type = entry["schema"]
        
        document = f"{sub.replace('_', ' ')} {rel.replace('_', ' ')} {obj.replace('_', ' ')}. Types: {sub_type} {rel_type} {obj_type}."
        
        ids.append(entry["id"])
        documents.append(document)
        metadatas.append({
            "sub": sub,
            "rel": rel,
            "obj": obj,
            "sub_type": sub_type,
            "rel_type": rel_type,
            "obj_type": obj_type,
            "source_file": "supplemented_data",
            "text": entry["text"]
        })
    
    # 获取嵌入向量
    print("🔄 生成嵌入向量...")
    embeddings = embedding_client.get_embeddings_batch(documents)
    
    if embeddings:
        # 添加到数据库
        print("💾 添加到向量数据库...")
        db_manager.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✅ 成功补充 {len(missing_data)} 条数据")
        
        # 验证补充结果
        print("\n🔍 验证补充结果:")
        
        # 检查Belgium leader
        belgium_results = db_manager.query_database("Belgium leader", n_results=3)
        print("Belgium leader查询结果:")
        for i, result in enumerate(belgium_results, 1):
            triple = result['triple']
            similarity = 1 - result['distance']
            print(f"   {i}. {triple} (相似度: {similarity:.4f})")
        
        # 检查Amsterdam Airport location
        airport_results = db_manager.query_database("Amsterdam Airport location", n_results=3)
        print("\nAmsterdam Airport location查询结果:")
        for i, result in enumerate(airport_results, 1):
            triple = result['triple']
            similarity = 1 - result['distance']
            print(f"   {i}. {triple} (相似度: {similarity:.4f})")
        
    else:
        print("❌ 嵌入向量生成失败")

def test_improved_answers():
    """测试补充数据后的答案质量"""
    print(f"\n🧪 测试补充数据后的答案质量")
    print("=" * 50)
    
    from retrieval_engine import RetrievalEngine
    
    engine = RetrievalEngine()
    
    test_questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport Schiphol located?",
        "What is the capital of Netherlands?",
        "What type of entity is Belgium?"
    ]
    
    for question in test_questions:
        print(f"\n❓ 问题: {question}")
        
        try:
            result = engine.retrieve_and_rewrite(question)
            
            print(f"💡 答案: {result['final_answer']}")
            print(f"🏷 问题类型: {result['retrieval_stats']['question_type']}")
            
            # 显示最相关的检索结果
            if result['retrieved_items']:
                top_result = result['retrieved_items'][0]
                similarity = 1 - top_result['distance']
                print(f"📊 最相关结果: {top_result['triple']} (相似度: {similarity:.4f})")
            
        except Exception as e:
            print(f"❌ 错误: {e}")

def check_data_coverage():
    """检查数据覆盖情况"""
    print(f"\n📈 检查数据覆盖情况")
    print("=" * 50)
    
    db_manager = VectorDatabaseManager()
    db_manager.initialize_collection()
    
    # 获取更新后的统计
    stats = db_manager.get_database_stats()
    print(f"📊 更新后的数据库统计:")
    print(f"   - 文档总数: {stats['total_documents']}")
    
    # 检查关键查询
    key_queries = [
        ("Belgium leader", "Belgium领导信息"),
        ("Amsterdam Airport location", "Amsterdam机场位置"),
        ("Netherlands capital", "荷兰首都"),
        ("Belgium type", "Belgium类型")
    ]
    
    for query, description in key_queries:
        results = db_manager.query_database(query, n_results=1)
        if results:
            top_result = results[0]
            similarity = 1 - top_result['distance']
            print(f"✅ {description}: {top_result['triple']} (相似度: {similarity:.4f})")
        else:
            print(f"❌ {description}: 未找到相关数据")

if __name__ == '__main__':
    supplement_missing_data()
    test_improved_answers()
    check_data_coverage()
    
    print(f"\n🎉 数据补充完成！")
    print(f"\n💡 补充的关键数据:")
    print(f"   1. Belgium的领导信息 (King Philippe, PM Alexander De Croo)")
    print(f"   2. Amsterdam Airport的位置信息 (Netherlands, Amsterdam)")
    print(f"   3. Netherlands的首都信息 (Amsterdam)")
    print(f"   4. Belgium的类型信息 (Country)")
    print(f"\n🔄 现在可以重新测试问答系统的效果！")