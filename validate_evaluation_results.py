#!/usr/bin/env python3
# validate_evaluation_results.py - 验证RAG vs LLM评估结果的正确率

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import csv

class EvaluationResultValidator:
    """评估结果验证器"""
    
    def __init__(self, evaluation_dir: str = "evaluation"):
        self.evaluation_dir = Path(evaluation_dir)
        self.output_dir = self.evaluation_dir / "evaluation_result"
        
        # 确保输出目录存在
        self.output_dir.mkdir(exist_ok=True)
    
    def find_simple_qa_records_files(self) -> List[Path]:
        """查找所有simple_qa_records文件"""
        pattern = "simple_qa_records_*.jsonl"
        files = list(self.evaluation_dir.glob(pattern))
        
        print(f"🔍 在 {self.evaluation_dir} 中找到 {len(files)} 个评估结果文件:")
        for file in files:
            print(f"   - {file.name}")
        
        return files
    
    def load_qa_records(self, file_path: Path) -> List[Dict]:
        """加载QA记录"""
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
            print(f"❌ 加载文件 {file_path} 时出错: {e}")
        
        return records
    
    def normalize_answer(self, answer: str) -> str:
        """标准化答案文本，用于比较"""
        if not answer:
            return ""
        
        # 转换为小写并去除首尾空格
        normalized = answer.lower().strip()
        
        # 去除标点符号
        import string
        normalized = normalized.translate(str.maketrans('', '', string.punctuation))
        
        # 去除多余空格
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def is_answer_correct(self, predicted: str, expected: str) -> bool:
        """判断答案是否正确"""
        pred_norm = self.normalize_answer(predicted)
        exp_norm = self.normalize_answer(expected)
        
        if not pred_norm or not exp_norm:
            return False
        
        # 精确匹配
        if pred_norm == exp_norm:
            return True
        
        # 包含匹配（预测答案包含期望答案或反之）
        if exp_norm in pred_norm or pred_norm in exp_norm:
            return True
        
        return False
    
    def validate_records(self, records: List[Dict]) -> Dict:
        """验证QA记录的正确率"""
        results = {
            'total_questions': len(records),
            'rag_correct': 0,
            'llm_correct': 0,
            'both_correct': 0,
            'both_wrong': 0,
            'rag_only_correct': 0,
            'llm_only_correct': 0,
            'detailed_results': []
        }
        
        print(f"\n🔍 开始验证 {len(records)} 条QA记录...")
        
        for i, record in enumerate(records, 1):
            question = record.get('question', '')
            expected = record.get('expected_answer', '')
            rag_answer = record.get('rag_answer', '')
            llm_answer = record.get('llm_answer', '')
            
            # 判断正确性
            rag_correct = self.is_answer_correct(rag_answer, expected)
            llm_correct = self.is_answer_correct(llm_answer, expected)
            
            # 统计
            if rag_correct:
                results['rag_correct'] += 1
            if llm_correct:
                results['llm_correct'] += 1
            
            if rag_correct and llm_correct:
                results['both_correct'] += 1
            elif not rag_correct and not llm_correct:
                results['both_wrong'] += 1
            elif rag_correct and not llm_correct:
                results['rag_only_correct'] += 1
            elif not rag_correct and llm_correct:
                results['llm_only_correct'] += 1
            
            # 保存详细结果
            detailed_result = {
                'question_id': i,
                'question': question,
                'expected_answer': expected,
                'rag_answer': rag_answer,
                'llm_answer': llm_answer,
                'rag_correct': rag_correct,
                'llm_correct': llm_correct,
                'rag_normalized': self.normalize_answer(rag_answer),
                'llm_normalized': self.normalize_answer(llm_answer),
                'expected_normalized': self.normalize_answer(expected)
            }
            results['detailed_results'].append(detailed_result)
        
        # 计算正确率
        total = results['total_questions']
        if total > 0:
            results['rag_accuracy'] = results['rag_correct'] / total
            results['llm_accuracy'] = results['llm_correct'] / total
        else:
            results['rag_accuracy'] = 0.0
            results['llm_accuracy'] = 0.0
        
        return results
    
    def save_validation_results(self, results: Dict, source_file: str):
        """保存验证结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = Path(source_file).stem
        
        # 1. 保存JSON格式的完整结果
        json_file = self.output_dir / f"{base_name}_validation_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 2. 保存CSV格式的详细结果
        csv_file = self.output_dir / f"{base_name}_detailed_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                '问题ID', '问题', '期望答案', 'RAG答案', 'LLM答案',
                'RAG正确', 'LLM正确', 'RAG标准化', 'LLM标准化', '期望标准化'
            ])
            
            # 写入数据行
            for detail in results['detailed_results']:
                writer.writerow([
                    detail['question_id'],
                    detail['question'],
                    detail['expected_answer'],
                    detail['rag_answer'],
                    detail['llm_answer'],
                    '✓' if detail['rag_correct'] else '✗',
                    '✓' if detail['llm_correct'] else '✗',
                    detail['rag_normalized'],
                    detail['llm_normalized'],
                    detail['expected_normalized']
                ])
        
        # 3. 保存汇总报告
        report_file = self.output_dir / f"{base_name}_summary_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"RAG vs LLM 评估结果验证报告\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"源文件: {source_file}\n")
            f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"📊 总体统计:\n")
            f.write(f"   总问题数: {results['total_questions']}\n")
            f.write(f"   RAG正确数: {results['rag_correct']}\n")
            f.write(f"   LLM正确数: {results['llm_correct']}\n\n")
            
            f.write(f"📈 正确率:\n")
            f.write(f"   RAG正确率: {results['rag_accuracy']:.2%}\n")
            f.write(f"   LLM正确率: {results['llm_accuracy']:.2%}\n\n")
            
            f.write(f"🔍 详细分析:\n")
            f.write(f"   两者都正确: {results['both_correct']} ({results['both_correct']/results['total_questions']:.2%})\n")
            f.write(f"   两者都错误: {results['both_wrong']} ({results['both_wrong']/results['total_questions']:.2%})\n")
            f.write(f"   仅RAG正确: {results['rag_only_correct']} ({results['rag_only_correct']/results['total_questions']:.2%})\n")
            f.write(f"   仅LLM正确: {results['llm_only_correct']} ({results['llm_only_correct']/results['total_questions']:.2%})\n\n")
            
            # 添加错误案例分析
            f.write(f"❌ 错误案例分析:\n")
            f.write(f"-" * 30 + "\n")
            
            error_count = 0
            for detail in results['detailed_results']:
                if not detail['rag_correct'] or not detail['llm_correct']:
                    error_count += 1
                    if error_count <= 10:  # 只显示前10个错误案例
                        f.write(f"\n案例 {error_count}:\n")
                        f.write(f"  问题: {detail['question']}\n")
                        f.write(f"  期望: {detail['expected_answer']}\n")
                        f.write(f"  RAG: {detail['rag_answer']} {'✓' if detail['rag_correct'] else '✗'}\n")
                        f.write(f"  LLM: {detail['llm_answer']} {'✓' if detail['llm_correct'] else '✗'}\n")
        
        print(f"\n💾 验证结果已保存:")
        print(f"   - 完整结果: {json_file.name}")
        print(f"   - 详细CSV: {csv_file.name}")
        print(f"   - 汇总报告: {report_file.name}")
        
        return {
            'json_file': json_file,
            'csv_file': csv_file,
            'report_file': report_file
        }
    
    def print_summary(self, results: Dict):
        """打印验证结果摘要"""
        total = results['total_questions']
        
        print(f"\n📊 验证结果摘要:")
        print(f"=" * 40)
        print(f"总问题数: {total}")
        print(f"RAG正确数: {results['rag_correct']} ({results['rag_accuracy']:.2%})")
        print(f"LLM正确数: {results['llm_correct']} ({results['llm_accuracy']:.2%})")
        print()
        print(f"详细分析:")
        print(f"  两者都正确: {results['both_correct']} ({results['both_correct']/total:.2%})")
        print(f"  两者都错误: {results['both_wrong']} ({results['both_wrong']/total:.2%})")
        print(f"  仅RAG正确: {results['rag_only_correct']} ({results['rag_only_correct']/total:.2%})")
        print(f"  仅LLM正确: {results['llm_only_correct']} ({results['llm_only_correct']/total:.2%})")
        
        # 判断哪个系统表现更好
        if results['rag_accuracy'] > results['llm_accuracy']:
            diff = results['rag_accuracy'] - results['llm_accuracy']
            print(f"\n🏆 RAG系统表现更好，领先 {diff:.2%}")
        elif results['llm_accuracy'] > results['rag_accuracy']:
            diff = results['llm_accuracy'] - results['rag_accuracy']
            print(f"\n🏆 LLM系统表现更好，领先 {diff:.2%}")
        else:
            print(f"\n🤝 两个系统表现相当")

def validate_specific_file(file_path: str):
    """验证指定的评估结果文件"""
    print(f"🎯 验证指定文件: {file_path}")
    print("=" * 60)
    
    validator = EvaluationResultValidator()
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 加载QA记录
    records = validator.load_qa_records(file_path_obj)
    if not records:
        print("❌ 无法加载QA记录")
        return
    
    # 验证结果
    results = validator.validate_records(records)
    
    # 保存结果
    saved_files = validator.save_validation_results(results, file_path_obj.name)
    
    # 打印摘要
    validator.print_summary(results)
    
    print(f"\n✅ 验证完成！结果已保存到 evaluation_result 文件夹")

def validate_all_files():
    """验证所有评估结果文件"""
    print("🔍 验证所有评估结果文件")
    print("=" * 50)
    
    validator = EvaluationResultValidator()
    
    # 查找所有文件
    files = validator.find_simple_qa_records_files()
    
    if not files:
        print("❌ 未找到任何评估结果文件")
        return
    
    # 验证每个文件
    for i, file_path in enumerate(files, 1):
        print(f"\n📄 验证文件 {i}/{len(files)}: {file_path.name}")
        print("-" * 40)
        
        # 加载QA记录
        records = validator.load_qa_records(file_path)
        if not records:
            continue
        
        # 验证结果
        results = validator.validate_records(records)
        
        # 保存结果
        saved_files = validator.save_validation_results(results, file_path.name)
        
        # 打印摘要
        validator.print_summary(results)
    
    print(f"\n✅ 所有文件验证完成！")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="验证RAG vs LLM评估结果的正确率")
    parser.add_argument('--file', type=str, 
                       help='指定要验证的文件路径 (例如: evaluation/simple_qa_records_20250831_005030.jsonl)')
    parser.add_argument('--all', action='store_true',
                       help='验证evaluation目录下的所有文件')
    
    args = parser.parse_args()
    
    if args.file:
        validate_specific_file(args.file)
    elif args.all:
        validate_all_files()
    else:
        # 默认验证指定文件
        target_file = r"D:\PythonFile\newSystem\evaluation\simple_qa_records_20250831_005030.jsonl"
        validate_specific_file(target_file)