#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试基于三元组的相关性判断
"""

from rag_vs_llm_evaluation import RAGvsLLMEvaluator
from test_reranking_methods import RerankingMethodComparator

def test_triple_based_relevance():
    """测试基于三元组的相关性判断"""
    print("🔄 测试基于三元组的相关性判断")
    print("=" * 60)
    
    try:
        # 测试RAG vs LLM评估器
        print("1️⃣ 测试RAG vs LLM评估器的三元组相关性判断")
        evaluator = RAGvsLLMEvaluator()
        
        # 创建测试数据
        test_qa_item = {
            'question': 'Which airport has a runway named "7/25"?',
            'expected_answer': 'Alpena County Regional Airport',
            'triple': ['Alpena_County_Regional_Airport', 'runwayName', '7/25'],
            'question_type': 'sub',
            'source_file': 'test'
        }
        
        print(f"   问题: {test_qa_item['question']}")
        print(f"   原始三元组: {test_qa_item['triple']}")
        
        # 测试单个问题评估
        result = evaluator.evaluate_single_question(test_qa_item)
        
        print(f"   ✅ RAG答案: {result['rag_answer'][:50]}...")
        print(f"   📊 RAG综合分数: {result['rag_scores']['composite_score']:.4f}")
        
        # 检查检索指标
        if result.get('rag_retrieval_metrics'):
            print(f"   🎯 检索指标 (基于三元组相关性):")
            for metric, score in result['rag_retrieval_metrics'].items():
                if 'precision@' in metric or 'recall@' in metric:
                    print(f"      {metric}: {score:.4f}")
        
        print("\n" + "-" * 40)
        
        # 测试重排方法对比器
        print("2️⃣ 测试重排方法对比器的三元组相关性判断")
        comparator = RerankingMethodComparator()
        
        # 加载一些测试问题
        test_questions = comparator.load_qa_questions(max_questions=3)
        
        if test_questions:
            print(f"   加载了 {len(test_questions)} 个测试问题")
            
            # 测试第一个问题
            first_qa = test_questions[0]
            print(f"   测试问题: {first_qa['question']}")
            print(f"   原始三元组: {first_qa.get('triple', 'None')}")
            
            # 运行对比测试
            original_triple = first_qa.get('triple', None)
            result = comparator.test_single_question(
                first_qa['question'], 
                first_qa['answer'], 
                original_triple
            )
            
            print(f"   ✅ 测试完成")
            print(f"   📊 原有方法 Precision@1: {result['original_method']['precision']['precision@1']:.4f}")
            print(f"   📊 Cross-Encoder Precision@1: {result['cross_encoder_method']['precision']['precision@1']:.4f}")
        
        print(f"\n✅ 基于三元组的相关性判断测试完成!")
        print("🔧 改进说明:")
        print("   - 如果检索到的三元组与原始三元组完全匹配 → 完全相关 (1.0)")
        print("   - 如果检索到的三元组有2项与原始三元组匹配 → 部分相关 (0.6)")
        print("   - 否则 → 不相关 (0.0)")
        print("   - 如果没有原始三元组信息，回退到基于文本的相关性判断")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_triple_based_relevance()