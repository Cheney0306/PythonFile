# test_scan_all_evaluation.py - 测试全量扫描评估功能

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from retrieval_evaluation_system import RetrievalEvaluator

def test_scan_all_functionality():
    """测试全量扫描功能"""
    print("🧪 测试全量扫描评估功能")
    print("=" * 50)
    
    evaluator = RetrievalEvaluator()
    
    # 测试加载全部数据
    print("📊 测试1: 加载全部QA数据")
    all_questions = evaluator.load_qa_dataset(scan_all=True)
    
    if all_questions:
        print(f"✅ 成功加载 {len(all_questions)} 个问题")
        
        # 统计信息
        question_types = {}
        source_files = {}
        
        for q in all_questions:
            q_type = q.get('question_type', 'unknown')
            source_file = q.get('source_file', 'unknown')
            
            question_types[q_type] = question_types.get(q_type, 0) + 1
            source_files[source_file] = source_files.get(source_file, 0) + 1
        
        print(f"\n📋 问题类型分布:")
        for q_type, count in sorted(question_types.items()):
            percentage = (count / len(all_questions)) * 100
            print(f"   - {q_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n📁 数据文件分布:")
        for source_file, count in sorted(source_files.items()):
            percentage = (count / len(all_questions)) * 100
            print(f"   - {source_file}: {count} ({percentage:.1f}%)")
        
        # 显示前几个问题示例
        print(f"\n📝 问题示例 (前5个):")
        for i, q in enumerate(all_questions[:5], 1):
            print(f"{i}. 类型: {q.get('question_type', 'unknown')}")
            print(f"   问题: {q['question'][:80]}...")
            print(f"   答案: {q['expected_answer']}")
            print(f"   来源: {q.get('source_file', 'unknown')}")
            print()
    else:
        print("❌ 未找到QA数据")
    
    # 测试对比限制模式
    print("\n📊 测试2: 对比限制模式")
    limited_questions = evaluator.load_qa_dataset(limit=10, scan_all=False)
    print(f"限制模式: {len(limited_questions)} 个问题")
    print(f"全量模式: {len(all_questions)} 个问题")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")

def show_usage_examples():
    """显示使用示例"""
    print("\n💡 全量扫描评估使用示例:")
    print("=" * 40)
    print("1. 扫描全部QA数据:")
    print("   python retrieval_evaluation_system.py --mode scan-all")
    print()
    print("2. 指定数据集路径:")
    print("   python retrieval_evaluation_system.py --mode scan-all --qa-path custom_qa_datasets")
    print()
    print("3. 自定义K值:")
    print("   python retrieval_evaluation_system.py --mode scan-all --k-values 1 3 5 10 20")
    print()
    print("4. 指定输出目录:")
    print("   python retrieval_evaluation_system.py --mode scan-all --output-dir custom_evaluation")
    print("=" * 40)

if __name__ == "__main__":
    # 显示使用示例
    show_usage_examples()
    
    # 运行测试
    test_scan_all_functionality()