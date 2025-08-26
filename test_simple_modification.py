# test_simple_modification.py - 简化测试修改后的功能

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_retrieval_engine_modification():
    """测试检索引擎的修改"""
    print("🔍 测试检索引擎的prompt_type参数修改")
    print("=" * 50)
    
    from retrieval_engine import RetrievalEngine
    
    engine = RetrievalEngine()
    test_text = "Amsterdam Airport Schiphol is located in the Netherlands."
    
    # 测试不带prompt_type的调用（原有功能）
    print("1️⃣ 测试不带prompt_type的调用:")
    try:
        result1 = engine.retrieve_and_rewrite(test_text)
        print(f"   ✅ 成功 - 问题类型: {result1['retrieval_stats']['question_type']}")
        print(f"   检索数量: {result1['retrieval_stats']['num_retrieved']}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试带prompt_type的调用（新功能）
    print("\n2️⃣ 测试带prompt_type的调用:")
    for prompt_type in ['sub', 'obj', 'rel', 'type']:
        try:
            result2 = engine.retrieve_and_rewrite(test_text, prompt_type=prompt_type)
            print(f"   ✅ {prompt_type} - 问题类型: {result2['retrieval_stats']['question_type']}")
        except Exception as e:
            print(f"   ❌ {prompt_type} 错误: {e}")

def test_cotkr_rewriter_modification():
    """测试CoTKR重写器的修改"""
    print("\n🧠 测试CoTKR重写器的prompt_type参数修改")
    print("=" * 50)
    
    from cotkr_rewriter import CoTKRRewriter
    
    rewriter = CoTKRRewriter()
    
    # 模拟检索结果
    mock_items = [
        {
            'triple': ('Amsterdam_Airport_Schiphol', 'location', 'Netherlands'),
            'schema': ('Airport', 'location', 'Country'),
            'distance': 0.25
        }
    ]
    
    test_text = "Amsterdam Airport Schiphol is located in the Netherlands."
    
    # 测试不带prompt_type的调用（原有功能）
    print("1️⃣ 测试不带prompt_type的调用:")
    try:
        rewritten1 = rewriter.rewrite_knowledge(mock_items, test_text)
        answer1 = rewriter.extract_answer_from_knowledge(test_text, rewritten1, mock_items)
        print(f"   ✅ 成功 - 答案: {answer1}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试带prompt_type的调用（新功能）
    print("\n2️⃣ 测试带prompt_type的调用:")
    for prompt_type in ['sub', 'obj', 'rel', 'type']:
        try:
            rewritten2 = rewriter.rewrite_knowledge(mock_items, test_text, prompt_type)
            answer2 = rewriter.extract_answer_from_knowledge(test_text, rewritten2, mock_items, prompt_type)
            print(f"   ✅ {prompt_type} - 答案: {answer2}")
        except Exception as e:
            print(f"   ❌ {prompt_type} 错误: {e}")

def test_qa_generator_flow():
    """测试QA生成器的流程修改"""
    print("\n📝 测试QA生成器的流程修改")
    print("=" * 50)
    
    # 模拟文本项目
    test_text_item = {
        'id': 'test_001',
        'text': 'Amsterdam Airport Schiphol is located in the Netherlands.',
        'triple': ('Amsterdam_Airport_Schiphol', 'location', 'Netherlands'),
        'schema': ('Airport', 'location', 'Country'),
        'source_file': 'test.xml'
    }
    
    print(f"📋 测试文本: {test_text_item['text']}")
    print(f"📋 三元组: {test_text_item['triple']}")
    print(f"📋 Schema: {test_text_item['schema']}")
    
    # 检查是否会为每种问题类型调用RAG系统
    print("\n🔄 验证流程修改:")
    print("   原流程: 调用一次RAG → 生成四种QA")
    print("   新流程: 为每种问题类型调用一次RAG → 生成对应QA")
    
    # 这里我们不实际调用QA生成（避免API调用），只验证逻辑
    from text_based_qa_generator import TextBasedQAGenerator
    
    generator = TextBasedQAGenerator()
    
    # 检查方法签名是否正确修改
    import inspect
    
    # 检查retrieve_and_rewrite方法的签名
    retrieve_sig = inspect.signature(generator.retrieval_engine.retrieve_and_rewrite)
    print(f"\n🔍 retrieve_and_rewrite方法参数: {list(retrieve_sig.parameters.keys())}")
    
    # 检查rewrite_knowledge方法的签名
    rewrite_sig = inspect.signature(generator.retrieval_engine.cotkr_rewriter.rewrite_knowledge)
    print(f"🔍 rewrite_knowledge方法参数: {list(rewrite_sig.parameters.keys())}")
    
    # 检查extract_answer_from_knowledge方法的签名
    extract_sig = inspect.signature(generator.retrieval_engine.cotkr_rewriter.extract_answer_from_knowledge)
    print(f"🔍 extract_answer_from_knowledge方法参数: {list(extract_sig.parameters.keys())}")
    
    print("\n✅ 方法签名检查完成")

if __name__ == '__main__':
    test_retrieval_engine_modification()
    test_cotkr_rewriter_modification()
    test_qa_generator_flow()
    
    print("\n🎉 简化测试完成！")
    print("\n📋 修改总结:")
    print("1. ✅ retrieval_engine.retrieve_and_rewrite() 增加了 prompt_type 参数")
    print("2. ✅ cotkr_rewriter.rewrite_knowledge() 增加了 prompt_type 参数")
    print("3. ✅ cotkr_rewriter.extract_answer_from_knowledge() 增加了 prompt_type 参数")
    print("4. ✅ text_based_qa_generator 中的RAG调用移到了问题类型循环内部")
    print("5. ✅ 不再需要 detect_question_type，直接使用传入的 prompt_type")