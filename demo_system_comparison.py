#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示原始系统与增强系统的技术差异
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from retrieval_engine import RetrievalEngine
from enhanced_retrieval_engine import EnhancedRetrievalEngine

def demo_retrieval_comparison():
    """演示检索系统对比"""
    print("🔍 检索系统技术对比演示")
    print("=" * 60)
    
    # 初始化两个系统
    print("🔧 初始化系统...")
    original_engine = RetrievalEngine()
    enhanced_engine = EnhancedRetrievalEngine()
    
    # 测试问题
    test_questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport located?",
        "What is the relationship between Amsterdam Airport and Haarlemmermeer?",
        "What type of entity is Belgium?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试问题 {i}: {question}")
        print("-" * 60)
        
        # 原始系统检索
        print("🔵 原始系统 (单阶段检索 + CoTKR重写):")
        original_result = original_engine.retrieve_and_rewrite(question, n_results=3)
        print(f"   检索方法: 单阶段向量检索")
        print(f"   检索数量: {original_result['retrieval_stats']['num_retrieved']}")
        print(f"   平均距离: {original_result['retrieval_stats']['avg_distance']:.4f}")
        print(f"   问题类型: {original_result['retrieval_stats']['question_type']}")
        print(f"   重写功能: ✅ CoTKR重写")
        print(f"   重排算法: ❌ 无")
        print(f"   最终答案: {original_result['final_answer']}")
        
        # 增强系统检索（启用重排）
        print("\n🟢 增强系统 (多阶段检索 + 重排 + CoTKR重写):")
        enhanced_result = enhanced_engine.retrieve_and_rewrite(question, n_results=3, use_reranking=True)
        print(f"   检索方法: {enhanced_result['retrieval_stats']['retrieval_method']}")
        print(f"   检索数量: {enhanced_result['retrieval_stats']['num_retrieved']}")
        print(f"   平均距离: {enhanced_result['retrieval_stats']['avg_distance']:.4f}")
        print(f"   问题类型: {enhanced_result['retrieval_stats']['question_type']}")
        print(f"   重写功能: ✅ CoTKR重写")
        print(f"   重排算法: ✅ 多信号重排")
        if 'avg_rerank_score' in enhanced_result['retrieval_stats']:
            print(f"   平均重排分数: {enhanced_result['retrieval_stats']['avg_rerank_score']:.4f}")
        print(f"   最终答案: {enhanced_result['final_answer']}")
        
        # 增强系统检索（禁用重排，等同于原始系统）
        print("\n🟡 增强系统 (禁用重排，等同于原始系统):")
        enhanced_basic = enhanced_engine.retrieve_and_rewrite(question, n_results=3, use_reranking=False)
        print(f"   检索方法: {enhanced_basic['retrieval_stats']['retrieval_method']}")
        print(f"   检索数量: {enhanced_basic['retrieval_stats']['num_retrieved']}")
        print(f"   平均距离: {enhanced_basic['retrieval_stats']['avg_distance']:.4f}")
        print(f"   重写功能: ✅ CoTKR重写")
        print(f"   重排算法: ❌ 禁用")
        print(f"   最终答案: {enhanced_basic['final_answer']}")
        
        print("\n" + "=" * 60)

def demo_cotkr_rewriting():
    """演示CoTKR重写功能"""
    print("\n🧠 CoTKR重写功能演示")
    print("=" * 60)
    
    enhanced_engine = EnhancedRetrievalEngine()
    
    # 四种问题类型示例
    question_types = [
        ("Who is the leader of Belgium?", "sub", "Subject类型 - 询问主语实体"),
        ("Where is Amsterdam Airport located?", "obj", "Object类型 - 询问宾语实体"),
        ("What is the relationship between Amsterdam Airport and Haarlemmermeer?", "rel", "Relationship类型 - 询问关系"),
        ("What type of entity is Belgium?", "type", "Type类型 - 询问实体类型")
    ]
    
    for question, prompt_type, description in question_types:
        print(f"\n📝 {description}")
        print(f"问题: {question}")
        print(f"类型: {prompt_type}")
        print("-" * 40)
        
        # 获取重写结果
        result = enhanced_engine.retrieve_and_rewrite(question, n_results=2, prompt_type=prompt_type)
        
        print("🔄 CoTKR重写输出:")
        cotkr_lines = result['cotkr_knowledge'].split('\\n')
        for line in cotkr_lines:
            if line.strip():
                print(f"   {line}")
        
        print(f"\n✅ 最终答案: {result['final_answer']}")
        print("-" * 40)

def demo_reranking_details():
    """演示重排算法详细信息"""
    print("\n🎯 重排算法详细演示")
    print("=" * 60)
    
    enhanced_engine = EnhancedRetrievalEngine()
    
    question = "Who is the leader of Belgium?"
    print(f"📝 测试问题: {question}")
    
    # 获取详细的检索结果
    result = enhanced_engine.retrieve_and_rewrite(question, n_results=3, use_reranking=True)
    
    print("\\n🔍 检索结果详细分析:")
    for i, item in enumerate(result['retrieved_items'], 1):
        print(f"\\n结果 {i}:")
        print(f"   三元组: {item['triple']}")
        print(f"   模式: {item['schema']}")
        print(f"   向量距离: {item['distance']:.4f}")
        
        if 'rerank_score' in item:
            print(f"   重排分数: {item['rerank_score']:.4f}")
            
            if 'detailed_scores' in item:
                scores = item['detailed_scores']
                print(f"   详细分数:")
                print(f"     - 实体匹配: {scores.get('entity_match', 0):.3f}")
                print(f"     - 关系匹配: {scores.get('relation_match', 0):.3f}")
                print(f"     - 类型匹配: {scores.get('type_match', 0):.3f}")
                print(f"     - 语义相似度: {scores.get('semantic_similarity', 0):.3f}")

def show_system_architecture():
    """显示系统架构对比"""
    print("\\n🏗️ 系统架构对比")
    print("=" * 60)
    
    print("🔵 原始系统架构:")
    print("   用户问题 → 向量嵌入 → 向量检索 → CoTKR重写 → 答案生成")
    print("   特点:")
    print("   ✅ 简单直接")
    print("   ✅ 使用CoTKR重写")
    print("   ❌ 检索精度有限")
    print("   ❌ 无重排机制")
    
    print("\\n🟢 增强系统架构:")
    print("   用户问题 → 向量嵌入 → 第一阶段检索(扩大范围) → 第二阶段重排 → CoTKR重写 → 答案生成")
    print("   特点:")
    print("   ✅ 多阶段检索")
    print("   ✅ 使用CoTKR重写")
    print("   ✅ 多信号重排")
    print("   ✅ 可配置重排")
    
    print("\\n🎯 重排算法组成:")
    print("   1. 实体匹配分数 (30%权重) - 检查问题中提到的实体")
    print("   2. 关系匹配分数 (25%权重) - 匹配关系关键词")
    print("   3. 类型匹配分数 (20%权重) - 匹配实体类型")
    print("   4. 语义相似度分数 (25%权重) - 来自向量检索")

if __name__ == "__main__":
    try:
        # 显示系统架构
        show_system_architecture()
        
        # 演示检索对比
        demo_retrieval_comparison()
        
        # 演示CoTKR重写
        demo_cotkr_rewriting()
        
        # 演示重排详细信息
        demo_reranking_details()
        
        print("\\n✅ 演示完成！")
        print("\\n💡 总结:")
        print("   - 两个系统都使用CoTKR重写功能")
        print("   - 增强系统额外使用多阶段检索和重排算法")
        print("   - 重排算法结合4种信号：实体、关系、类型、语义相似度")
        print("   - 增强系统可以选择启用或禁用重排功能")
        
    except Exception as e:
        print(f"\\n⚠️ 演示失败: {e}")
        print("💡 请确保数据库已初始化")
        import traceback
        traceback.print_exc()