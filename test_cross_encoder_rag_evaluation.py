#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试使用Cross-Encoder重排的RAG vs LLM评估
"""

from rag_vs_llm_evaluation import RAGvsLLMEvaluator

def test_cross_encoder_rag_evaluation():
    """测试Cross-Encoder重排的RAG评估"""
    print("🔄 测试使用Cross-Encoder重排的RAG vs LLM评估")
    print("=" * 60)
    
    try:
        # 初始化评估器
        evaluator = RAGvsLLMEvaluator()
        
        # 创建测试问题
        test_questions = [
            {
                'question': '什么是人工智能？',
                'expected_answer': '人工智能',
                'question_type': 'definition',
                'source_file': 'test'
            },
            {
                'question': '机器学习的主要类型有哪些？',
                'expected_answer': '监督学习、无监督学习、强化学习',
                'question_type': 'enumeration',
                'source_file': 'test'
            }
        ]
        
        print(f"📊 测试问题数量: {len(test_questions)}")
        print("🎯 使用Cross-Encoder重排方法")
        print("-" * 40)
        
        # 测试单个问题评估
        for i, qa_item in enumerate(test_questions, 1):
            print(f"\n🔍 测试问题 {i}: {qa_item['question']}")
            
            try:
                result = evaluator.evaluate_single_question(qa_item)
                
                print(f"   ✅ RAG答案: {result['rag_answer'][:50]}...")
                print(f"   📊 RAG综合分数: {result['rag_scores']['composite_score']:.4f}")
                
                # 检查是否有检索指标
                if result.get('rag_retrieval_metrics'):
                    print(f"   🎯 检索指标:")
                    for metric, score in result['rag_retrieval_metrics'].items():
                        if 'precision@' in metric or 'recall@' in metric:
                            print(f"      {metric}: {score:.4f}")
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        print(f"\n✅ Cross-Encoder重排的RAG评估测试完成!")
        print("🔧 修改说明:")
        print("   - enhanced_retrieval_engine.py 中的 retrieve_and_rewrite 方法")
        print("   - 已将重排方法改为 rerank_method='cross_encoder'")
        print("   - 其他流程保持不变")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cross_encoder_rag_evaluation()