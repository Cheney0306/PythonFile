#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试LLM增强的答案提取功能
验证修改后的extract_answer_from_knowledge方法
"""

from cotkr_rewriter import CoTKRRewriter
import config

def test_llm_enhanced_extraction():
    """测试LLM增强的答案提取"""
    print("🧪 测试LLM增强的答案提取功能")
    print("=" * 50)
    
    # 检查API密钥配置
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your-openai-api-key-here":
        print("⚠️ OpenAI API密钥未配置，将使用回退方案")
    else:
        print("✅ OpenAI API密钥已配置")
    
    # 初始化重写器
    rewriter = CoTKRRewriter()
    
    # 模拟检索结果
    mock_items = [
        {
            'triple': ('Belgium', 'leader', 'Philippe_of_Belgium'),
            'schema': ('Country', 'leader', 'Royalty'),
            'distance': 0.25,
            'text': 'Belgium is led by Philippe of Belgium.'
        },
        {
            'triple': ('Belgium', 'capital', 'Brussels'),
            'schema': ('Country', 'capital', 'CapitalCity'),
            'distance': 0.31,
            'text': 'Belgium has Brussels as its capital.'
        }
    ]
    
    # 测试问题
    test_cases = [
        {
            'question': 'Who is the leader of Belgium?',
            'prompt_type': 'sub',
            'expected_keywords': ['Philippe', 'Belgium']
        },
        {
            'question': 'Where is the capital of Belgium?',
            'prompt_type': 'obj', 
            'expected_keywords': ['Brussels']
        },
        {
            'question': 'What type of entity is Belgium?',
            'prompt_type': 'type',
            'expected_keywords': ['Country']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {test_case['question']}")
        print("-" * 40)
        
        try:
            # 1. 生成CoTKR知识
            cotkr_knowledge = rewriter.rewrite_knowledge(
                mock_items, 
                test_case['question'], 
                test_case['prompt_type']
            )
            
            print("🧠 CoTKR重写知识:")
            print(cotkr_knowledge[:200] + "..." if len(cotkr_knowledge) > 200 else cotkr_knowledge)
            
            # 2. 使用新的LLM增强提取方法
            final_answer = rewriter.extract_answer_from_knowledge(
                test_case['question'],
                cotkr_knowledge,
                mock_items,
                test_case['prompt_type']
            )
            
            print(f"\n💡 LLM生成答案: {final_answer}")
            
            # 3. 简单的答案质量检查
            answer_lower = final_answer.lower()
            keywords_found = [kw for kw in test_case['expected_keywords'] 
                            if kw.lower() in answer_lower]
            
            if keywords_found:
                print(f"✅ 答案质量检查通过 (包含关键词: {keywords_found})")
            else:
                print(f"⚠️ 答案质量需要检查 (期望关键词: {test_case['expected_keywords']})")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

def compare_old_vs_new_method():
    """对比旧方法和新方法的效果"""
    print("\n🔄 对比旧方法 vs 新方法")
    print("=" * 50)
    
    rewriter = CoTKRRewriter()
    
    mock_items = [
        {
            'triple': ('Belgium', 'leader', 'Philippe_of_Belgium'),
            'schema': ('Country', 'leader', 'Royalty'),
            'distance': 0.25
        }
    ]
    
    question = "Who is the leader of Belgium?"
    
    # 生成CoTKR知识
    cotkr_knowledge = rewriter.rewrite_knowledge(mock_items, question, 'sub')
    
    print(f"📝 问题: {question}")
    print(f"🧠 CoTKR知识: {cotkr_knowledge[:150]}...")
    
    # 新方法（LLM增强）
    try:
        new_answer = rewriter.extract_answer_from_knowledge(
            question, cotkr_knowledge, mock_items, 'sub'
        )
        print(f"\n🚀 新方法 (LLM增强): {new_answer}")
    except Exception as e:
        print(f"❌ 新方法失败: {e}")
    
    # 回退方法（规则式）
    try:
        fallback_answer = rewriter._fallback_extraction(question, mock_items, 'sub')
        print(f"🔧 回退方法 (规则式): {fallback_answer}")
    except Exception as e:
        print(f"❌ 回退方法失败: {e}")

def main():
    """主函数"""
    try:
        test_llm_enhanced_extraction()
        compare_old_vs_new_method()
        
        print("\n" + "=" * 50)
        print("✅ 测试完成")
        print("\n💡 关键改进:")
        print("   1. 答案提取现在使用LLM生成，更自然流畅")
        print("   2. 基于CoTKR思维链进行推理，答案更准确")
        print("   3. 提供回退方案，确保系统稳定性")
        print("   4. 支持API密钥未配置的情况")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()