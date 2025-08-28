# test_improved_qa.py - 测试改进后的问答系统

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from retrieval_engine import RetrievalEngine

def test_improved_qa_system():
    """测试改进后的问答系统"""
    print("🔧 测试改进后的问答系统")
    print("🎯 主要改进:")
    print("   1. 智能答案提取 - 根据问题语义匹配最相关答案")
    print("   2. 增强查询策略 - 生成多个查询变体提高检索质量")
    print("   3. 相关性重排序 - 基于问题类型调整结果排序")
    print("=" * 70)
    
    engine = RetrievalEngine()
    
    # 测试问题
    test_cases = [
        {
            'question': "Who is the leader of Belgium?",
            'expected_type': 'subject',
            'description': '测试领导者问题 - 应该返回领导者姓名而不是国家名'
        },
        {
            'question': "Where is Amsterdam Airport Schiphol located?",
            'expected_type': 'object',
            'description': '测试位置问题 - 应该返回地理位置而不是跑道信息'
        },
        {
            'question': "What is the relationship between Belgium and Brussels?",
            'expected_type': 'relationship',
            'description': '测试关系问题 - 应该返回关系类型'
        },
        {
            'question': "What type of entity is Belgium?",
            'expected_type': 'type',
            'description': '测试类型问题 - 应该返回实体类型'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}: {test_case['description']}")
        print(f"问题: {test_case['question']}")
        print("-" * 70)
        
        try:
            # 执行查询
            result = engine.retrieve_and_rewrite(test_case['question'])
            
            print(f"🏷 检测到的问题类型: {result['retrieval_stats']['question_type']}")
            print(f"📊 检索统计:")
            print(f"   - 检索文档数: {result['retrieval_stats']['num_retrieved']}")
            print(f"   - 平均相似度: {1 - result['retrieval_stats']['avg_distance']:.4f}")
            
            print(f"\n📚 检索到的知识 (Top 3):")
            for j, item in enumerate(result['retrieved_items'][:3], 1):
                triple = item['triple']
                similarity = 1 - item['distance']
                relevance = item.get('relevance_score', 'N/A')
                print(f"   {j}. 三元组: {triple}")
                print(f"      相似度: {similarity:.4f} | 相关性: {relevance}")
                if 'query_variant' in item:
                    print(f"      查询变体: {item['query_variant']}")
            
            print(f"\n💡 最终答案: {result['final_answer']}")
            
            # 简单的答案质量评估
            answer = result['final_answer'].lower()
            question_lower = test_case['question'].lower()
            
            print(f"\n🔍 答案质量评估:")
            if 'leader' in question_lower and 'belgium' in question_lower:
                if answer != 'belgium' and len(answer) > 3:
                    print("   ✅ 改进成功 - 没有返回国家名本身")
                else:
                    print("   ❌ 仍需改进 - 返回了错误答案")
            
            elif 'where' in question_lower and 'airport' in question_lower:
                if 'runway' not in answer and 'aalsmeerbaan' not in answer:
                    print("   ✅ 改进成功 - 没有返回跑道信息")
                else:
                    print("   ❌ 仍需改进 - 返回了跑道信息")
            
            else:
                print("   ℹ️ 其他类型问题，需要人工评估")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

def test_query_variants():
    """测试查询变体生成"""
    print("\n🔍 测试查询变体生成功能")
    print("=" * 50)
    
    from vector_database import VectorDatabaseManager
    
    db_manager = VectorDatabaseManager()
    db_manager.initialize_collection()
    
    test_queries = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport Schiphol located?",
        "What type of entity is Belgium?"
    ]
    
    for query in test_queries:
        print(f"\n原始查询: {query}")
        variants = db_manager._generate_query_variants(query)
        print("生成的变体:")
        for i, variant in enumerate(variants, 1):
            print(f"   {i}. {variant}")

def compare_before_after():
    """对比改进前后的效果"""
    print("\n📊 对比改进前后的效果")
    print("=" * 50)
    
    engine = RetrievalEngine()
    
    # 问题和期望的改进
    comparisons = [
        {
            'question': "Who is the leader of Belgium?",
            'before': "Belgium (错误 - 返回了国家名)",
            'expected': "领导者姓名 (如果数据库中有的话)"
        },
        {
            'question': "Where is Amsterdam Airport Schiphol located?", 
            'before': "18L/36R Aalsmeerbaan (错误 - 返回了跑道名)",
            'expected': "地理位置 (如Netherlands或具体城市)"
        }
    ]
    
    for comp in comparisons:
        print(f"\n问题: {comp['question']}")
        print(f"改进前: {comp['before']}")
        print(f"期望结果: {comp['expected']}")
        
        result = engine.retrieve_and_rewrite(comp['question'])
        print(f"改进后: {result['final_answer']}")
        
        # 检查是否有改进
        answer_lower = result['final_answer'].lower()
        if 'leader' in comp['question'].lower():
            if answer_lower != 'belgium':
                print("✅ 有改进 - 不再返回国家名")
            else:
                print("❌ 仍需改进")
        elif 'where' in comp['question'].lower():
            if 'runway' not in answer_lower and 'aalsmeerbaan' not in answer_lower:
                print("✅ 有改进 - 不再返回跑道信息")
            else:
                print("❌ 仍需改进")

if __name__ == '__main__':
    test_improved_qa_system()
    test_query_variants()
    compare_before_after()
    
    print(f"\n🎉 测试完成！")
    print(f"\n💡 主要改进点:")
    print(f"   1. 智能答案提取 - 根据问题语义和关系类型匹配答案")
    print(f"   2. 增强查询策略 - 为不同问题类型生成针对性查询变体")
    print(f"   3. 相关性重排序 - 基于问题类型和实体匹配调整结果排序")
    print(f"   4. 语义理解 - 区分领导关系、位置关系等不同语义")