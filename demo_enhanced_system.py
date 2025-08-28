# demo_enhanced_system.py - 增强系统演示

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from enhanced_embedding_system import EnhancedVectorDatabaseManager
from enhanced_retrieval_engine import EnhancedRetrievalEngine
from retrieval_engine import RetrievalEngine

def demo_embedding_improvements():
    """演示嵌入改进效果"""
    print("🎯 演示嵌入改进效果")
    print("=" * 60)
    
    # 示例三元组
    example_triple = ("Belgium", "leader", "Philippe_of_Belgium")
    example_schema = ("Country", "leader", "King")
    
    print("📋 示例三元组:")
    print(f"   三元组: {example_triple}")
    print(f"   Schema: {example_schema}")
    
    # 原始方法
    from vector_database import VectorDatabaseManager
    original_db = VectorDatabaseManager()
    original_text = original_db.triple_to_embedding_text(example_triple, example_schema)
    
    # 增强方法
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_text = enhanced_db.enhanced_triple_to_text(example_triple, example_schema)
    
    print(f"\n🔄 文本转换对比:")
    print(f"原始方法: \"{original_text}\"")
    print(f"增强方法: \"{enhanced_text}\"")
    
    # 元数据对比
    entry = {
        "id": "demo_001",
        "triple": example_triple,
        "schema": example_schema,
        "text": "Belgium's leader is King Philippe.",
        "source_file": "demo.xml"
    }
    
    enhanced_metadata = enhanced_db.create_enhanced_metadata(entry)
    
    print(f"\n📊 增强元数据:")
    for key, value in enhanced_metadata.items():
        if key not in ['source_file', 'text']:  # 跳过原有字段
            print(f"   {key}: {value}")

def demo_multi_stage_retrieval():
    """演示多阶段检索效果"""
    print(f"\n🔍 演示多阶段检索效果")
    print("=" * 60)
    
    # 初始化系统
    original_engine = RetrievalEngine()
    enhanced_engine = EnhancedRetrievalEngine()
    
    # 测试问题
    test_questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport Schiphol located?",
        "What type of entity is Belgium?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. 问题: {question}")
        print("-" * 50)
        
        try:
            # 原始系统结果
            original_result = original_engine.retrieve_and_rewrite(question, n_results=3)
            
            # 增强系统结果
            enhanced_result = enhanced_engine.retrieve_and_rewrite(question, n_results=3, use_reranking=True)
            
            print("📊 原始系统:")
            print(f"   答案: {original_result['final_answer']}")
            print("   Top-3检索结果:")
            for j, item in enumerate(original_result['retrieved_items'][:3], 1):
                similarity = 1 - item['distance']
                print(f"     {j}. {item['triple']} (相似度: {similarity:.4f})")
            
            print("\n🚀 增强系统:")
            print(f"   答案: {enhanced_result['final_answer']}")
            print("   Top-3检索结果:")
            for j, item in enumerate(enhanced_result['retrieved_items'][:3], 1):
                similarity = 1 - item['distance']
                rerank_score = item.get('rerank_score', 'N/A')
                print(f"     {j}. {item['triple']}")
                print(f"        相似度: {similarity:.4f}, 重排分数: {rerank_score}")
                
                # 显示详细分数
                if 'detailed_scores' in item:
                    scores = item['detailed_scores']
                    print(f"        详细分数: 实体匹配={scores.get('entity_match', 0):.3f}, "
                          f"关系匹配={scores.get('relation_match', 0):.3f}, "
                          f"类型匹配={scores.get('type_match', 0):.3f}")
            
        except Exception as e:
            print(f"❌ 处理问题时出错: {e}")

def demo_answer_quality_comparison():
    """演示答案质量对比"""
    print(f"\n💡 演示答案质量对比")
    print("=" * 60)
    
    # 初始化系统
    original_engine = RetrievalEngine()
    enhanced_engine = EnhancedRetrievalEngine()
    
    # 测试用例：已知正确答案的问题
    test_cases = [
        {
            'question': "Who is the leader of Belgium?",
            'expected_keywords': ['philippe', 'king', 'belgium'],
            'description': '比利时领导人问题'
        },
        {
            'question': "Where is Amsterdam Airport Schiphol located?",
            'expected_keywords': ['netherlands', 'amsterdam', 'holland'],
            'description': '机场位置问题'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case['question']
        expected_keywords = test_case['expected_keywords']
        description = test_case['description']
        
        print(f"\n{i}. {description}")
        print(f"   问题: {question}")
        print(f"   期望关键词: {expected_keywords}")
        
        try:
            # 获取两个系统的答案
            original_result = original_engine.retrieve_and_rewrite(question)
            enhanced_result = enhanced_engine.retrieve_and_rewrite(question, use_reranking=True)
            
            original_answer = original_result['final_answer'].lower()
            enhanced_answer = enhanced_result['final_answer'].lower()
            
            print(f"\n   原始系统答案: \"{original_result['final_answer']}\"")
            print(f"   增强系统答案: \"{enhanced_result['final_answer']}\"")
            
            # 评估答案质量
            original_score = sum(1 for keyword in expected_keywords if keyword in original_answer)
            enhanced_score = sum(1 for keyword in expected_keywords if keyword in enhanced_answer)
            
            print(f"\n   答案质量评分:")
            print(f"     原始系统: {original_score}/{len(expected_keywords)} 个关键词匹配")
            print(f"     增强系统: {enhanced_score}/{len(expected_keywords)} 个关键词匹配")
            
            if enhanced_score > original_score:
                print(f"     ✅ 增强系统表现更好")
            elif enhanced_score == original_score:
                print(f"     ➖ 两系统表现相当")
            else:
                print(f"     ❌ 原始系统表现更好")
                
        except Exception as e:
            print(f"   ❌ 处理时出错: {e}")

def demo_system_statistics():
    """演示系统统计信息"""
    print(f"\n📊 系统统计信息对比")
    print("=" * 60)
    
    try:
        # 原始系统状态
        original_engine = RetrievalEngine()
        original_status = original_engine.get_system_status()
        
        # 增强系统状态
        enhanced_engine = EnhancedRetrievalEngine()
        enhanced_status = enhanced_engine.get_system_status()
        
        print("🔧 原始系统:")
        print(f"   系统名称: {original_status['system_name']}")
        print(f"   数据库文档数: {original_status['database_status']['total_documents']}")
        print(f"   组件: {list(original_status['components'].keys())}")
        
        print("\n🚀 增强系统:")
        print(f"   系统名称: {enhanced_status['system_name']}")
        print(f"   数据库文档数: {enhanced_status['database_status']['total_documents']}")
        print(f"   组件: {list(enhanced_status['components'].keys())}")
        print(f"   增强功能: {enhanced_status['components']['enhancements']}")
        
    except Exception as e:
        print(f"❌ 获取系统状态时出错: {e}")

def main():
    """主演示函数"""
    print("🎯 增强RAG系统演示")
    print("🔄 主要改进:")
    print("   1. 更自然的三元组嵌入模板")
    print("   2. 丰富的元数据信息")
    print("   3. 多阶段检索重排")
    print("   4. 多信号相关性评分")
    print("=" * 70)
    
    # 运行各个演示
    demo_embedding_improvements()
    demo_multi_stage_retrieval()
    demo_answer_quality_comparison()
    demo_system_statistics()
    
    print(f"\n🎉 演示完成！")
    print(f"\n💡 下一步:")
    print(f"   - 运行 python retrieval_evaluation_system.py 进行全面评估")
    print(f"   - 查看详细的Precision@K, Recall@K, nDCG@K指标")
    print(f"   - 分析100个问题的系统性能对比")

if __name__ == '__main__':
    main()