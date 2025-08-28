# simple_enhanced_test.py - 简化的增强系统测试

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_enhanced_system_only():
    """只测试增强系统本身，不与原始系统对比"""
    print("🧪 测试增强系统（独立测试）")
    print("=" * 50)
    
    try:
        from enhanced_retrieval_engine import EnhancedRetrievalEngine
        
        # 初始化增强系统
        print("🔄 初始化增强系统...")
        enhanced_engine = EnhancedRetrievalEngine()
        
        # 检查数据库状态
        status = enhanced_engine.get_system_status()
        print(f"📊 数据库状态: {status['database_status']['total_documents']} 个文档")
        
        if status['database_status']['total_documents'] == 0:
            print("🔄 数据库为空，正在填充...")
            enhanced_engine.db_manager.populate_enhanced_database()
            
            # 重新检查
            status = enhanced_engine.get_system_status()
            print(f"✅ 数据库填充完成: {status['database_status']['total_documents']} 个文档")
        
        # 测试基础检索
        test_question = "Who is the leader of Belgium?"
        print(f"\n🔍 测试基础检索:")
        print(f"   问题: {test_question}")
        
        basic_result = enhanced_engine.retrieve_and_rewrite(
            test_question, 
            n_results=3, 
            use_reranking=False
        )
        
        print(f"   基础检索答案: {basic_result['final_answer']}")
        print(f"   检索到 {len(basic_result['retrieved_items'])} 个结果")
        
        # 测试增强检索
        print(f"\n🚀 测试增强检索:")
        enhanced_result = enhanced_engine.retrieve_and_rewrite(
            test_question, 
            n_results=3, 
            use_reranking=True
        )
        
        print(f"   增强检索答案: {enhanced_result['final_answer']}")
        print(f"   检索到 {len(enhanced_result['retrieved_items'])} 个结果")
        
        # 显示重排信息
        if enhanced_result['retrieved_items'] and 'rerank_score' in enhanced_result['retrieved_items'][0]:
            top_item = enhanced_result['retrieved_items'][0]
            print(f"   Top-1重排分数: {top_item['rerank_score']:.4f}")
            
            if 'detailed_scores' in top_item:
                scores = top_item['detailed_scores']
                print(f"   详细分数: 实体={scores.get('entity_match', 0):.3f}, "
                      f"关系={scores.get('relation_match', 0):.3f}, "
                      f"类型={scores.get('type_match', 0):.3f}")
        
        print(f"\n✅ 增强系统测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 增强系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_questions():
    """测试多个问题"""
    print(f"\n📋 测试多个问题")
    print("=" * 50)
    
    try:
        from enhanced_retrieval_engine import EnhancedRetrievalEngine
        
        enhanced_engine = EnhancedRetrievalEngine()
        
        test_questions = [
            "Who is the leader of Belgium?",
            "Where is Amsterdam Airport located?",
            "What type of entity is Belgium?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. 问题: {question}")
            
            try:
                result = enhanced_engine.retrieve_and_rewrite(
                    question, 
                    n_results=3, 
                    use_reranking=True
                )
                
                print(f"   答案: {result['final_answer']}")
                print(f"   问题类型: {result['retrieval_stats']['question_type']}")
                print(f"   检索方法: {result['retrieval_stats'].get('retrieval_method', 'N/A')}")
                
                # 显示Top-1结果
                if result['retrieved_items']:
                    top_triple = result['retrieved_items'][0]['triple']
                    print(f"   Top-1三元组: {top_triple}")
                
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
        
        print(f"\n✅ 多问题测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 多问题测试失败: {e}")
        return False

def check_system_components():
    """检查系统组件状态"""
    print(f"\n🔧 检查系统组件")
    print("=" * 50)
    
    components_status = {}
    
    # 检查增强嵌入系统
    try:
        from enhanced_embedding_system import EnhancedVectorDatabaseManager
        enhanced_db = EnhancedVectorDatabaseManager()
        enhanced_db.initialize_collection()
        components_status['enhanced_embedding'] = True
        print("✅ 增强嵌入系统 - 正常")
    except Exception as e:
        components_status['enhanced_embedding'] = False
        print(f"❌ 增强嵌入系统 - 失败: {e}")
    
    # 检查增强检索引擎
    try:
        from enhanced_retrieval_engine import EnhancedRetrievalEngine
        enhanced_engine = EnhancedRetrievalEngine()
        components_status['enhanced_retrieval'] = True
        print("✅ 增强检索引擎 - 正常")
    except Exception as e:
        components_status['enhanced_retrieval'] = False
        print(f"❌ 增强检索引擎 - 失败: {e}")
    
    # 检查CoTKR重写器
    try:
        from cotkr_rewriter import CoTKRRewriter
        rewriter = CoTKRRewriter()
        components_status['cotkr_rewriter'] = True
        print("✅ CoTKR重写器 - 正常")
    except Exception as e:
        components_status['cotkr_rewriter'] = False
        print(f"❌ CoTKR重写器 - 失败: {e}")
    
    # 检查嵌入客户端
    try:
        from embedding_client import EmbeddingClient
        client = EmbeddingClient()
        components_status['embedding_client'] = True
        print("✅ 嵌入客户端 - 正常")
    except Exception as e:
        components_status['embedding_client'] = False
        print(f"❌ 嵌入客户端 - 失败: {e}")
    
    # 汇总
    working_components = sum(components_status.values())
    total_components = len(components_status)
    
    print(f"\n📊 组件状态汇总: {working_components}/{total_components} 个组件正常")
    
    return working_components == total_components

def main():
    """主测试函数"""
    print("🚀 增强RAG系统简化测试")
    print("🎯 专注于增强系统本身，避免与原始系统的兼容性问题")
    print("=" * 60)
    
    tests = [
        ("系统组件检查", check_system_components),
        ("增强系统独立测试", test_enhanced_system_only),
        ("多问题测试", test_multiple_questions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 运行 {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print(f"\n📋 测试结果汇总:")
    print("=" * 30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 增强系统测试全部通过！")
        print("\n💡 下一步:")
        print("   1. 运行 python demo_enhanced_system.py 查看详细演示")
        print("   2. 如果需要对比原始系统，请先确保原始系统数据库已初始化")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

if __name__ == '__main__':
    main()