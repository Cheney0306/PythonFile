#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的问答对比功能
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from retrieval_evaluation_system import RetrievalEvaluator

def test_enhanced_qa_comparison():
    """测试增强的问答对比功能"""
    print("🧪 测试增强的问答对比功能")
    print("=" * 50)
    
    evaluator = RetrievalEvaluator()
    
    # 加载少量数据进行测试
    print("📊 加载测试数据...")
    questions = evaluator.load_qa_dataset(limit=5)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    print(f"✅ 加载了 {len(questions)} 个测试问题")
    
    # 运行评估
    print("\n🔄 开始评估...")
    results = evaluator.evaluate_dataset(questions)
    
    # 保存结果（包括增强的问答对比）
    print("\n💾 保存评估结果...")
    evaluator.save_evaluation_results(results)
    
    print("\n✅ 测试完成！")
    print("\n📁 生成的问答对比文件:")
    print("   - qa_comparison_*.json (JSON格式，便于程序处理)")
    print("   - qa_comparison_*.txt (文本格式，便于人工阅读)")
    print("   - qa_comparison_*.csv (CSV格式，便于Excel查看)")
    
    # 显示一个示例
    if results.get('detailed_results'):
        example = results['detailed_results'][0]
        print(f"\n📝 示例问答对比:")
        print(f"问题: {example['question']}")
        print(f"期望答案: {example['expected_answer']}")
        print(f"原始系统答案: {example['original_system']['final_answer']}")
        print(f"增强系统答案: {example['enhanced_system']['final_answer']}")
        
        # 显示指标改进
        original_metrics = evaluator._get_best_metrics(example['original_system']['metrics'])
        enhanced_metrics = evaluator._get_best_metrics(example['enhanced_system']['metrics'])
        improvement = evaluator._calculate_improvement(
            example['original_system']['metrics'],
            example['enhanced_system']['metrics']
        )
        
        print(f"\n📊 指标对比:")
        print(f"原始系统最佳指标: {original_metrics}")
        print(f"增强系统最佳指标: {enhanced_metrics}")
        print(f"改进幅度: {improvement}")

def show_qa_comparison_features():
    """显示问答对比功能特性"""
    print("💡 增强的问答对比功能特性:")
    print("=" * 50)
    print("📋 保存内容:")
    print("   ✓ 原始问题和期望答案")
    print("   ✓ 两个系统的最终答案")
    print("   ✓ 两个系统的重写查询")
    print("   ✓ 详细的指标对比")
    print("   ✓ 改进幅度计算")
    print("   ✓ 问题类型分类")
    print()
    print("📁 输出格式:")
    print("   ✓ JSON格式 (便于程序处理)")
    print("   ✓ TXT格式 (便于人工阅读)")
    print("   ✓ CSV格式 (便于Excel查看)")
    print()
    print("🎯 主要用途:")
    print("   ✓ 分析系统改进效果")
    print("   ✓ 识别问题类型的表现差异")
    print("   ✓ 调试和优化系统")
    print("   ✓ 生成案例研究报告")
    print("   ✓ 快速查看答案质量对比")
    print()
    print("🔍 新增特性:")
    print("   ✓ 自动计算最佳指标")
    print("   ✓ 百分比改进显示")
    print("   ✓ 多格式输出支持")
    print("   ✓ Excel友好的CSV格式")
    print("=" * 50)

def demo_file_formats():
    """演示不同文件格式的特点"""
    print("\n📄 文件格式说明:")
    print("-" * 30)
    print("1. JSON格式 (qa_comparison_*.json):")
    print("   - 结构化数据，便于程序处理")
    print("   - 包含完整的指标信息")
    print("   - 支持进一步的数据分析")
    print()
    print("2. TXT格式 (qa_comparison_*.txt):")
    print("   - 人类友好的可读格式")
    print("   - 清晰的分段显示")
    print("   - 包含改进幅度计算")
    print()
    print("3. CSV格式 (qa_comparison_*.csv):")
    print("   - Excel兼容格式")
    print("   - 便于制作表格和图表")
    print("   - 支持排序和筛选")
    print("   - UTF-8-BOM编码，中文显示正常")

if __name__ == "__main__":
    # 显示功能特性
    show_qa_comparison_features()
    
    # 演示文件格式
    demo_file_formats()
    
    # 运行测试
    try:
        test_enhanced_qa_comparison()
    except Exception as e:
        print(f"\n⚠️ 测试失败: {e}")
        print("💡 请确保数据库已初始化并且有QA数据集")
        import traceback
        traceback.print_exc()