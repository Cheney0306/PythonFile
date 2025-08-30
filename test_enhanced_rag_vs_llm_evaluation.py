#!/usr/bin/env python3
# test_enhanced_rag_vs_llm_evaluation.py - 测试增强的RAG vs LLM评估系统

import json
import random
from pathlib import Path
from rag_vs_llm_evaluation import RAGvsLLMEvaluator

def load_qa_dataset_questions(dataset_path: str = None, num_questions: int = 5):
    """从QA数据集中随机加载测试问题"""
    
    # 尝试多个可能的QA数据集位置
    possible_paths = [
        "qa_datasets",  # 当前目录下的qa_datasets
        "../qa_datasets",  # 上级目录的qa_datasets
        ".",  # 当前目录（查找所有json文件）
    ]
    
    if dataset_path:
        possible_paths.insert(0, dataset_path)
    
    qa_files = []
    used_path = None
    
    for path in possible_paths:
        print(f"📁 尝试从 {path} 加载QA数据集...")
        try:
            path_obj = Path(path)
            if path_obj.exists():
                files = list(path_obj.glob("*.json"))
                # 过滤出看起来像QA数据集的文件
                qa_files = [f for f in files if any(keyword in f.name.lower() 
                           for keyword in ['qa', 'question', 'dataset', 'enhanced'])]
                if qa_files:
                    used_path = path
                    print(f"✅ 在 {path} 中找到 {len(qa_files)} 个QA数据集文件")
                    break
                else:
                    print(f"⚠ 在 {path} 中未找到QA数据集文件")
            else:
                print(f"⚠ 路径 {path} 不存在")
        except Exception as e:
            print(f"⚠ 检查路径 {path} 时出错: {e}")
    
    if not qa_files:
        print(f"❌ 在所有可能的位置都未找到QA数据集文件")
        return []
    
    all_questions = []
    
    print(f"📄 找到的QA数据集文件:")
    for qa_file in qa_files:
        print(f"   - {qa_file.name}")
    
    for qa_file in qa_files:
        try:
            with open(qa_file, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            
            file_questions = 0
            for qa_item in qa_data:
                if 'question' in qa_item and 'answer' in qa_item:
                    all_questions.append({
                        'question': qa_item['question'],
                        'expected_answer': qa_item['answer'],
                        'question_type': qa_item.get('question_type', 'unknown'),
                        'source_text': qa_item.get('source_text', ''),
                        'triple': qa_item.get('triple'),
                        'schema': qa_item.get('schema'),
                        'source_file': qa_file.name
                    })
                    file_questions += 1
            
            print(f"   ✅ {qa_file.name}: {file_questions} 个问题")
                    
        except Exception as e:
            print(f"⚠ 加载文件 {qa_file} 时出错: {e}")
    
    print(f"📊 总计加载: {len(all_questions)} 个问题")
    
    # 随机选择指定数量的问题
    if len(all_questions) > num_questions:
        selected_questions = random.sample(all_questions, num_questions)
        print(f"🎲 随机选择了 {num_questions} 个问题进行测试")
    else:
        selected_questions = all_questions
        print(f"✅ 使用全部 {len(selected_questions)} 个问题")
    
    return selected_questions

def test_enhanced_evaluation():
    """测试增强的评估功能"""
    print("🧪 测试增强的RAG vs LLM评估系统")
    print("=" * 50)
    
    # 创建评估器
    evaluator = RAGvsLLMEvaluator()
    
    # 从QA数据集中加载测试问题
    test_questions = load_qa_dataset_questions(num_questions=5)
    
    if not test_questions:
        print("❌ 无法加载测试问题，使用默认问题")
        # 备用的硬编码问题
        test_questions = [
            {
                'question': 'Who is the leader of Belgium?',
                'expected_answer': 'Alexander De Croo',
                'question_type': 'factual'
            },
            {
                'question': 'What is the capital of Netherlands?',
                'expected_answer': 'Amsterdam',
                'question_type': 'factual'
            }
        ]
    
    print(f"📝 测试 {len(test_questions)} 个问题")
    
    # 测试单个问题评估
    print("\n🔍 测试单个问题评估:")
    for i, qa_item in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {qa_item['question']}")
        
        result = evaluator.evaluate_single_question(qa_item)
        
        print(f"  期望答案: {result['expected_answer']}")
        print(f"  RAG答案: {result['rag_answer']}")
        print(f"  LLM答案: {result['llm_answer']}")
        
        # 显示检索指标
        if 'rag_retrieval_metrics' in result:
            metrics = result['rag_retrieval_metrics']
            print(f"  检索指标:")
            print(f"    Precision@1: {metrics.get('precision@1', 0):.3f}")
            print(f"    Recall@1: {metrics.get('recall@1', 0):.3f}")
            print(f"    nDCG@1: {metrics.get('ndcg@1', 0):.3f}")
        
        # 显示答案质量分数
        print(f"  RAG综合分数: {result['rag_scores']['composite_score']:.3f}")
        print(f"  LLM综合分数: {result['llm_scores']['composite_score']:.3f}")
    
    # 测试完整评估流程
    print(f"\n🚀 运行完整评估流程...")
    
    results = evaluator.evaluate_dataset(test_questions)
    
    # 保存结果
    evaluator.save_evaluation_results(results, output_dir="test_evaluation")
    
    # 打印报告
    evaluator.print_summary_report(results)
    
    # 验证生成的文件
    print(f"\n📁 验证生成的文件:")
    test_dir = Path("test_evaluation")
    if test_dir.exists():
        files = list(test_dir.glob("*"))
        for file in files:
            print(f"  ✅ {file.name} ({file.stat().st_size} bytes)")
            
            # 检查简化问答记录文件
            if file.name.startswith("simple_qa_records_") and file.suffix == ".jsonl":
                print(f"    📄 检查简化问答记录:")
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"      - 总行数: {len(lines)}")
                    if lines:
                        # 解析第一行
                        first_record = json.loads(lines[0])
                        print(f"      - 第一条记录字段: {list(first_record.keys())}")
                        print(f"      - 示例问题: {first_record.get('question', 'N/A')[:50]}...")
    
    print(f"\n✅ 增强评估系统测试完成!")

def test_retrieval_metrics():
    """测试检索指标计算"""
    print("\n🎯 测试检索指标计算")
    print("-" * 30)
    
    evaluator = RAGvsLLMEvaluator()
    
    # 模拟检索结果
    mock_retrieved_items = [
        {
            'text': 'Alexander De Croo is the Prime Minister of Belgium',
            'distance': 0.1,
            'triple': ('Alexander De Croo', 'is Prime Minister of', 'Belgium')
        },
        {
            'text': 'Belgium is a country in Europe',
            'distance': 0.3,
            'triple': ('Belgium', 'is located in', 'Europe')
        },
        {
            'text': 'Brussels is the capital of Belgium',
            'distance': 0.5,
            'triple': ('Brussels', 'is capital of', 'Belgium')
        }
    ]
    
    expected_answer = "Alexander De Croo"
    
    # 计算检索指标
    metrics = evaluator.calculate_retrieval_metrics(
        mock_retrieved_items, expected_answer, k_values=[1, 2, 3]
    )
    
    print("检索指标结果:")
    for metric, score in metrics.items():
        print(f"  {metric}: {score:.4f}")

if __name__ == '__main__':
    # 测试检索指标计算
    test_retrieval_metrics()
    
    # 测试完整评估系统
    test_enhanced_evaluation()