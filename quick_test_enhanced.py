# quick_test_enhanced.py - 快速测试增强系统

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_enhanced_embedding():
    """测试增强嵌入功能"""
    print("🧪 测试增强嵌入功能")
    print("=" * 40)
    
    try:
        from enhanced_embedding_system import EnhancedVectorDatabaseManager
        
        # 初始化增强数据库
        enhanced_db = EnhancedVectorDatabaseManager()
        enhanced_db.initialize_collection(reset=True)
        
        # 测试文本转换
        example_triple = ("Belgium", "leader", "Philippe_of_Belgium")
        example_schema = ("Country", "leader", "King")
        
        enhanced_text = enhanced_db.enhanced_triple_to_text(example_triple, example_schema)
        print(f"✅ 增强文本转换成功:")
        print(f"   {enhanced_text}")
        
        # 测试元数据创建
        entry = {
            "id": "test_001",
            "triple": example_triple,
            "schema": example_schema,
            "text": "Test text",
            "source_file": "test.xml"
        }
        
        metadata = enhanced_db.create_enhanced_metadata(entry)
        print(f"✅ 元数据创建成功，包含 {len(metadata)} 个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强嵌入测试失败: {e}")
        return False

def test_enhanced_retrieval():
    """测试增强检索功能"""
    print("\n🔍 测试增强检索功能")
    print("=" * 40)
    
    try:
        from enhanced_retrieval_engine import EnhancedRetrievalEngine
        
        # 初始化增强检索引擎
        enhanced_engine = EnhancedRetrievalEngine()
        
        # 测试系统状态
        status = enhanced_engine.get_system_status()
        print(f"✅ 系统状态获取成功:")
        print(f"   系统名称: {status['system_name']}")
        print(f"   数据库文档数: {status['database_status']['total_documents']}")
        
        # 测试简单查询
        test_question = "Who is the leader of Belgium?"
        result = enhanced_engine.retrieve_and_rewrite(test_question, n_results=3, use_reranking=False)
        
        print(f"✅ 基础检索测试成功:")
        print(f"   问题: {test_question}")
        print(f"   答案: {result['final_answer']}")
        print(f"   检索到 {len(result['retrieved_items'])} 个结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强检索测试失败: {e}")
        return False

def test_evaluation_system():
    """测试评估系统功能"""
    print("\n📊 测试评估系统功能")
    print("=" * 40)
    
    try:
        from retrieval_evaluation_system import RetrievalEvaluator
        
        # 初始化评估器
        evaluator = RetrievalEvaluator()
        
        # 测试单个问题评估
        test_question_data = {
            'question': "Who is the leader of Belgium?",
            'expected_answer': "Philippe",
            'question_type': 'subject',
            'source_text': 'Belgium leader test',
            'triple': ("Belgium", "leader", "Philippe_of_Belgium"),
            'schema': ("Country", "leader", "King")
        }
        
        result = evaluator.evaluate_single_question(test_question_data, k_values=[1, 3])
        
        print(f"✅ 单问题评估测试成功:")
        print(f"   问题: {result['question']}")
        print(f"   原始系统答案: {result['original_system']['final_answer']}")
        print(f"   增强系统答案: {result['enhanced_system']['final_answer']}")
        
        # 显示部分指标
        orig_p1 = result['original_system']['metrics'].get('precision@1', 0)
        enh_p1 = result['enhanced_system']['metrics'].get('precision@1', 0)
        print(f"   Precision@1: 原始={orig_p1:.3f}, 增强={enh_p1:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 评估系统测试失败: {e}")
        return False

def test_system_comparison():
    """测试系统对比功能"""
    print("\n⚖️ 测试系统对比功能")
    print("=" * 40)
    
    try:
        from retrieval_engine import RetrievalEngine
        from enhanced_retrieval_engine import EnhancedRetrievalEngine
        
        # 检查增强系统的数据库状态
        enhanced_engine = EnhancedRetrievalEngine()
        enhanced_status = enhanced_engine.get_system_status()
        
        if enhanced_status['database_status']['total_documents'] == 0:
            print("⚠️ 增强系统数据库为空，需要先填充数据")
            print("🔄 正在填充增强系统数据库...")
            
            # 填充增强系统数据库
            enhanced_engine.db_manager.populate_enhanced_database()
            
            # 重新检查状态
            enhanced_status = enhanced_engine.get_system_status()
            print(f"✅ 增强系统数据库已填充，文档数: {enhanced_status['database_status']['total_documents']}")
        
        # 初始化原始系统
        original_engine = RetrievalEngine()
        original_status = original_engine.get_system_status()
        
        if original_status['database_status']['total_documents'] == 0:
            print("⚠️ 原始系统数据库为空，跳过对比测试")
            print("💡 请先运行 python main_system.py --mode setup 初始化原始系统")
            return False
        
        test_question = "Where is Amsterdam Airport located?"
        
        print(f"🔄 测试问题: {test_question}")
        
        # 获取两个系统的结果
        print("   - 查询原始系统...")
        original_result = original_engine.retrieve_and_rewrite(test_question, n_results=3)
        
        print("   - 查询增强系统...")
        enhanced_result = enhanced_engine.retrieve_and_rewrite(test_question, n_results=3, use_reranking=True)
        
        print(f"✅ 系统对比测试成功:")
        print(f"   问题: {test_question}")
        print(f"   原始系统答案: {original_result['final_answer']}")
        print(f"   增强系统答案: {enhanced_result['final_answer']}")
        
        # 比较检索质量
        orig_avg_dist = original_result['retrieval_stats']['avg_distance']
        enh_avg_dist = enhanced_result['retrieval_stats']['avg_distance']
        print(f"   平均距离: 原始={orig_avg_dist:.4f}, 增强={enh_avg_dist:.4f}")
        
        # 显示检索方法
        orig_method = original_result['retrieval_stats'].get('retrieval_method', 'basic')
        enh_method = enhanced_result['retrieval_stats'].get('retrieval_method', 'enhanced')
        print(f"   检索方法: 原始={orig_method}, 增强={enh_method}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 增强RAG系统快速测试")
    print("=" * 50)
    
    tests = [
        ("增强嵌入", test_enhanced_embedding),
        ("增强检索", test_enhanced_retrieval),
        ("评估系统", test_evaluation_system),
        ("系统对比", test_system_comparison)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 运行 {test_name} 测试...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
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
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n💡 下一步建议:")
        print("   1. 运行 python demo_enhanced_system.py 查看详细演示")
        print("   2. 运行 python retrieval_evaluation_system.py 进行全面评估")
    else:
        print("⚠️ 部分测试失败，请检查系统配置。")

if __name__ == '__main__':
    main()