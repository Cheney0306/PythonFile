#!/usr/bin/env python3
# create_realistic_test_questions.py - 基于实际数据库内容创建测试问题

from enhanced_embedding_system import EnhancedVectorDatabaseManager
import json
import random

def analyze_database_content():
    """分析数据库内容，生成合适的测试问题"""
    print("🔍 分析数据库内容生成测试问题")
    print("=" * 50)
    
    db_manager = EnhancedVectorDatabaseManager()
    db_manager.initialize_collection()
    
    # 获取数据库中的所有数据
    all_data = db_manager.collection.get()
    
    if not all_data or not all_data['metadatas']:
        print("❌ 数据库为空")
        return []
    
    # 分析不同类型的关系
    relations = {}
    for metadata in all_data['metadatas']:
        rel = metadata.get('rel', '')
        sub = metadata.get('sub', '')
        obj = metadata.get('obj', '')
        sub_type = metadata.get('sub_type', '')
        obj_type = metadata.get('obj_type', '')
        
        if rel not in relations:
            relations[rel] = []
        
        relations[rel].append({
            'sub': sub,
            'obj': obj,
            'sub_type': sub_type,
            'obj_type': obj_type
        })
    
    print(f"📊 发现 {len(relations)} 种关系类型:")
    for rel, items in relations.items():
        print(f"  - {rel}: {len(items)} 条记录")
    
    # 生成基于实际数据的测试问题
    test_questions = []
    
    # 1. 基于 'leader' 关系的问题
    if 'leader' in relations:
        leader_items = relations['leader'][:3]  # 取前3个
        for item in leader_items:
            test_questions.append({
                'question': f"Who is the leader of {item['sub'].replace('_', ' ')}?",
                'expected_answer': item['obj'].replace('_', ' '),
                'question_type': 'factual',
                'relation': 'leader',
                'subject': item['sub']
            })
    
    # 2. 基于 'capital' 关系的问题
    if 'capital' in relations:
        capital_items = relations['capital'][:3]
        for item in capital_items:
            test_questions.append({
                'question': f"What is the capital of {item['sub'].replace('_', ' ')}?",
                'expected_answer': item['obj'].replace('_', ' '),
                'question_type': 'factual',
                'relation': 'capital',
                'subject': item['sub']
            })
    
    # 3. 基于 'location' 关系的问题
    if 'location' in relations:
        location_items = relations['location'][:3]
        for item in location_items:
            test_questions.append({
                'question': f"Where is {item['sub'].replace('_', ' ')} located?",
                'expected_answer': item['obj'].replace('_', ' '),
                'question_type': 'location',
                'relation': 'location',
                'subject': item['sub']
            })
    
    # 4. 基于 'country' 关系的问题
    if 'country' in relations:
        country_items = relations['country'][:2]
        for item in country_items:
            test_questions.append({
                'question': f"Which country is {item['sub'].replace('_', ' ')} in?",
                'expected_answer': item['obj'].replace('_', ' '),
                'question_type': 'location',
                'relation': 'country',
                'subject': item['sub']
            })
    
    print(f"\n📝 生成了 {len(test_questions)} 个基于实际数据的测试问题:")
    for i, q in enumerate(test_questions, 1):
        print(f"  {i}. {q['question']}")
        print(f"     期望答案: {q['expected_answer']}")
        print(f"     关系类型: {q['relation']}")
        print()
    
    return test_questions

def save_realistic_test_questions():
    """保存现实的测试问题"""
    questions = analyze_database_content()
    
    if questions:
        # 保存为JSON文件
        with open('realistic_test_questions.json', 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存 {len(questions)} 个测试问题到 realistic_test_questions.json")
        
        # 创建更新的测试脚本
        create_updated_test_script(questions)
    
    return questions

def create_updated_test_script(questions):
    """创建使用现实问题的测试脚本"""
    
    script_content = f'''#!/usr/bin/env python3
# test_realistic_rag_vs_llm_evaluation.py - 使用现实问题的RAG vs LLM评估测试

import json
from pathlib import Path
from rag_vs_llm_evaluation import RAGvsLLMEvaluator

def test_realistic_evaluation():
    """使用基于实际数据库内容的问题进行测试"""
    print("🧪 测试RAG vs LLM评估系统 (使用现实问题)")
    print("=" * 60)
    
    # 创建评估器
    evaluator = RAGvsLLMEvaluator()
    
    # 使用基于实际数据库内容的测试问题
    test_questions = {questions}
    
    print(f"📝 测试 {{len(test_questions)}} 个基于实际数据的问题")
    
    # 测试单个问题评估
    print("\\n🔍 测试单个问题评估:")
    for i, qa_item in enumerate(test_questions[:3], 1):  # 只测试前3个
        print(f"\\n问题 {{i}}: {{qa_item['question']}}")
        print(f"  关系类型: {{qa_item['relation']}}")
        print(f"  主体: {{qa_item['subject']}}")
        
        result = evaluator.evaluate_single_question(qa_item)
        
        print(f"  期望答案: {{result['expected_answer']}}")
        print(f"  RAG答案: {{result['rag_answer']}}")
        print(f"  LLM答案: {{result['llm_answer']}}")
        
        # 显示检索指标
        if 'rag_retrieval_metrics' in result:
            metrics = result['rag_retrieval_metrics']
            print(f"  检索指标:")
            print(f"    Precision@1: {{metrics.get('precision@1', 0):.3f}}")
            print(f"    Recall@1: {{metrics.get('recall@1', 0):.3f}}")
            print(f"    nDCG@1: {{metrics.get('ndcg@1', 0):.3f}}")
        
        # 显示答案质量分数
        print(f"  RAG综合分数: {{result['rag_scores']['composite_score']:.3f}}")
        print(f"  LLM综合分数: {{result['llm_scores']['composite_score']:.3f}}")
    
    # 测试完整评估流程
    print(f"\\n🚀 运行完整评估流程...")
    
    results = evaluator.evaluate_dataset(test_questions)
    
    # 保存结果
    evaluator.save_evaluation_results(results, output_dir="realistic_evaluation")
    
    # 打印报告
    evaluator.print_summary_report(results)
    
    print(f"\\n✅ 现实问题评估测试完成！")

if __name__ == '__main__':
    test_realistic_evaluation()
'''
    
    with open('test_realistic_rag_vs_llm_evaluation.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📄 已创建更新的测试脚本: test_realistic_rag_vs_llm_evaluation.py")

if __name__ == '__main__':
    save_realistic_test_questions()