# evaluation_engine.py - 评估引擎

import json
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from retrieval_engine import RetrievalEngine
from qa_generator import QAGenerator
import config

class EvaluationEngine:
    """评估引擎 - 评估新系统的性能"""
    
    def __init__(self):
        self.retrieval_engine = RetrievalEngine()
        self.qa_generator = QAGenerator()
        self.evaluation_dir = Path(config.QA_EVALUATION_DIR)
        self.evaluation_dir.mkdir(exist_ok=True)
    
    def calculate_precision_at_k(self, retrieved_items: List[Dict], ground_truth: Dict, k: int = 5) -> float:
        """计算Precision@K"""
        if not retrieved_items or k <= 0:
            return 0.0
        
        # 取前k个结果
        top_k_items = retrieved_items[:k]
        
        # 检查相关性（基于三元组匹配）
        relevant_count = 0
        ground_truth_triple = ground_truth.get('triple', ())
        
        for item in top_k_items:
            item_triple = item.get('triple', ())
            # 如果三元组的任何部分匹配，认为是相关的
            if any(gt_part in item_triple for gt_part in ground_truth_triple if gt_part):
                relevant_count += 1
        
        return relevant_count / k
    
    def calculate_recall_at_k(self, retrieved_items: List[Dict], ground_truth: Dict, k: int = 5) -> float:
        """计算Recall@K"""
        if not retrieved_items or k <= 0:
            return 0.0
        
        # 假设只有一个相关文档（ground truth）
        top_k_items = retrieved_items[:k]
        ground_truth_triple = ground_truth.get('triple', ())
        
        # 检查是否找到了相关文档
        for item in top_k_items:
            item_triple = item.get('triple', ())
            if any(gt_part in item_triple for gt_part in ground_truth_triple if gt_part):
                return 1.0
        
        return 0.0
    
    def calculate_ndcg_at_k(self, retrieved_items: List[Dict], ground_truth: Dict, k: int = 5) -> float:
        """计算nDCG@K"""
        if not retrieved_items or k <= 0:
            return 0.0
        
        top_k_items = retrieved_items[:k]
        ground_truth_triple = ground_truth.get('triple', ())
        
        # 计算相关性分数（0或1）
        relevance_scores = []
        for item in top_k_items:
            item_triple = item.get('triple', ())
            if any(gt_part in item_triple for gt_part in ground_truth_triple if gt_part):
                relevance_scores.append(1.0)
            else:
                relevance_scores.append(0.0)
        
        # 计算DCG
        dcg = 0.0
        for i, score in enumerate(relevance_scores):
            dcg += score / np.log2(i + 2)  # i+2 because log2(1) = 0
        
        # 计算IDCG（理想情况下的DCG）
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = 0.0
        for i, score in enumerate(ideal_scores):
            idcg += score / np.log2(i + 2)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def evaluate_single_qa(self, qa_pair: Dict, k_values: List[int] = [1, 3, 5]) -> Dict:
        """评估单个QA对"""
        question = qa_pair['question']
        
        # 使用检索引擎获取结果
        result = self.retrieval_engine.retrieve_and_rewrite(question, n_results=max(k_values))
        
        # 计算各种指标
        metrics = {
            'question': question,
            'answer': qa_pair['answer'],
            'question_type': qa_pair.get('question_type', 'general'),
            'retrieved_count': len(result['retrieved_items']),
            'cotkr_knowledge': result['cotkr_knowledge'],
            'final_answer': result['final_answer']
        }
        
        # 为每个k值计算指标
        for k in k_values:
            metrics[f'precision_at_{k}'] = self.calculate_precision_at_k(
                result['retrieved_items'], qa_pair, k
            )
            metrics[f'recall_at_{k}'] = self.calculate_recall_at_k(
                result['retrieved_items'], qa_pair, k
            )
            metrics[f'ndcg_at_{k}'] = self.calculate_ndcg_at_k(
                result['retrieved_items'], qa_pair, k
            )
        
        return metrics
    
    def evaluate_qa_dataset(self, qa_dataset: List[Dict], k_values: List[int] = [1, 3, 5]) -> Dict:
        """评估整个QA数据集"""
        print(f"🔄 开始评估 {len(qa_dataset)} 个QA对")
        
        all_metrics = []
        start_time = time.time()
        
        for i, qa_pair in enumerate(qa_dataset):
            if i % 10 == 0:
                print(f"  进度: {i}/{len(qa_dataset)}")
            
            metrics = self.evaluate_single_qa(qa_pair, k_values)
            all_metrics.append(metrics)
        
        # 计算平均指标
        avg_metrics = self._calculate_average_metrics(all_metrics, k_values)
        
        # 按问题类型分组统计
        type_metrics = self._calculate_metrics_by_type(all_metrics, k_values)
        
        evaluation_time = time.time() - start_time
        
        evaluation_result = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_questions': len(qa_dataset),
            'evaluation_time_seconds': evaluation_time,
            'average_metrics': avg_metrics,
            'metrics_by_type': type_metrics,
            'detailed_results': all_metrics
        }
        
        print(f"✅ 评估完成，耗时 {evaluation_time:.2f} 秒")
        return evaluation_result
    
    def _calculate_average_metrics(self, all_metrics: List[Dict], k_values: List[int]) -> Dict:
        """计算平均指标"""
        avg_metrics = {}
        
        for k in k_values:
            precision_key = f'precision_at_{k}'
            recall_key = f'recall_at_{k}'
            ndcg_key = f'ndcg_at_{k}'
            
            precisions = [m[precision_key] for m in all_metrics if precision_key in m]
            recalls = [m[recall_key] for m in all_metrics if recall_key in m]
            ndcgs = [m[ndcg_key] for m in all_metrics if ndcg_key in m]
            
            avg_metrics[precision_key] = np.mean(precisions) if precisions else 0.0
            avg_metrics[recall_key] = np.mean(recalls) if recalls else 0.0
            avg_metrics[ndcg_key] = np.mean(ndcgs) if ndcgs else 0.0
        
        return avg_metrics
    
    def _calculate_metrics_by_type(self, all_metrics: List[Dict], k_values: List[int]) -> Dict:
        """按问题类型计算指标"""
        type_metrics = {}
        
        # 按类型分组
        metrics_by_type = {}
        for metric in all_metrics:
            q_type = metric.get('question_type', 'general')
            if q_type not in metrics_by_type:
                metrics_by_type[q_type] = []
            metrics_by_type[q_type].append(metric)
        
        # 为每种类型计算平均指标
        for q_type, type_metrics_list in metrics_by_type.items():
            type_metrics[q_type] = {
                'count': len(type_metrics_list),
                'metrics': self._calculate_average_metrics(type_metrics_list, k_values)
            }
        
        return type_metrics
    
    def save_evaluation_results(self, results: Dict, filename: str = None) -> str:
        """保存评估结果"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"evaluation_results_{timestamp}.json"
        
        filepath = self.evaluation_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 评估结果已保存到: {filepath}")
        return str(filepath)
    
    def load_evaluation_results(self, filename: str) -> Dict:
        """加载评估结果"""
        filepath = self.evaluation_dir / filename
        
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            return {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"📖 已加载评估结果: {filename}")
        return results
    
    def print_evaluation_summary(self, results: Dict):
        """打印评估结果摘要"""
        print("\n" + "="*60)
        print("📊 新系统评估结果摘要")
        print("="*60)
        
        avg_metrics = results.get('average_metrics', {})
        
        print(f"总问题数: {results.get('total_questions', 0)}")
        print(f"评估时间: {results.get('evaluation_time_seconds', 0):.2f} 秒")
        
        print("\n平均指标:")
        for metric_name, value in avg_metrics.items():
            print(f"  {metric_name}: {value:.4f}")
        
        print("\n按问题类型统计:")
        type_metrics = results.get('metrics_by_type', {})
        for q_type, type_data in type_metrics.items():
            print(f"\n  {q_type} ({type_data['count']} 个问题):")
            for metric_name, value in type_data['metrics'].items():
                print(f"    {metric_name}: {value:.4f}")

# 测试函数
def test_evaluation_engine():
    """测试评估引擎"""
    evaluator = EvaluationEngine()
    
    # 生成小规模测试数据集
    print("🔄 生成测试QA数据集")
    qa_dataset = evaluator.qa_generator.generate_qa_dataset(max_entries=5)
    
    if qa_dataset:
        # 评估数据集
        results = evaluator.evaluate_qa_dataset(qa_dataset, k_values=[1, 3, 5])
        
        # 打印摘要
        evaluator.print_evaluation_summary(results)
        
        # 保存结果
        evaluator.save_evaluation_results(results, "test_evaluation.json")

if __name__ == '__main__':
    test_evaluation_engine()