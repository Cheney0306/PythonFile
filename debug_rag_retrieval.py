#!/usr/bin/env python3
# debug_rag_retrieval.py - 调试RAG检索问题

from enhanced_retrieval_engine import EnhancedRetrievalEngine

def debug_rag_retrieval():
    """调试RAG检索问题"""
    print("🔍 调试RAG检索问题")
    print("=" * 50)
    
    engine = EnhancedRetrievalEngine()
    
    # 测试问题
    test_questions = [
        'Who is the leader of Belgium?',
        'What is the capital of Netherlands?', 
        'Where is Brussels Airport located?'
    ]
    
    for question in test_questions:
        print(f"\n🔍 问题: {question}")
        print("-" * 40)
        
        try:
            result = engine.retrieve_and_rewrite(question)
            
            print(f"检索到的项目数: {len(result.get('retrieved_items', []))}")
            
            # 显示检索到的前3个项目
            for i, item in enumerate(result.get('retrieved_items', [])[:3]):
                print(f"  {i+1}. 三元组: {item.get('triple', 'N/A')}")
                print(f"     距离: {item.get('distance', 'N/A'):.4f}")
                print(f"     文档: {item.get('document', 'N/A')[:80]}...")
                print()
            
            print(f"CoTKR知识: {result.get('cotkr_knowledge', 'N/A')[:200]}...")
            print(f"最终答案: {result.get('final_answer', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("=" * 50)

if __name__ == '__main__':
    debug_rag_retrieval()