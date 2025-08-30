#!/usr/bin/env python3
# quick_validate.py - 快速验证指定的评估结果文件

import json
import os
from pathlib import Path
from datetime import datetime

def validate_qa_results():
    """验证QA评估结果"""
    
    # 指定文件路径
    file_path = r"D:\PythonFile\newSystem\evaluation\simple_qa_records_20250831_005030.jsonl"
    output_dir = Path(r"D:\PythonFile\newSystem\evaluation\evaluation_result")
    
    print(f"🎯 验证评估结果文件")
    print(f"📁 源文件: {file_path}")
    print(f"📁 输出目录: {output_dir}")
    print("=" * 60)
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 加载QA记录
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        print(f"⚠ 第 {line_num} 行JSON解析错误: {e}")
        
        print(f"✅ 成功加载 {len(records)} 条QA记录")
        
    except Exception as e:
        print(f"❌ 加载文件时出错: {e}")
        return
    
    if not records:
        print("❌ 没有有效的QA记录")
        return
    
    # 验证结果
    rag_correct = 0
    llm_correct = 0
    both_correct = 0
    both_wrong = 0
    rag_only_correct = 0
    llm_only_correct = 0
    
    detailed_results = []
    
    print(f"\n🔍 开始验证 {len(records)} 条记录...")
    
    for i, record in enumerate(records, 1):
        question = record.get('question', '')
        expected = record.get('expected_answer', '').lower().strip()
        rag_answer = record.get('rag_answer', '').lower().strip()
        llm_answer = record.get('llm_answer', '').lower().strip()
        
        # 简单的正确性判断（精确匹配或包含匹配）
        rag_correct_flag = (expected == rag_answer) or (expected in rag_answer) or (rag_answer in expected)
        llm_correct_flag = (expected == llm_answer) or (expected in llm_answer) or (llm_answer in expected)
        
        # 统计
        if rag_correct_flag:
            rag_correct += 1
        if llm_correct_flag:
            llm_correct += 1
        
        if rag_correct_flag and llm_correct_flag:
            both_correct += 1
        elif not rag_correct_flag and not llm_correct_flag:
            both_wrong += 1
        elif rag_correct_flag and not llm_correct_flag:
            rag_only_correct += 1
        elif not rag_correct_flag and llm_correct_flag:
            llm_only_correct += 1
        
        # 保存详细结果
        detailed_results.append({
            'id': i,
            'question': question,
            'expected': record.get('expected_answer', ''),
            'rag_answer': record.get('rag_answer', ''),
            'llm_answer': record.get('llm_answer', ''),
            'rag_correct': rag_correct_flag,
            'llm_correct': llm_correct_flag
        })
    
    # 计算正确率
    total = len(records)
    rag_accuracy = rag_correct / total if total > 0 else 0
    llm_accuracy = llm_correct / total if total > 0 else 0
    
    # 打印结果
    print(f"\n📊 验证结果:")
    print(f"=" * 40)
    print(f"总问题数: {total}")
    print(f"RAG正确数: {rag_correct} ({rag_accuracy:.2%})")
    print(f"LLM正确数: {llm_correct} ({llm_accuracy:.2%})")
    print()
    print(f"详细分析:")
    print(f"  两者都正确: {both_correct} ({both_correct/total:.2%})")
    print(f"  两者都错误: {both_wrong} ({both_wrong/total:.2%})")
    print(f"  仅RAG正确: {rag_only_correct} ({rag_only_correct/total:.2%})")
    print(f"  仅LLM正确: {llm_only_correct} ({llm_only_correct/total:.2%})")
    
    # 判断哪个系统表现更好
    if rag_accuracy > llm_accuracy:
        diff = rag_accuracy - llm_accuracy
        print(f"\n🏆 RAG系统表现更好，领先 {diff:.2%}")
    elif llm_accuracy > rag_accuracy:
        diff = llm_accuracy - rag_accuracy
        print(f"\n🏆 LLM系统表现更好，领先 {diff:.2%}")
    else:
        print(f"\n🤝 两个系统表现相当")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存汇总结果
    summary_file = output_dir / f"validation_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"RAG vs LLM 评估结果验证\n")
        f.write(f"=" * 30 + "\n\n")
        f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"源文件: {file_path}\n\n")
        
        f.write(f"总体统计:\n")
        f.write(f"  总问题数: {total}\n")
        f.write(f"  RAG正确数: {rag_correct}\n")
        f.write(f"  LLM正确数: {llm_correct}\n\n")
        
        f.write(f"正确率:\n")
        f.write(f"  RAG正确率: {rag_accuracy:.2%}\n")
        f.write(f"  LLM正确率: {llm_accuracy:.2%}\n\n")
        
        f.write(f"详细分析:\n")
        f.write(f"  两者都正确: {both_correct} ({both_correct/total:.2%})\n")
        f.write(f"  两者都错误: {both_wrong} ({both_wrong/total:.2%})\n")
        f.write(f"  仅RAG正确: {rag_only_correct} ({rag_only_correct/total:.2%})\n")
        f.write(f"  仅LLM正确: {llm_only_correct} ({llm_only_correct/total:.2%})\n")
    
    # 2. 保存详细结果（CSV格式）
    csv_file = output_dir / f"detailed_results_{timestamp}.csv"
    with open(csv_file, 'w', encoding='utf-8-sig') as f:
        f.write("ID,问题,期望答案,RAG答案,LLM答案,RAG正确,LLM正确\n")
        for result in detailed_results:
            f.write(f"{result['id']},")
            f.write(f'"{result["question"]}",')
            f.write(f'"{result["expected"]}",')
            f.write(f'"{result["rag_answer"]}",')
            f.write(f'"{result["llm_answer"]}",')
            f.write(f"{'是' if result['rag_correct'] else '否'},")
            f.write(f"{'是' if result['llm_correct'] else '否'}\n")
    
    # 3. 保存JSON格式的完整结果
    json_file = output_dir / f"validation_results_{timestamp}.json"
    results_data = {
        'timestamp': datetime.now().isoformat(),
        'source_file': file_path,
        'total_questions': total,
        'rag_correct': rag_correct,
        'llm_correct': llm_correct,
        'rag_accuracy': rag_accuracy,
        'llm_accuracy': llm_accuracy,
        'both_correct': both_correct,
        'both_wrong': both_wrong,
        'rag_only_correct': rag_only_correct,
        'llm_only_correct': llm_only_correct,
        'detailed_results': detailed_results
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到:")
    print(f"   - 汇总报告: {summary_file.name}")
    print(f"   - 详细CSV: {csv_file.name}")
    print(f"   - 完整JSON: {json_file.name}")
    
    # 显示一些错误案例
    print(f"\n❌ 错误案例示例 (前5个):")
    print("-" * 50)
    
    error_count = 0
    for result in detailed_results:
        if not result['rag_correct'] or not result['llm_correct']:
            error_count += 1
            if error_count <= 5:
                print(f"\n案例 {error_count}:")
                print(f"  问题: {result['question']}")
                print(f"  期望: {result['expected']}")
                print(f"  RAG: {result['rag_answer']} {'✓' if result['rag_correct'] else '✗'}")
                print(f"  LLM: {result['llm_answer']} {'✓' if result['llm_correct'] else '✗'}")
    
    print(f"\n✅ 验证完成！")

if __name__ == '__main__':
    validate_qa_results()