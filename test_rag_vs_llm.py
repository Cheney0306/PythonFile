# test_rag_vs_llm.py - 测试RAG vs LLM评估系统

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rag_vs_llm_evaluation import RAGvsLLMEvaluator

def test_single_question():
    """测试单个问题的评估"""
    print("🧪 测试单个问题评估")
    print("=" * 40)
    
    evaluator = RAGvsLLMEvaluator()
    
    # 测试问题
    test_qa = {
        'question': 'Who is the leader of Belgium?',
        'expected_answer': 'Philippe of Belgium',
        'question_type': 'sub',
        'source_file': 'test'
    }
    
    print(f"📝 测试问题: {test_qa['question']}")
    print(f"📋 期望答案: {test_qa['expected_answer']}")
    
    # 评估单个问题
    result = evaluator.evaluate_single_question(test_qa)
    
    print(f"\n🔍 评估结果:")
    print(f"RAG答案: {result['rag_answer']}")
    print(f"LLM答案: {result['llm_answer']}")
    
    print(f"\n📊 RAG分数:")
    for metric, score in result['rag_scores'].items():
        print(f"  {metric}: {score:.4f}")
    
    print(f"\n📊 LLM分数:")
    for metric, score in result['llm_scores'].items():
        print(f"  {metric}: {score:.4f}")
    
    print("\n" + "=" * 40)
    print("🎯 单个问题测试完成！")

def test_answer_similarity():
    """测试答案相似度评估"""
    print("\n🧪 测试答案相似度评估")
    print("=" * 40)
    
    evaluator = RAGvsLLMEvaluator()
    
    test_cases = [
        ("Philippe of Belgium", "Philippe of Belgium"),  # 精确匹配
        ("King Philippe", "Philippe of Belgium"),        # 部分匹配
        ("Belgium's leader is Philippe", "Philippe of Belgium"),  # 包含匹配
        ("Charles Michel", "Philippe of Belgium"),       # 不匹配
        ("Unknown", "Philippe of Belgium")               # 完全不匹配
    ]
    
    for predicted, expected in test_cases:
        scores = evaluator.evaluate_answer_similarity(predicted, expected)
        print(f"\n预测: '{predicted}' vs 期望: '{expected}'")
        print(f"  精确匹配: {scores['exact_match']:.2f}")
        print(f"  包含匹配: {scores['contains_match']:.2f}")
        print(f"  词汇重叠: {scores['word_overlap']:.2f}")
        print(f"  综合分数: {scores['composite_score']:.2f}")

def show_usage_examples():
    """显示使用示例"""
    print("\n💡 RAG vs LLM评估使用示例:")
    print("=" * 40)
    print("1. 快速评估（20个问题）:")
    print("   python rag_vs_llm_evaluation.py --mode quick")
    print()
    print("2. 快速评估（自定义数量）:")
    print("   python rag_vs_llm_evaluation.py --mode quick --sample-size 50")
    print()
    print("3. 完整评估（所有问题）:")
    print("   python rag_vs_llm_evaluation.py --mode full")
    print()
    print("4. 指定数据集路径:")
    print("   python rag_vs_llm_evaluation.py --mode quick --qa-path custom_qa_datasets")
    print("=" * 40)

if __name__ == "__main__":
    # 显示使用示例
    show_usage_examples()
    
    # 测试答案相似度评估
    test_answer_similarity()
    
    # 测试单个问题评估（需要API密钥）
    try:
        test_single_question()
    except Exception as e:
        print(f"\n⚠️ 单个问题测试跳过: {e}")
        print("💡 请确保设置了OpenAI API密钥以进行完整测试")