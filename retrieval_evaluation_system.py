# retrieval_evaluation_system.py - 检索评估系统

import json
import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from tqdm import tqdm
import math
from collections import defaultdict

# 导入我们的系统
from retrieval_engine import RetrievalEngine  # 原始系统
from enhanced_retrieval_engine import EnhancedRetrievalEngine  # 增强系统
import config  # 导入配置

class RetrievalEvaluator:
    """检索系统评估器 - 计算Precision@K, Recall@K, nDCG@K等指标"""
    
    def __init__(self):
        self.original_engine = RetrievalEngine()
        self.enhanced_engine = EnhancedRetrievalEngine()
        
    def load_qa_dataset(self, dataset_path: str = "qa_datasets", limit: int = 100, scan_all: bool = False) -> List[Dict]:
        """
        从QA数据集中加载问题用于评估
        
        Args:
            dataset_path: QA数据集路径
            limit: 限制加载的问题数量 (scan_all=True时忽略)
            scan_all: 是否扫描全部数据，忽略limit限制
        """
        qa_files = list(Path(dataset_path).glob("*.json"))
        
        if not qa_files:
            print(f"❌ 在 {dataset_path} 中未找到QA数据集文件")
            return []
        
        all_questions = []
        
        print(f"📁 找到 {len(qa_files)} 个QA数据集文件:")
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
        
        # 根据scan_all参数决定是否限制数量
        if scan_all:
            print(f"🔍 扫描全部模式: 使用全部 {len(all_questions)} 个问题")
            final_questions = all_questions
        else:
            # 随机采样并限制数量
            if len(all_questions) > limit:
                final_questions = random.sample(all_questions, limit)
                print(f"🎲 随机采样: 从 {len(all_questions)} 个问题中选择 {len(final_questions)} 个")
            else:
                final_questions = all_questions
                print(f"✅ 使用全部 {len(final_questions)} 个问题")
        
        print(f"✅ 最终评估问题数: {len(final_questions)}")
        return final_questions
    
    def create_ground_truth_relevance(self, question_data: Dict, retrieved_items: List[Dict]) -> List[int]:
        """
        创建相关性标注 (0: 不相关, 1: 相关, 2: 高度相关)
        
        基于问题的预期答案和三元组信息判断检索结果的相关性
        """
        relevance_scores = []
        expected_answer = question_data['expected_answer'].lower()
        question_lower = question_data['question'].lower()
        expected_triple = question_data.get('triple')
        
        for item in retrieved_items:
            score = 0
            triple = item['triple']
            sub, rel, obj = triple
            
            # 清理实体名称
            sub_clean = sub.replace('_', ' ').lower()
            obj_clean = obj.replace('_', ' ').lower()
            rel_clean = rel.replace('_', ' ').lower()
            
            # 1. 检查是否包含预期答案
            if expected_answer in sub_clean or expected_answer in obj_clean:
                score += 2
            
            # 2. 检查三元组匹配
            if expected_triple:
                expected_sub, expected_rel, expected_obj = expected_triple
                if (sub == expected_sub and rel == expected_rel and obj == expected_obj):
                    score = 2  # 完全匹配
                elif (sub == expected_sub or obj == expected_obj) and rel == expected_rel:
                    score = max(score, 1)  # 部分匹配
            
            # 3. 检查实体在问题中的出现
            question_entities = self._extract_entities_from_question(question_lower)
            if any(entity in sub_clean or entity in obj_clean for entity in question_entities):
                score = max(score, 1)
            
            # 4. 检查关系相关性
            if self._is_relation_relevant(question_lower, rel_clean):
                score = max(score, 1)
            
            relevance_scores.append(min(score, 2))  # 限制在0-2范围
        
        return relevance_scores
    
    def _extract_entities_from_question(self, question: str) -> List[str]:
        """从问题中提取可能的实体名称"""
        # 简单的实体提取逻辑
        entities = []
        
        # 常见的实体模式
        words = question.split()
        for i, word in enumerate(words):
            # 大写开头的词可能是实体
            if word[0].isupper() and len(word) > 2:
                entities.append(word.lower())
            
            # 连续的大写词组合
            if i < len(words) - 1 and word[0].isupper() and words[i+1][0].isupper():
                entities.append(f"{word} {words[i+1]}".lower())
        
        # 特定实体
        known_entities = ['belgium', 'amsterdam', 'airport', 'schiphol', 'netherlands']
        for entity in known_entities:
            if entity in question:
                entities.append(entity)
        
        return list(set(entities))
    
    def _is_relation_relevant(self, question: str, relation: str) -> bool:
        """判断关系是否与问题相关"""
        relation_keywords = {
            'leader': ['leader', 'president', 'king', 'queen', 'head', 'who leads'],
            'location': ['location', 'located', 'where', 'place'],
            'capital': ['capital'],
            'type': ['type', 'kind', 'what type'],
            'runway': ['runway', 'strip'],
        }
        
        for rel_type, keywords in relation_keywords.items():
            if rel_type in relation:
                return any(keyword in question for keyword in keywords)
        
        return False
    
    def calculate_precision_at_k(self, relevance_scores: List[int], k: int) -> float:
        """计算Precision@K"""
        if k > len(relevance_scores):
            k = len(relevance_scores)
        
        if k == 0:
            return 0.0
        
        relevant_count = sum(1 for score in relevance_scores[:k] if score > 0)
        return relevant_count / k
    
    def calculate_recall_at_k(self, relevance_scores: List[int], k: int) -> float:
        """计算Recall@K"""
        if k > len(relevance_scores):
            k = len(relevance_scores)
        
        total_relevant = sum(1 for score in relevance_scores if score > 0)
        if total_relevant == 0:
            return 0.0
        
        relevant_at_k = sum(1 for score in relevance_scores[:k] if score > 0)
        return relevant_at_k / total_relevant
    
    def calculate_ndcg_at_k(self, relevance_scores: List[int], k: int) -> float:
        """计算nDCG@K (Normalized Discounted Cumulative Gain)"""
        if k > len(relevance_scores):
            k = len(relevance_scores)
        
        if k == 0:
            return 0.0
        
        # 计算DCG@K
        dcg = 0.0
        for i in range(k):
            if i < len(relevance_scores):
                dcg += relevance_scores[i] / math.log2(i + 2)
        
        # 计算IDCG@K (理想情况下的DCG)
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = 0.0
        for i in range(k):
            if i < len(ideal_scores):
                idcg += ideal_scores[i] / math.log2(i + 2)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def evaluate_single_question(self, question_data: Dict, k_values: List[int] = [1, 3, 5, 10]) -> Dict:
        """评估单个问题的检索效果"""
        question = question_data['question']
        
        # 获取两个系统的检索结果
        original_result = self.original_engine.retrieve_and_rewrite(question, n_results=max(k_values))
        enhanced_result = self.enhanced_engine.retrieve_and_rewrite(question, n_results=max(k_values), use_reranking=True)
        
        # 创建相关性标注
        original_relevance = self.create_ground_truth_relevance(question_data, original_result['retrieved_items'])
        enhanced_relevance = self.create_ground_truth_relevance(question_data, enhanced_result['retrieved_items'])
        
        # 计算各种指标
        metrics = {
            'question': question,
            'expected_answer': question_data['expected_answer'],
            'question_type': question_data['question_type'],
            'original_system': {
                'final_answer': original_result['final_answer'],
                'rewritten_query': original_result.get('rewritten_query', question),
                'relevance_scores': original_relevance,
                'metrics': {}
            },
            'enhanced_system': {
                'final_answer': enhanced_result['final_answer'],
                'rewritten_query': enhanced_result.get('rewritten_query', question),
                'relevance_scores': enhanced_relevance,
                'metrics': {}
            }
        }
        
        # 为每个K值计算指标
        for k in k_values:
            # 原始系统
            metrics['original_system']['metrics'][f'precision@{k}'] = self.calculate_precision_at_k(original_relevance, k)
            metrics['original_system']['metrics'][f'recall@{k}'] = self.calculate_recall_at_k(original_relevance, k)
            metrics['original_system']['metrics'][f'ndcg@{k}'] = self.calculate_ndcg_at_k(original_relevance, k)
            
            # 增强系统
            metrics['enhanced_system']['metrics'][f'precision@{k}'] = self.calculate_precision_at_k(enhanced_relevance, k)
            metrics['enhanced_system']['metrics'][f'recall@{k}'] = self.calculate_recall_at_k(enhanced_relevance, k)
            metrics['enhanced_system']['metrics'][f'ndcg@{k}'] = self.calculate_ndcg_at_k(enhanced_relevance, k)
        
        return metrics
    
    def evaluate_dataset(self, questions: List[Dict], k_values: List[int] = [1, 3, 5, 10]) -> Dict:
        """评估整个数据集"""
        print(f"🔄 开始评估 {len(questions)} 个问题...")
        
        all_results = []
        
        for question_data in tqdm(questions, desc="评估进度"):
            try:
                result = self.evaluate_single_question(question_data, k_values)
                all_results.append(result)
            except Exception as e:
                print(f"⚠ 评估问题时出错: {question_data['question'][:50]}... - {e}")
                continue
        
        # 计算平均指标
        summary = self._calculate_summary_metrics(all_results, k_values)
        
        return {
            'summary': summary,
            'detailed_results': all_results,
            'total_questions': len(all_results)
        }
    
    def _calculate_summary_metrics(self, results: List[Dict], k_values: List[int]) -> Dict:
        """计算汇总指标"""
        summary = {
            'original_system': defaultdict(list),
            'enhanced_system': defaultdict(list)
        }
        
        # 收集所有指标
        for result in results:
            for system in ['original_system', 'enhanced_system']:
                for metric_name, metric_value in result[system]['metrics'].items():
                    summary[system][metric_name].append(metric_value)
        
        # 计算平均值和标准差
        final_summary = {}
        for system in ['original_system', 'enhanced_system']:
            final_summary[system] = {}
            for metric_name, values in summary[system].items():
                if values:
                    final_summary[system][metric_name] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'count': len(values)
                    }
        
        return final_summary
    
    def save_evaluation_results(self, results: Dict, output_dir: str = None):
        """
        保存评估结果到本地磁盘
        
        Args:
            results: 评估结果字典
            output_dir: 输出目录，默认使用config中的配置
        """
        import config
        from datetime import datetime
        
        # 确定输出目录
        if output_dir is None:
            output_dir = config.EVALUATION_OUTPUT_DIR
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存完整的评估结果
        full_results_file = output_path / f"full_evaluation_results_{timestamp}.json"
        with open(full_results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        # 2. 保存汇总指标
        summary_file = output_path / f"evaluation_summary_{timestamp}.json"
        summary_data = {
            'timestamp': timestamp,
            'total_questions': results['total_questions'],
            'summary_metrics': results['summary'],
            'evaluation_config': {
                'sample_size': config.EVALUATION_SAMPLE_SIZE,
                'k_values': config.EVALUATION_K_VALUES,
                'embedding_model': config.EMBEDDING_MODEL
            }
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 3. 保存问题和答案对比
        self._save_qa_comparison(results, output_path, timestamp)
        
        # 4. 保存CSV格式的指标对比
        self._save_metrics_csv(results['summary'], output_path, timestamp)
        
        # 5. 保存详细结果（如果配置允许）
        if config.SAVE_DETAILED_RESULTS:
            detailed_file = output_path / f"detailed_results_{timestamp}.json"
            detailed_data = {
                'timestamp': timestamp,
                'detailed_results': results['detailed_results']
            }
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 6. 生成Markdown报告
        self._generate_markdown_report(results, output_path, timestamp)
        
        # 7. 保存可视化图表（如果配置允许）
        if config.SAVE_SUMMARY_CHARTS:
            self._save_visualization_charts(results['summary'], output_path, timestamp)
        
        print(f"💾 评估结果已保存到目录: {output_path}")
        print(f"📁 生成的文件:")
        print(f"   - 完整结果: {full_results_file.name}")
        print(f"   - 汇总指标: {summary_file.name}")
        print(f"   - 问答对比: qa_comparison_{timestamp}.json")
        print(f"   - 问答对比(易读): qa_comparison_{timestamp}.txt")
        print(f"   - CSV对比: metrics_comparison_{timestamp}.csv")
        print(f"   - Markdown报告: evaluation_report_{timestamp}.md")
        if config.SAVE_DETAILED_RESULTS:
            print(f"   - 详细结果: detailed_results_{timestamp}.json")
        if config.SAVE_SUMMARY_CHARTS:
            print(f"   - 可视化图表: charts_{timestamp}/")
    
    def _save_qa_comparison(self, results: Dict, output_path: Path, timestamp: str):
        """
        保存问题和两个系统答案的对比
        
        Args:
            results: 完整的评估结果
            output_path: 输出路径
            timestamp: 时间戳
        """
        # 1. 保存JSON格式（便于程序处理）
        qa_comparison_file = output_path / f"qa_comparison_{timestamp}.json"
        
        qa_comparisons = []
        
        for result in results.get('detailed_results', []):
            qa_comparison = {
                'question': result['question'],
                'expected_answer': result['expected_answer'],
                'question_type': result.get('question_type', 'unknown'),
                'original_system': {
                    'final_answer': result['original_system']['final_answer'],
                    'rewritten_query': result['original_system'].get('rewritten_query', ''),
                    'best_metrics': self._get_best_metrics(result['original_system']['metrics'])
                },
                'enhanced_system': {
                    'final_answer': result['enhanced_system']['final_answer'],
                    'rewritten_query': result['enhanced_system'].get('rewritten_query', ''),
                    'best_metrics': self._get_best_metrics(result['enhanced_system']['metrics'])
                },
                'improvement': self._calculate_improvement(
                    result['original_system']['metrics'],
                    result['enhanced_system']['metrics']
                )
            }
            qa_comparisons.append(qa_comparison)
        
        # 保存JSON格式
        with open(qa_comparison_file, 'w', encoding='utf-8') as f:
            json.dump(qa_comparisons, f, ensure_ascii=False, indent=2)
        
        # 2. 保存易读的文本格式
        txt_comparison_file = output_path / f"qa_comparison_{timestamp}.txt"
        with open(txt_comparison_file, 'w', encoding='utf-8') as f:
            f.write("问题和答案对比报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间: {results.get('timestamp', timestamp)}\n")
            f.write(f"总问题数: {results.get('total_questions', len(qa_comparisons))}\n\n")
            
            for i, qa in enumerate(qa_comparisons, 1):
                f.write(f"问题 {i}:\n")
                f.write("-" * 40 + "\n")
                f.write(f"问题: {qa['question']}\n")
                f.write(f"期望答案: {qa['expected_answer']}\n")
                f.write(f"问题类型: {qa['question_type']}\n\n")
                
                f.write("原始系统:\n")
                f.write(f"  重写查询: {qa['original_system']['rewritten_query']}\n")
                f.write(f"  最终答案: {qa['original_system']['final_answer']}\n")
                f.write(f"  最佳指标: {qa['original_system']['best_metrics']}\n\n")
                
                f.write("增强系统:\n")
                f.write(f"  重写查询: {qa['enhanced_system']['rewritten_query']}\n")
                f.write(f"  最终答案: {qa['enhanced_system']['final_answer']}\n")
                f.write(f"  最佳指标: {qa['enhanced_system']['best_metrics']}\n\n")
                
                f.write("改进情况:\n")
                for metric, improvement in qa['improvement'].items():
                    f.write(f"  {metric}: {improvement:+.1f}%\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
        
        # 3. 保存简化的CSV格式（便于Excel查看）
        csv_comparison_file = output_path / f"qa_comparison_{timestamp}.csv"
        import csv
        
        with open(csv_comparison_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                '问题', '期望答案', '问题类型',
                '原始系统答案', '增强系统答案',
                '原始系统重写查询', '增强系统重写查询',
                'Precision改进%', 'Recall改进%', 'nDCG改进%'
            ])
            
            # 写入数据行
            for qa in qa_comparisons:
                writer.writerow([
                    qa['question'],
                    qa['expected_answer'],
                    qa['question_type'],
                    qa['original_system']['final_answer'],
                    qa['enhanced_system']['final_answer'],
                    qa['original_system']['rewritten_query'],
                    qa['enhanced_system']['rewritten_query'],
                    f"{qa['improvement'].get('precision', 0):.1f}",
                    f"{qa['improvement'].get('recall', 0):.1f}",
                    f"{qa['improvement'].get('ndcg', 0):.1f}"
                ])
    
    def _get_best_metrics(self, metrics: Dict) -> Dict:
        """获取最佳K值的指标"""
        best_metrics = {}
        for k_key, k_metrics in metrics.items():
            if isinstance(k_metrics, dict):
                for metric_name, value in k_metrics.items():
                    if metric_name not in best_metrics or value > best_metrics[metric_name]:
                        best_metrics[metric_name] = value
        return best_metrics
    
    def _calculate_improvement(self, original_metrics: Dict, enhanced_metrics: Dict) -> Dict:
        """计算改进幅度"""
        original_best = self._get_best_metrics(original_metrics)
        enhanced_best = self._get_best_metrics(enhanced_metrics)
        
        improvement = {}
        for metric in ['precision', 'recall', 'ndcg']:
            original_val = original_best.get(metric, 0)
            enhanced_val = enhanced_best.get(metric, 0)
            
            if original_val > 0:
                improvement[metric] = ((enhanced_val - original_val) / original_val) * 100
            else:
                improvement[metric] = 0 if enhanced_val == 0 else 100
        
        return improvement

    def _save_metrics_csv(self, summary: Dict, output_path: Path, timestamp: str):
        """保存指标对比的CSV文件"""
        import csv
        
        csv_file = output_path / f"metrics_comparison_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow(['System', 'Metric', 'K', 'Mean', 'Std', 'Count'])
            
            # 写入数据
            for system_name in ['original_system', 'enhanced_system']:
                if system_name in summary:
                    system_data = summary[system_name]
                    system_display_name = '原始系统' if system_name == 'original_system' else '增强系统'
                    
                    for metric_name, metric_data in system_data.items():
                        # 解析指标名称 (如 "precision@1")
                        if '@' in metric_name:
                            metric_type, k_value = metric_name.split('@')
                            writer.writerow([
                                system_display_name,
                                metric_type.upper(),
                                k_value,
                                f"{metric_data['mean']:.4f}",
                                f"{metric_data['std']:.4f}",
                                metric_data['count']
                            ])
    
    def _generate_markdown_report(self, results: Dict, output_path: Path, timestamp: str):
        """生成Markdown格式的评估报告"""
        report_file = output_path / f"evaluation_report_{timestamp}.md"
        
        summary = results['summary']
        total_questions = results['total_questions']
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 检索系统评估报告\n\n")
            f.write(f"**生成时间**: {timestamp}\n")
            f.write(f"**评估问题数**: {total_questions}\n")
            f.write(f"**嵌入模型**: {config.EMBEDDING_MODEL}\n\n")
            
            # 系统对比表格
            f.write("## 📊 系统性能对比\n\n")
            
            # 为每个K值创建对比表格
            k_values = [1, 3, 5, 10]
            for k in k_values:
                f.write(f"### K={k} 指标对比\n\n")
                f.write("| 指标 | 原始系统 | 增强系统 | 改进幅度 |\n")
                f.write("|------|----------|----------|----------|\n")
                
                for metric_type in ['precision', 'recall', 'ndcg']:
                    metric_key = f'{metric_type}@{k}'
                    
                    if ('original_system' in summary and metric_key in summary['original_system'] and
                        'enhanced_system' in summary and metric_key in summary['enhanced_system']):
                        
                        orig_val = summary['original_system'][metric_key]['mean']
                        enh_val = summary['enhanced_system'][metric_key]['mean']
                        
                        if orig_val > 0:
                            improvement = ((enh_val - orig_val) / orig_val) * 100
                            improvement_str = f"{improvement:+.2f}%"
                        else:
                            improvement_str = "N/A"
                        
                        f.write(f"| {metric_type.upper()}@{k} | {orig_val:.4f} | {enh_val:.4f} | {improvement_str} |\n")
                
                f.write("\n")
            
            # 详细统计信息
            f.write("## 📈 详细统计信息\n\n")
            
            for system_name, system_display in [('original_system', '原始系统'), ('enhanced_system', '增强系统')]:
                if system_name in summary:
                    f.write(f"### {system_display}\n\n")
                    f.write("| 指标 | 均值 | 标准差 | 样本数 |\n")
                    f.write("|------|------|--------|--------|\n")
                    
                    system_data = summary[system_name]
                    for metric_name, metric_data in sorted(system_data.items()):
                        f.write(f"| {metric_name} | {metric_data['mean']:.4f} | {metric_data['std']:.4f} | {metric_data['count']} |\n")
                    
                    f.write("\n")
            
            # 结论和建议
            f.write("## 💡 结论和建议\n\n")
            
            # 计算总体改进情况
            improvements = []
            if 'original_system' in summary and 'enhanced_system' in summary:
                for k in k_values:
                    for metric_type in ['precision', 'recall', 'ndcg']:
                        metric_key = f'{metric_type}@{k}'
                        if (metric_key in summary['original_system'] and 
                            metric_key in summary['enhanced_system']):
                            orig_val = summary['original_system'][metric_key]['mean']
                            enh_val = summary['enhanced_system'][metric_key]['mean']
                            if orig_val > 0:
                                improvement = ((enh_val - orig_val) / orig_val) * 100
                                improvements.append(improvement)
            
            if improvements:
                avg_improvement = sum(improvements) / len(improvements)
                if avg_improvement > 5:
                    f.write("✅ **增强系统表现显著优于原始系统**\n\n")
                elif avg_improvement > 0:
                    f.write("✅ **增强系统表现略优于原始系统**\n\n")
                else:
                    f.write("⚠️ **增强系统表现与原始系统相当或略差**\n\n")
                
                f.write(f"- 平均改进幅度: {avg_improvement:.2f}%\n")
                f.write(f"- 最大改进幅度: {max(improvements):.2f}%\n")
                f.write(f"- 最小改进幅度: {min(improvements):.2f}%\n\n")
            
            f.write("### 改进建议\n\n")
            f.write("1. **继续优化重排算法**: 调整多信号融合的权重\n")
            f.write("2. **扩展训练数据**: 增加更多样化的问题类型\n")
            f.write("3. **优化嵌入模板**: 进一步改进自然语言模板\n")
            f.write("4. **引入用户反馈**: 基于实际使用反馈持续优化\n")
    
    def _save_visualization_charts(self, summary: Dict, output_path: Path, timestamp: str):
        """保存可视化图表"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 创建图表目录
            charts_dir = output_path / f"charts_{timestamp}"
            charts_dir.mkdir(exist_ok=True)
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 1. 指标对比柱状图
            self._create_metrics_bar_chart(summary, charts_dir)
            
            # 2. K值趋势图
            self._create_k_trend_chart(summary, charts_dir)
            
            # 3. 改进幅度图
            self._create_improvement_chart(summary, charts_dir)
            
            print(f"📊 可视化图表已保存到: {charts_dir}")
            
        except ImportError:
            print("⚠️ matplotlib未安装，跳过图表生成")
        except Exception as e:
            print(f"⚠️ 图表生成失败: {e}")
    
    def _create_metrics_bar_chart(self, summary: Dict, charts_dir: Path):
        """创建指标对比柱状图"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('检索系统性能对比', fontsize=16, fontweight='bold')
        
        k_values = [1, 3, 5, 10]
        metrics = ['precision', 'recall', 'ndcg']
        
        for i, k in enumerate(k_values):
            ax = axes[i//2, i%2]
            
            x = np.arange(len(metrics))
            width = 0.35
            
            orig_values = []
            enh_values = []
            
            for metric in metrics:
                metric_key = f'{metric}@{k}'
                orig_val = summary.get('original_system', {}).get(metric_key, {}).get('mean', 0)
                enh_val = summary.get('enhanced_system', {}).get(metric_key, {}).get('mean', 0)
                orig_values.append(orig_val)
                enh_values.append(enh_val)
            
            ax.bar(x - width/2, orig_values, width, label='原始系统', alpha=0.8)
            ax.bar(x + width/2, enh_values, width, label='增强系统', alpha=0.8)
            
            ax.set_xlabel('指标类型')
            ax.set_ylabel('分数')
            ax.set_title(f'K={k} 指标对比')
            ax.set_xticks(x)
            ax.set_xticklabels([m.upper() for m in metrics])
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(charts_dir / 'metrics_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_k_trend_chart(self, summary: Dict, charts_dir: Path):
        """创建K值趋势图"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('不同K值下的性能趋势', fontsize=16, fontweight='bold')
        
        k_values = [1, 3, 5, 10]
        metrics = ['precision', 'recall', 'ndcg']
        
        for i, metric in enumerate(metrics):
            ax = axes[i]
            
            orig_values = []
            enh_values = []
            
            for k in k_values:
                metric_key = f'{metric}@{k}'
                orig_val = summary.get('original_system', {}).get(metric_key, {}).get('mean', 0)
                enh_val = summary.get('enhanced_system', {}).get(metric_key, {}).get('mean', 0)
                orig_values.append(orig_val)
                enh_values.append(enh_val)
            
            ax.plot(k_values, orig_values, 'o-', label='原始系统', linewidth=2, markersize=8)
            ax.plot(k_values, enh_values, 's-', label='增强系统', linewidth=2, markersize=8)
            
            ax.set_xlabel('K值')
            ax.set_ylabel(f'{metric.upper()}分数')
            ax.set_title(f'{metric.upper()}@K 趋势')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(k_values)
        
        plt.tight_layout()
        plt.savefig(charts_dir / 'k_trend_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_improvement_chart(self, summary: Dict, charts_dir: Path):
        """创建改进幅度图"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        k_values = [1, 3, 5, 10]
        metrics = ['precision', 'recall', 'ndcg']
        
        improvements = []
        labels = []
        
        for k in k_values:
            for metric in metrics:
                metric_key = f'{metric}@{k}'
                if (summary.get('original_system', {}).get(metric_key) and 
                    summary.get('enhanced_system', {}).get(metric_key)):
                    
                    orig_val = summary['original_system'][metric_key]['mean']
                    enh_val = summary['enhanced_system'][metric_key]['mean']
                    
                    if orig_val > 0:
                        improvement = ((enh_val - orig_val) / orig_val) * 100
                        improvements.append(improvement)
                        labels.append(f'{metric.upper()}@{k}')
        
        if improvements:
            colors = ['green' if imp > 0 else 'red' for imp in improvements]
            
            bars = ax.barh(labels, improvements, color=colors, alpha=0.7)
            
            # 添加数值标签
            for bar, imp in zip(bars, improvements):
                width = bar.get_width()
                ax.text(width + (0.5 if width > 0 else -0.5), bar.get_y() + bar.get_height()/2, 
                       f'{imp:+.1f}%', ha='left' if width > 0 else 'right', va='center')
            
            ax.set_xlabel('改进幅度 (%)')
            ax.set_title('增强系统相对于原始系统的改进幅度', fontsize=14, fontweight='bold')
            ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(charts_dir / 'improvement_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def print_summary_report(self, results: Dict):
        """打印汇总报告"""
        summary = results['summary']
        total_questions = results['total_questions']
        
        print(f"\n📊 评估报告 (共 {total_questions} 个问题)")
        print("=" * 80)
        
        # 对比两个系统
        systems = [
            ('原始系统', 'original_system'),
            ('增强系统', 'enhanced_system')
        ]
        
        for system_name, system_key in systems:
            print(f"\n🔍 {system_name}:")
            print("-" * 40)
            
            if system_key in summary:
                metrics = summary[system_key]
                
                # 按K值分组显示
                k_values = [1, 3, 5, 10]
                for k in k_values:
                    print(f"\n  K={k}:")
                    
                    for metric_type in ['precision', 'recall', 'ndcg']:
                        metric_key = f'{metric_type}@{k}'
                        if metric_key in metrics:
                            mean_val = metrics[metric_key]['mean']
                            std_val = metrics[metric_key]['std']
                            print(f"    {metric_type.upper()}@{k}: {mean_val:.4f} (±{std_val:.4f})")
        
        # 计算改进幅度
        print(f"\n📈 改进幅度:")
        print("-" * 40)
        
        if 'original_system' in summary and 'enhanced_system' in summary:
            orig_metrics = summary['original_system']
            enh_metrics = summary['enhanced_system']
            
            for k in [1, 3, 5, 10]:
                print(f"\n  K={k}:")
                for metric_type in ['precision', 'recall', 'ndcg']:
                    metric_key = f'{metric_type}@{k}'
                    if metric_key in orig_metrics and metric_key in enh_metrics:
                        orig_val = orig_metrics[metric_key]['mean']
                        enh_val = enh_metrics[metric_key]['mean']
                        
                        if orig_val > 0:
                            improvement = ((enh_val - orig_val) / orig_val) * 100
                            print(f"    {metric_type.upper()}@{k}: {improvement:+.2f}%")

# 主评估函数
def run_comprehensive_evaluation():
    """运行全面的评估"""
    print("🚀 启动检索系统全面评估")
    print("🎯 评估内容: Precision@K, Recall@K, nDCG@K")
    print("📊 对比系统: 原始系统 vs 增强系统")
    print("=" * 60)
    
    # 初始化评估器
    evaluator = RetrievalEvaluator()
    
    # 加载评估数据
    import config
    questions = evaluator.load_qa_dataset(limit=config.EVALUATION_SAMPLE_SIZE)
    
    if not questions:
        print("❌ 无法加载评估数据")
        print("💡 请确保qa_datasets目录中有QA数据文件")
        return
    
    # 运行评估
    print(f"🔄 开始评估 {len(questions)} 个问题...")
    results = evaluator.evaluate_dataset(questions, k_values=config.EVALUATION_K_VALUES)
    
    # 保存结果到本地磁盘
    print(f"\n💾 保存评估结果...")
    evaluator.save_evaluation_results(results)
    
    # 打印控制台报告
    evaluator.print_summary_report(results)
    
    print(f"\n✅ 评估完成！")
    print(f"📁 所有结果已保存到 {config.EVALUATION_OUTPUT_DIR}/ 目录")
    print(f"📊 包含JSON、CSV、Markdown报告和可视化图表")

def run_quick_evaluation(sample_size: int = 20):
    """运行快速评估（少量样本）"""
    print("⚡ 启动快速评估")
    print(f"📊 样本数量: {sample_size}")
    print("=" * 40)
    
    evaluator = RetrievalEvaluator()
    
    # 加载少量数据进行快速测试
    questions = evaluator.load_qa_dataset(limit=sample_size)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    # 运行评估
    results = evaluator.evaluate_dataset(questions, k_values=[1, 3, 5])
    
    # 保存结果
    evaluator.save_evaluation_results(results)
    
    # 打印简化报告
    evaluator.print_summary_report(results)
    
    print(f"\n✅ 快速评估完成！")

def run_scan_all_evaluation(dataset_path: str = "qa_datasets", k_values: list = None, output_dir: str = None):
    """运行全量扫描评估 - 扫描QA数据集的全部数据"""
    import config
    
    k_values = k_values or config.EVALUATION_K_VALUES
    
    print("🔍 启动全量扫描评估")
    print(f"� 数自据集路径: {dataset_path}")
    print(f"� K本值: {k_values}")
    print("=" * 50)
    
    evaluator = RetrievalEvaluator()
    
    # 加载全部数据
    questions = evaluator.load_qa_dataset(dataset_path=dataset_path, scan_all=True)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    print(f"\n🚀 开始评估 {len(questions)} 个问题...")
    print("⚠️ 注意: 全量评估可能需要较长时间，请耐心等待")
    
    # 运行评估
    results = evaluator.evaluate_dataset(questions, k_values=k_values)
    
    # 保存结果
    if output_dir:
        evaluator.save_evaluation_results(results, output_dir)
    else:
        evaluator.save_evaluation_results(results)
    
    # 打印详细报告
    evaluator.print_summary_report(results)
    
    # 打印数据集统计信息
    print(f"\n📊 数据集统计信息:")
    question_types = {}
    source_files = {}
    
    for q in questions:
        q_type = q.get('question_type', 'unknown')
        source_file = q.get('source_file', 'unknown')
        
        question_types[q_type] = question_types.get(q_type, 0) + 1
        source_files[source_file] = source_files.get(source_file, 0) + 1
    
    print(f"   问题类型分布:")
    for q_type, count in sorted(question_types.items()):
        percentage = (count / len(questions)) * 100
        print(f"     - {q_type}: {count} ({percentage:.1f}%)")
    
    print(f"   数据文件分布:")
    for source_file, count in sorted(source_files.items()):
        percentage = (count / len(questions)) * 100
        print(f"     - {source_file}: {count} ({percentage:.1f}%)")
    
    print(f"\n✅ 全量扫描评估完成！")

def run_custom_evaluation(sample_size: int = None, k_values: list = None, output_dir: str = None):
    """运行自定义评估"""
    import config
    
    sample_size = sample_size or config.EVALUATION_SAMPLE_SIZE
    k_values = k_values or config.EVALUATION_K_VALUES
    
    print("🔧 启动自定义评估")
    print(f"📊 样本数量: {sample_size}")
    print(f"📈 K值: {k_values}")
    print("=" * 40)
    
    evaluator = RetrievalEvaluator()
    
    # 加载数据
    questions = evaluator.load_qa_dataset(limit=sample_size)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    # 运行评估
    results = evaluator.evaluate_dataset(questions, k_values=k_values)
    
    # 保存结果
    if output_dir:
        evaluator.save_evaluation_results(results, output_dir)
    else:
        evaluator.save_evaluation_results(results)
    
    # 打印报告
    evaluator.print_summary_report(results)
    
    print(f"\n✅ 自定义评估完成！")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="检索系统评估")
    parser.add_argument('--mode', choices=['full', 'quick', 'custom', 'scan-all'], default='full',
                       help='评估模式: full(完整评估), quick(快速评估), custom(自定义评估), scan-all(全量扫描)')
    parser.add_argument('--sample-size', type=int, default=None,
                       help='评估样本数量 (scan-all模式下忽略)')
    parser.add_argument('--k-values', nargs='+', type=int, default=None,
                       help='K值列表，如: --k-values 1 3 5 10')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='输出目录')
    parser.add_argument('--qa-path', type=str, default="qa_datasets",
                       help='QA数据集路径 (默认: qa_datasets)')
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        run_comprehensive_evaluation()
    elif args.mode == 'quick':
        sample_size = args.sample_size or 20
        run_quick_evaluation(sample_size)
    elif args.mode == 'custom':
        run_custom_evaluation(
            sample_size=args.sample_size,
            k_values=args.k_values,
            output_dir=args.output_dir
        )
    elif args.mode == 'scan-all':
        run_scan_all_evaluation(
            dataset_path=args.qa_path,
            k_values=args.k_values,
            output_dir=args.output_dir
        )