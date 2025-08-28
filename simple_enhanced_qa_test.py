# simple_enhanced_qa_test.py - 简单的增强QA生成测试

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from enhanced_qa_generator import EnhancedQAGenerator

def simple_test():
    """简单测试增强QA生成"""
    print("🧪 简单增强QA生成测试")
    print("=" * 50)
    
    # 初始化生成器
    generator = EnhancedQAGenerator()
    
    # 测试文本
    test_text = "Belgium's leader is King Philippe. Brussels is the capital of Belgium."
    
    print(f"📝 测试文本: {test_text}")
    print()
    
    # 生成QA对
    print("🚀 生成QA对...")
    qa_pairs = generator._generate_qa_from_text(test_text, "simple_test")
    
    if qa_pairs:
        print(f"✅ 成功生成 {len(qa_pairs)} 个QA对:")
        for i, qa in enumerate(qa_pairs, 1):
            print(f"\n{i}. 问题类型: {qa['question_type']}")
            print(f"   问题: {qa['question']}")
            print(f"   答案: {qa['answer']}")
            print(f"   三元组: {qa['triple']}")
            print(f"   Schema: {qa.get('schema', 'N/A')}")
            print(f"   生成方法: {qa['generation_method']}")
            print(f"   检索距离: {qa['retrieval_distance']:.4f}")
    else:
        print("❌ 未生成QA对")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")

if __name__ == "__main__":
    simple_test()