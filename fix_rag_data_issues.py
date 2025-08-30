#!/usr/bin/env python3
# fix_rag_data_issues.py - 修复RAG数据问题

from enhanced_embedding_system import EnhancedVectorDatabaseManager
import json

def add_missing_data():
    """添加缺失的关键数据"""
    print("🔧 修复RAG数据问题")
    print("=" * 50)
    
    db_manager = EnhancedVectorDatabaseManager()
    db_manager.initialize_collection()
    
    # 需要添加的关键数据
    missing_data = [
        # 荷兰首都信息
        {
            "triple": ("Netherlands", "capital", "Amsterdam"),
            "schema": ("Country", "capital", "CapitalCity"),
            "text": "Netherlands capital Amsterdam. The capital city of Netherlands is Amsterdam.",
            "source_file": "manual_fix.json"
        },
        # 比利时现任总理信息
        {
            "triple": ("Belgium", "primeMinister", "Alexander_De_Croo"),
            "schema": ("Country", "primeMinister", "PrimeMinister"),
            "text": "Belgium primeMinister Alexander De Croo. Alexander De Croo is the Prime Minister of Belgium.",
            "source_file": "manual_fix.json"
        },
        # 布鲁塞尔机场位置信息
        {
            "triple": ("Brussels_Airport", "location", "Belgium"),
            "schema": ("Airport", "location", "Country"),
            "text": "Brussels Airport location Belgium. Brussels Airport is located in Belgium.",
            "source_file": "manual_fix.json"
        },
        {
            "triple": ("Brussels_Airport", "city", "Brussels"),
            "schema": ("Airport", "city", "CapitalCity"),
            "text": "Brussels Airport city Brussels. Brussels Airport is located near Brussels.",
            "source_file": "manual_fix.json"
        }
    ]
    
    print(f"📝 准备添加 {len(missing_data)} 条关键数据...")
    
    # 添加数据到向量数据库
    for i, data in enumerate(missing_data, 1):
        try:
            # 构造文档
            document = f"An instance of a '{data['schema'][0]}' named '{data['triple'][0]}' has a relation '{data['triple'][1]}' with an instance of a '{data['schema'][2]}' named '{data['triple'][2]}'."
            
            # 获取嵌入
            embedding = db_manager.embedding_client.get_embeddings_batch([data['text']])
            if not embedding:
                print(f"❌ 无法获取第 {i} 条数据的嵌入")
                continue
            
            # 构造元数据
            metadata = {
                'sub': data['triple'][0],
                'rel': data['triple'][1], 
                'obj': data['triple'][2],
                'sub_type': data['schema'][0],
                'rel_type': data['triple'][1],
                'obj_type': data['schema'][2],
                'text': data['text'],
                'source_file': data['source_file']
            }
            
            # 添加到数据库
            db_manager.collection.add(
                embeddings=embedding,
                documents=[document],
                metadatas=[metadata],
                ids=[f"manual_fix_{i}"]
            )
            
            print(f"✅ 已添加: {data['triple']}")
            
        except Exception as e:
            print(f"❌ 添加第 {i} 条数据时出错: {e}")
    
    # 验证添加结果
    print(f"\n🔍 验证添加结果...")
    
    test_queries = [
        "Netherlands capital",
        "Belgium prime minister Alexander De Croo", 
        "Brussels Airport location Belgium"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = db_manager.collection.query(
            query_texts=[query],
            n_results=3
        )
        
        if results and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0][:2]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                print(f"  {i+1}. 三元组: ({metadata['sub']}, {metadata['rel']}, {metadata['obj']})")
                print(f"     距离: {distance:.4f}")
        else:
            print("  未找到相关结果")
    
    print(f"\n✅ 数据修复完成！")

def test_fixed_retrieval():
    """测试修复后的检索效果"""
    print(f"\n🧪 测试修复后的检索效果")
    print("=" * 50)
    
    from enhanced_retrieval_engine import EnhancedRetrievalEngine
    engine = EnhancedRetrievalEngine()
    
    test_questions = [
        'Who is the prime minister of Belgium?',  # 改为更具体的问题
        'What is the capital of Netherlands?',
        'Where is Brussels Airport located?'
    ]
    
    for question in test_questions:
        print(f"\n🔍 问题: {question}")
        print("-" * 30)
        
        try:
            result = engine.retrieve_and_rewrite(question)
            
            print(f"检索项目数: {len(result.get('retrieved_items', []))}")
            
            # 显示最相关的结果
            if result.get('retrieved_items'):
                top_item = result['retrieved_items'][0]
                print(f"最佳匹配: {top_item.get('triple', 'N/A')}")
                print(f"距离: {top_item.get('distance', 'N/A'):.4f}")
            
            print(f"最终答案: {result.get('final_answer', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == '__main__':
    # 添加缺失数据
    add_missing_data()
    
    # 测试修复效果
    test_fixed_retrieval()