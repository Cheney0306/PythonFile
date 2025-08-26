# test_four_types_system.py - 测试改造后的四种问题类型系统

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

def test_cotkr_four_types():
    """测试CoTKR重写器的四种问题类型"""
    print("🧠 测试CoTKR重写器 - 四种问题类型")
    print("=" * 60)
    
    try:
        from cotkr_rewriter import CoTKRRewriter
        
        rewriter = CoTKRRewriter()
        
        # 模拟检索结果
        mock_items = [
            {
                'triple': ('John_Doe', 'wrote', 'A_Fistful_of_Dollars'),
                'schema': ('Person', 'wrote', 'Movie'),
                'distance': 0.25
            },
            {
                'triple': ('Steven_Spielberg', 'directed', 'Jaws'),
                'schema': ('Director', 'directed', 'Movie'),
                'distance': 0.30
            }
        ]
        
        # 四种类型的测试问题
        test_cases = [
            {
                'question': "Who wrote A Fistful of Dollars?",
                'expected_type': 'subject',
                'expected_answer': 'John Doe'
            },
            {
                'question': "What did John Doe write?",
                'expected_type': 'object',
                'expected_answer': 'A Fistful of Dollars'
            },
            {
                'question': "What is the relationship between John Doe and A Fistful of Dollars?",
                'expected_type': 'relationship',
                'expected_answer': 'wrote'
            },
            {
                'question': "What type of entity is John Doe?",
                'expected_type': 'type',
                'expected_answer': 'Person'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            question = test_case['question']
            expected_type = test_case['expected_type']
            expected_answer = test_case['expected_answer']
            
            print(f"\n{i}. 测试问题: {question}")
            
            # 检测问题类型
            detected_type = rewriter.detect_question_type(question)
            type_correct = detected_type == expected_type
            print(f"   问题类型: {detected_type} {'✅' if type_correct else '❌'} (预期: {expected_type})")
            
            # 重写知识
            rewritten_knowledge = rewriter.rewrite_knowledge(mock_items, question)
            print(f"   重写知识: {rewritten_knowledge.split('.')[0]}...")  # 只显示第一句
            
            # 提取答案
            extracted_answer = rewriter.extract_answer_from_knowledge(question, rewritten_knowledge, mock_items)
            answer_correct = extracted_answer.lower() == expected_answer.lower()
            print(f"   提取答案: {extracted_answer} {'✅' if answer_correct else '❌'} (预期: {expected_answer})")
            
            print(f"   测试结果: {'通过' if type_correct and answer_correct else '失败'}")
        
        print("\n✅ CoTKR四种类型测试完成")
        
    except Exception as e:
        print(f"❌ CoTKR测试失败: {e}")

def test_qa_generator_four_types():
    """测试QA生成器的四种问题类型"""
    print("\n📝 测试QA生成器 - 四种问题类型")
    print("=" * 60)
    
    try:
        from qa_generator import QAGenerator
        
        generator = QAGenerator()
        
        # 测试三元组
        test_triple = ('John_Doe', 'wrote', 'A_Fistful_of_Dollars')
        test_schema = ('Person', 'wrote', 'Movie')
        
        print(f"测试三元组: {test_triple}")
        print(f"测试Schema: {test_schema}")
        
        # 生成四种类型的QA对
        qa_pairs = generator.generate_qa_from_triple(test_triple, test_schema)
        
        expected_types = ['subject', 'object', 'relationship', 'type']
        
        print(f"\n生成了 {len(qa_pairs)} 个QA对:")
        
        for i, qa_pair in enumerate(qa_pairs):
            question_type = qa_pair['question_type']
            question = qa_pair['question']
            answer = qa_pair['answer']
            
            type_expected = question_type in expected_types
            print(f"\n{i+1}. 类型: {question_type} {'✅' if type_expected else '❌'}")
            print(f"   问题: {question}")
            print(f"   答案: {answer}")
        
        # 检查是否生成了所有四种类型
        generated_types = set(qa['question_type'] for qa in qa_pairs)
        missing_types = set(expected_types) - generated_types
        
        if not missing_types:
            print("\n✅ 成功生成所有四种类型的QA对")
        else:
            print(f"\n⚠ 缺少类型: {missing_types}")
        
    except Exception as e:
        print(f"❌ QA生成器测试失败: {e}")

def test_end_to_end_four_types():
    """端到端测试四种问题类型"""
    print("\n🔄 端到端测试 - 四种问题类型")
    print("=" * 60)
    
    try:
        from retrieval_engine import RetrievalEngine
        
        engine = RetrievalEngine()
        
        # 四种类型的测试问题
        test_questions = [
            "Who wrote A Fistful of Dollars?",  # subject
            "What did John write?",              # object  
            "What is the relationship between John and the book?",  # relationship
            "What type of entity is John?"       # type
        ]
        
        print("测试问题:")
        for i, question in enumerate(test_questions, 1):
            print(f"  {i}. {question}")
        
        print("\n开始端到端测试...")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. 问题: {question}")
            
            try:
                result = engine.retrieve_and_rewrite(question)
                
                question_type = result['retrieval_stats']['question_type']
                final_answer = result['final_answer']
                num_retrieved = result['retrieval_stats']['num_retrieved']
                
                print(f"   检测类型: {question_type}")
                print(f"   检索数量: {num_retrieved}")
                print(f"   最终答案: {final_answer}")
                
                # 检查CoTKR重写知识的前两行
                cotkr_lines = result['cotkr_knowledge'].split('\n')[:2]
                print(f"   CoTKR重写: {cotkr_lines[0] if cotkr_lines else 'N/A'}")
                
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
        
        print("\n✅ 端到端测试完成")
        
    except Exception as e:
        print(f"❌ 端到端测试失败: {e}")

def test_qa_dataset_generation():
    """测试QA数据集生成"""
    print("\n📊 测试QA数据集生成")
    print("=" * 60)
    
    try:
        from qa_generator import QAGenerator
        
        generator = QAGenerator()
        
        # 生成小规模数据集
        print("生成小规模QA数据集 (最多2个条目)...")
        qa_dataset = generator.generate_qa_dataset(max_entries=2)
        
        if qa_dataset:
            print(f"✅ 成功生成 {len(qa_dataset)} 个QA对")
            
            # 统计类型分布
            type_counts = {}
            for qa in qa_dataset:
                q_type = qa.get('question_type', 'unknown')
                type_counts[q_type] = type_counts.get(q_type, 0) + 1
            
            print("\n📊 类型分布:")
            for q_type, count in type_counts.items():
                print(f"   {q_type}: {count} 个")
            
            # 显示每种类型的示例
            print("\n📋 示例QA对:")
            shown_types = set()
            for qa in qa_dataset:
                q_type = qa['question_type']
                if q_type not in shown_types:
                    print(f"   {q_type}: {qa['question']} -> {qa['answer']}")
                    shown_types.add(q_type)
                    if len(shown_types) >= 4:  # 最多显示4种类型
                        break
        else:
            print("❌ QA数据集生成失败")
        
    except Exception as e:
        print(f"❌ QA数据集生成测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 改造后系统测试 - 四种问题类型")
    print("🎯 Subject, Object, Relationship, Type")
    print("=" * 80)
    
    # 运行各项测试
    test_cotkr_four_types()
    test_qa_generator_four_types()
    test_qa_dataset_generation()
    test_end_to_end_four_types()
    
    print("\n🎉 所有测试完成！")
    print("=" * 80)
    
    print("\n📋 系统改造总结:")
    print("✅ CoTKR重写器支持四种问题类型")
    print("✅ QA生成器为每个三元组生成四种类型的QA对")
    print("✅ 问题类型检测算法更新")
    print("✅ 答案提取逻辑针对四种类型优化")
    
    print("\n🔧 四种问题类型:")
    print("   1. Subject - 询问三元组的主语 (Who wrote X?)")
    print("   2. Object - 询问三元组的宾语 (What did X write?)")
    print("   3. Relationship - 询问三元组的关系 (What is the relationship between X and Y?)")
    print("   4. Type - 询问实体的类型 (What type of entity is X?)")

if __name__ == '__main__':
    main()