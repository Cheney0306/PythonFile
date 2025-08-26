# test_modified_qa_generator.py - 测试修改后的QA生成器

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from text_based_qa_generator import TextBasedQAGenerator

def test_modified_qa_generation():
    """测试修改后的QA生成流程"""
    print("🧪 测试修改后的QA生成器")
    print("🎯 新流程: 每种问题类型单独调用RAG系统")
    print("=" * 60)
    
    generator = TextBasedQAGenerator()
    
    # 模拟一个文本项目
    test_text_item = {
        'id': 'test_001',
        'text': 'Amsterdam Airport Schiphol is located in the Netherlands and has a runway length of 3800 meters.',
        'triple': ('Amsterdam_Airport_Schiphol', 'location', 'Netherlands'),
        'schema': ('Airport', 'location', 'Country'),
        'source_file': 'test.xml'
    }
    
    print(f"📋 测试文本项目:")
    print(f"   ID: {test_text_item['id']}")
    print(f"   文本: {test_text_item['text']}")
    print(f"   三元组: {test_text_item['triple']}")
    print(f"   Schema: {test_text_item['schema']}")
    
    # 测试QA生成
    print(f"\n🔄 开始生成QA对...")
    print(f"   每种问题类型将单独调用RAG系统")
    
    try:
        qa_pairs = generator.generate_qa_from_text_via_rag(test_text_item)
        
        if qa_pairs:
            print(f"\n✅ 成功生成 {len(qa_pairs)} 个QA对")
            
            for i, qa in enumerate(qa_pairs, 1):
                print(f"\n{i}. 问题类型: {qa.get('question_type', 'N/A')}")
                print(f"   问题: {qa.get('question', 'N/A')}")
                print(f"   答案: {qa.get('answer', 'N/A')}")
                print(f"   生成方法: {qa.get('generation_method', 'N/A')}")
                
                # 显示RAG相关信息
                if 'rag_context' in qa:
                    print(f"   RAG上下文: {qa['rag_context'][:100]}...")
                if 'rag_answer' in qa:
                    print(f"   RAG答案: {qa['rag_answer']}")
                
                print(f"   时间戳: {qa.get('timestamp', 'N/A')}")
                print("-" * 40)
                
        else:
            print("❌ QA生成失败")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def test_retrieval_engine_with_prompt_type():
    """测试检索引擎的prompt_type参数"""
    print("\n🔍 测试检索引擎的prompt_type参数")
    print("=" * 50)
    
    from retrieval_engine import RetrievalEngine
    
    engine = RetrievalEngine()
    test_text = "Amsterdam Airport Schiphol is located in the Netherlands."
    
    # 测试四种问题类型
    prompt_types = ['sub', 'obj', 'rel', 'type']
    
    for prompt_type in prompt_types:
        print(f"\n🏷 测试问题类型: {prompt_type}")
        
        try:
            result = engine.retrieve_and_rewrite(test_text, prompt_type=prompt_type)
            
            print(f"   问题类型: {result['retrieval_stats']['question_type']}")
            print(f"   检索数量: {result['retrieval_stats']['num_retrieved']}")
            print(f"   CoTKR知识: {result['cotkr_knowledge'][:100]}...")
            print(f"   最终答案: {result['final_answer']}")
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print("-" * 30)

def test_cotkr_rewriter_with_prompt_type():
    """测试CoTKR重写器的prompt_type参数"""
    print("\n🧠 测试CoTKR重写器的prompt_type参数")
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
    prompt_types = ['sub', 'obj', 'rel', 'type']
    
    for prompt_type in prompt_types:
        print(f"\n🏷 测试问题类型: {prompt_type}")
        
        try:
            # 测试知识重写
            rewritten = rewriter.rewrite_knowledge(mock_items, test_text, prompt_type)
            print(f"   重写知识: {rewritten[:100]}...")
            
            # 测试答案提取
            answer = rewriter.extract_answer_from_knowledge(test_text, rewritten, mock_items, prompt_type)
            print(f"   提取答案: {answer}")
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print("-" * 30)

if __name__ == '__main__':
    # 运行所有测试
    test_modified_qa_generation()
    test_retrieval_engine_with_prompt_type()
    test_cotkr_rewriter_with_prompt_type()
    
    print("\n🎉 所有测试完成！")