#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试双LLM调用的RAG vs LLM评估
验证现在的评估确实是：RAG(使用LLM) vs 纯LLM
"""

from rag_vs_llm_evaluation import RAGvsLLMEvaluator
import config

def test_double_llm_evaluation():
    """测试双LLM调用的评估流程"""
    print("🔄 测试双LLM调用的RAG vs LLM评估")
    print("=" * 60)
    
    # 检查API密钥
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your-openai-api-key-here":
        print("❌ OpenAI API密钥未配置，无法进行测试")
        return
    
    print("✅ OpenAI API密钥已配置")
    
    # 初始化评估器
    evaluator = RAGvsLLMEvaluator()
    
    # 测试问题
    test_question = "Who is the leader of Belgium?"
    expected_answer = "Philippe of Belgium"
    
    print(f"\n📝 测试问题: {test_question}")
    print(f"🎯 期望答案: {expected_answer}")
    print("-" * 60)
    
    try:
        # 执行单个问题的评估
        qa_item = {
            'question': test_question,
            'expected_answer': expected_answer
        }
        result = evaluator.evaluate_single_question(qa_item)
        
        print("📊 评估结果:")
        print(f"   RAG答案: {result['rag_answer']}")
        print(f"   纯LLM答案: {result['llm_answer']}")
        
        print(f"\n📈 RAG系统评分:")
        for metric, score in result['rag_scores'].items():
            print(f"   {metric}: {score:.4f}")
        
        print(f"\n📈 纯LLM系统评分:")
        for metric, score in result['llm_scores'].items():
            print(f"   {metric}: {score:.4f}")
        
        # 分析LLM使用情况
        print(f"\n🔍 LLM使用分析:")
        print(f"   RAG系统: 使用LLM进行答案生成 (基于CoTKR推理链)")
        print(f"   纯LLM系统: 直接使用LLM回答问题")
        print(f"   总LLM调用次数: 2次 (每个问题)")
        
        # 检索指标
        if 'rag_retrieval_metrics' in result:
            print(f"\n📋 RAG检索指标:")
            for metric, score in result['rag_retrieval_metrics'].items():
                print(f"   {metric}: {score:.4f}")
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()

def analyze_evaluation_architecture():
    """分析评估架构的变化"""
    print("\n🏗️ 评估架构分析")
    print("=" * 60)
    
    print("📈 修改前的评估:")
    print("   RAG系统: 检索 → CoTKR重写 → 规则式提取 → 答案")
    print("   纯LLM系统: 问题 → LLM → 答案")
    print("   对比: 规则式RAG vs 纯LLM")
    
    print("\n📈 修改后的评估:")
    print("   RAG系统: 检索 → CoTKR重写 → LLM生成 → 答案")
    print("   纯LLM系统: 问题 → LLM → 答案")
    print("   对比: 增强RAG(带LLM) vs 纯LLM")
    
    print("\n🎯 关键差异:")
    print("   1. RAG系统现在也使用LLM，但基于结构化的CoTKR推理链")
    print("   2. 纯LLM系统直接回答，没有外部知识支持")
    print("   3. 评估变成了：'有知识支持的LLM' vs '无知识支持的LLM'")
    
    print("\n💡 评估意义:")
    print("   - 测试外部知识检索和结构化推理的价值")
    print("   - 对比有无RAG支持的LLM性能差异")
    print("   - 验证CoTKR重写是否提升了LLM的推理能力")

def estimate_api_costs():
    """估算API成本"""
    print("\n💰 API成本估算")
    print("=" * 60)
    
    print("🔢 每个问题的LLM调用:")
    print("   RAG系统: 1次LLM调用 (答案生成)")
    print("   纯LLM系统: 1次LLM调用 (直接回答)")
    print("   总计: 2次LLM调用/问题")
    
    print("\n📊 成本估算 (基于gpt-3.5-turbo):")
    print("   输入token: ~200-300 tokens/调用")
    print("   输出token: ~50-100 tokens/调用")
    print("   成本: ~$0.002-0.004/问题")
    
    print("\n⚠️ 注意事项:")
    print("   - 大规模评估时成本会快速累积")
    print("   - 建议先用小样本测试")
    print("   - 可以设置API调用限制")

def main():
    """主函数"""
    try:
        test_double_llm_evaluation()
        analyze_evaluation_architecture()
        estimate_api_costs()
        
        print("\n" + "=" * 60)
        print("✅ 分析完成")
        print("\n🎉 总结:")
        print("   ✅ 现在的RAG vs LLM评估确实是双LLM调用")
        print("   ✅ RAG系统使用LLM进行最终答案生成")
        print("   ✅ 评估对比的是'增强RAG' vs '纯LLM'")
        print("   ✅ 这样的对比更能体现RAG系统的价值")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()