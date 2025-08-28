#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG vs LLM问答对比功能
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rag_vs_llm_evaluation import RAGvsLLMEvaluator

def test_rag_vs_llm_qa_comparison():
    """测试RAG vs LLM问答对比功能"""
    print("🧪 测试RAG vs LLM问答对比功能")
    print("=" * 50)
    
    evaluator = RAGvsLLMEvaluator()
    
    # 加载少量数据进行测试
    print("📊 加载测试数据...")
    questions = evaluator.load_qa_dataset(limit=3)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    print(f"✅ 加载了 {len(questions)} 个测试问题")
    
    # 运行评估
    print("\n🔄 开始RAG vs LLM评估...")
    print("⚠️ 注意: 包含LLM调用，可能需要较长时间")
    results = evaluator.evaluate_dataset(questions)
    
    # 保存结果（包括问答对比）
    print("\n💾 保存评估结果...")
    evaluator.save_evaluation_results(results)
    
    print("\n✅ 测试完成！")
    print("\n📁 生成的问答对比文件:")
    print("   - rag_vs_llm_qa_comparison_*.json (JSON格式，便于程序处理)")
    print("   - rag_vs_llm_qa_comparison_*.txt (文本格式，便于人工阅读)")
    print("   - rag_vs_llm_qa_comparison_*.csv (CSV格式，便于Excel查看)")
    
    # 显示一个示例
    if results.get('detailed_results'):
        example = results['detailed_results'][0]
        print(f"\n📝 示例问答对比:")
        print(f"问题: {example['question']}")
        print(f"期望答案: {example['expected_answer']}")
        print(f"RAG系统答案: {example['rag_answer']}")
        print(f"LLM系统答案: {example['llm_answer']}")
        
        # 显示分数对比
        rag_score = example['rag_scores']['composite_score']
        llm_score = example['llm_scores']['composite_score']
        winner = 'RAG' if rag_score > llm_score else 'LLM' if llm_score > rag_score else 'TIE'
        
        print(f"\n📊 分数对比:")
        print(f"RAG综合分数: {rag_score:.3f}")
        print(f"LLM综合分数: {llm_score:.3f}")
        print(f"胜负结果: {winner}")

def show_rag_vs_llm_comparison_features():
    """显示RAG vs LLM问答对比功能特性"""
    print("💡 RAG vs LLM问答对比功能特性:")
    print("=" * 50)
    print("📋 对比内容:")
    print("   ✓ 原始问题和期望答案")
    print("   ✓ RAG系统的答案")
    print("   ✓ 纯LLM的答案")
    print("   ✓ 详细的评分对比")
    print("   ✓ 胜负结果判定")
    print("   ✓ 分数差异计算")
    print("   ✓ 问题类型分类")
    print()
    print("📊 评估指标:")
    print("   ✓ 精确匹配 (Exact Match)")
    print("   ✓ 包含匹配 (Contains Match)")
    print("   ✓ 词汇重叠 (Word Overlap)")
    print("   ✓ 综合分数 (Composite Score)")
    print()
    print("📁 输出格式:")
    print("   ✓ JSON格式 (便于程序处理)")
    print("   ✓ TXT格式 (便于人工阅读)")
    print("   ✓ CSV格式 (便于Excel查看)")
    print()
    print("🎯 主要用途:")
    print("   ✓ 验证RAG系统的实际价值")
    print("   ✓ 量化知识检索的贡献")
    print("   ✓ 识别LLM的知识盲区")
    print("   ✓ 为系统改进提供方向")
    print("   ✓ 生成对比分析报告")
    print()
    print("🔍 新增特性:")
    print("   ✓ 自动胜负判定")
    print("   ✓ 详细分数差异")
    print("   ✓ 胜负统计汇总")
    print("   ✓ Excel友好的CSV格式")
    print("=" * 50)

def demo_file_formats():
    """演示不同文件格式的特点"""
    print("\n📄 文件格式说明:")
    print("-" * 30)
    print("1. JSON格式 (rag_vs_llm_qa_comparison_*.json):")
    print("   - 结构化数据，便于程序处理")
    print("   - 包含完整的评分信息")
    print("   - 支持进一步的数据分析")
    print()
    print("2. TXT格式 (rag_vs_llm_qa_comparison_*.txt):")
    print("   - 人类友好的可读格式")
    print("   - 包含胜负统计汇总")
    print("   - 清晰的分段显示")
    print("   - 详细的分数差异计算")
    print()
    print("3. CSV格式 (rag_vs_llm_qa_comparison_*.csv):")
    print("   - Excel兼容格式")
    print("   - 便于制作对比图表")
    print("   - 支持排序和筛选")
    print("   - UTF-8-BOM编码，中文显示正常")
    print("   - 包含所有评分指标的详细对比")

if __name__ == "__main__":
    # 显示功能特性
    show_rag_vs_llm_comparison_features()
    
    # 演示文件格式
    demo_file_formats()
    
    # 运行测试
    try:
        test_rag_vs_llm_qa_comparison()
    except Exception as e:
        print(f"\n⚠️ 测试失败: {e}")
        print("💡 请确保:")
        print("   - 增强数据库已初始化")
        print("   - 有可用的QA数据集")
        print("   - OpenAI API密钥已设置（用于LLM调用）")
        import traceback
        traceback.print_exc()