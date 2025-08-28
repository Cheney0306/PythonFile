# test_enhanced_qa_generation.py - 测试增强QA生成流程

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from enhanced_qa_generator import EnhancedQAGenerator

def test_enhanced_qa_flow():
    """测试增强QA生成流程"""
    print("🧪 测试增强QA生成流程")
    print("=" * 60)
    
    # 初始化生成器
    generator = EnhancedQAGenerator()
    
    # 测试文本
    test_text = "Belgium's leader is King Philippe. The country is located in Western Europe and has Brussels as its capital."
    
    print(f"📝 测试文本: {test_text}")
    print()
    
    # 测试检索功能
    print("🔍 步骤1: 增强检索（跳过重写）")
    retrieved_results = generator._enhanced_retrieve_for_qa(test_text)
    
    if retrieved_results:
        print(f"✅ 检索到 {len(retrieved_results)} 个相关三元组:")
        for i, result in enumerate(retrieved_results[:3], 1):
            print(f"   {i}. 三元组: {result['triple']}")
            print(f"      Schema: {result.get('schema', 'N/A')}")
            print(f"      距离: {result['distance']:.4f}")
        print()
    else:
        print("❌ 未检索到相关三元组")
        return
    
    # 测试One-shot示例
    print("📋 步骤2: One-shot示例测试")
    question_types = ['sub', 'obj', 'rel', 'type']
    
    for q_type in question_types:
        example = generator._get_one_shot_example(q_type)
        print(f"\n🏷 {q_type.upper()} 类型示例:")
        print(example[:200] + "...")
    
    print()
    
    # 测试prompt构造
    print("💬 步骤3: Prompt构造测试")
    if retrieved_results:
        result = retrieved_results[0]
        triple = result['triple']
        schema = result.get('schema')
        
        for q_type in ['obj', 'rel']:  # 测试两种类型
            prompt = generator._construct_enhanced_prompt(triple, schema, q_type, test_text)
            print(f"\n🏷 {q_type.upper()} 类型Prompt:")
            print(prompt[:300] + "...")
    
    print()
    
    # 测试完整QA生成流程
    print("🚀 步骤4: 完整QA生成测试")
    qa_pairs = generator._generate_qa_from_text(test_text, "test_001")
    
    if qa_pairs:
        print(f"✅ 生成了 {len(qa_pairs)} 个QA对:")
        for i, qa in enumerate(qa_pairs, 1):
            print(f"\n{i}. 问题类型: {qa['question_type']}")
            print(f"   问题: {qa['question']}")
            print(f"   答案: {qa['answer']}")
            print(f"   三元组: {qa['triple']}")
            print(f"   生成方法: {qa['generation_method']}")
    else:
        print("❌ 未生成QA对")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成！")

def test_question_type_examples():
    """测试不同问题类型的示例"""
    print("\n🔍 测试问题类型示例")
    print("=" * 40)
    
    generator = EnhancedQAGenerator()
    
    question_types = {
        'rel': '关系提问',
        'sub': '主语提问', 
        'obj': '宾语提问',
        'type': '类型提问'
    }
    
    for q_type, description in question_types.items():
        print(f"\n📋 {description} ({q_type}):")
        example = generator._get_one_shot_example(q_type)
        print(example)

if __name__ == "__main__":
    # 测试问题类型示例
    test_question_type_examples()
    
    # 测试完整流程
    test_enhanced_qa_flow()