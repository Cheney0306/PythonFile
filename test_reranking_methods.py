#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新旧重排方法性能对比
从QA数据集中随机选择100个问题，测试recall@k和nDCG@k性能
"""

import json
import random
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from tqdm import tqdm
import time

from enhanced_embedding_system import EnhancedVectorDatabaseManager

class RerankingMethodComparator:
    """重排方法对比器"""
    
    def __init__(self):
        self.db_manager = EnhancedVectorDatabaseManager()
        self.db_manager.initialize_collection()
        
    def load_qa_questions(self, max_questions: int = 100) -> List[Dict]:
        """从QA数据集中加载问题"""
        qa_files = list(Path("qa_datasets").glob("*.json"))
        
        if not qa_files:
            print("❌ 未找到QA数据集文件")
            return []
        
        all_questions = []
        
        for qa_file in qa_files:
            try:
                with open(qa_file, 'r', encoding='utf-8') as f:
                    qa_data = json.load(f)
                
                for item in qa_data:
                    if isinstance(item, dict) and 'question' in item and 'answer' in item:
                        all_questions.append({
                            'question': item['question'],
                            'answer': item['answer'],
                            'source_file': qa_file.name
                        })
                        
            except Exception as e:
                print(f"⚠️ 读取文件 {qa_file} 失败: {e}")
                continue
        
        if not all_questions:
            print("❌ 没有找到有效的QA问题")
            return []
        
        # 随机选择指定数量的问题
        if len(all_questions) > max_questions:
            selected_questions = random.sample(all_questions, max_questions)
        else:
            selected_questions = all_questions
        
        print(f"✅ 加载了 {len(selected_questions)} 个测试问题")
        return selected_questions
    
    def calculate_precision_at_k(self, retrieved_items: List[Dict], expected_answer: str, k_values: List[int], original_triple: List[str] = None) -> Dict[str, float]:
        """计算Precision@K指标"""
        precision_scores = {}
        
        for k in k_values:
            relevant_count = 0
            top_k_items = retrieved_items[:k]
            
            for item in top_k_items:
                # 检查检索项是否与期望答案相关
                if self._is_relevant(item, expected_answer, original_triple):
                    relevant_count += 1
            
            # Precision@K = 相关文档数 / K
            precision_scores[f'precision@{k}'] = relevant_count / k if k > 0 else 0.0
        
        return precision_scores
    
    def calculate_recall_at_k(self, retrieved_items: List[Dict], expected_answer: str, k_values: List[int], original_triple: List[str] = None) -> Dict[str, float]:
        """计算Recall@K指标"""
        recall_scores = {}
        
        for k in k_values:
            relevant_count = 0
            top_k_items = retrieved_items[:k]
            
            for item in top_k_items:
                # 检查检索项是否与期望答案相关
                if self._is_relevant(item, expected_answer, original_triple):
                    relevant_count += 1
            
            # Recall@K = 相关文档数 / 总相关文档数 (这里假设总相关文档数为1)
            recall_scores[f'recall@{k}'] = min(relevant_count, 1)  # 最多为1
        
        return recall_scores
    
    def calculate_ndcg_at_k(self, retrieved_items: List[Dict], expected_answer: str, k_values: List[int], original_triple: List[str] = None) -> Dict[str, float]:
        """计算nDCG@K指标"""
        ndcg_scores = {}
        
        for k in k_values:
            top_k_items = retrieved_items[:k]
            
            # 计算DCG@K
            dcg = 0.0
            for i, item in enumerate(top_k_items):
                relevance = self._get_relevance_score(item, expected_answer, original_triple)
                dcg += relevance / np.log2(i + 2)  # i+2 因为log2(1)=0
            
            # 计算IDCG@K (理想情况下的DCG)
            idcg = 1.0 / np.log2(2)  # 假设只有1个相关文档，且在第1位
            
            # nDCG@K = DCG@K / IDCG@K
            ndcg_scores[f'ndcg@{k}'] = dcg / idcg if idcg > 0 else 0.0
        
        return ndcg_scores
    
    def _is_relevant(self, item: Dict, expected_answer: str, original_triple: List[str] = None) -> bool:
        """判断检索项是否与期望答案相关"""
        if original_triple and 'triple' in item:
            # 基于三元组的相关性判断
            retrieved_triple = item['triple']
            relevance_score = self._get_relevance_score(item, expected_answer, original_triple)
            return relevance_score > 0.0
        else:
            # 回退到基于文本的相关性判断
            return self._is_relevant_by_text(item, expected_answer)
    
    def _get_relevance_score(self, item: Dict, expected_answer: str, original_triple: List[str] = None) -> float:
        """获取相关性分数"""
        if original_triple and 'triple' in item:
            # 基于三元组的相关性分数
            retrieved_triple = item['triple']
            return self._calculate_triple_relevance_score(retrieved_triple, original_triple)
        else:
            # 回退到基于文本的相关性分数
            return 1.0 if self._is_relevant_by_text(item, expected_answer) else 0.0
    
    def _calculate_triple_relevance_score(self, retrieved_triple: List[str], original_triple: List[str]) -> float:
        """
        基于三元组计算相关性分数
        
        Args:
            retrieved_triple: 检索到的三元组
            original_triple: 原始三元组
            
        Returns:
            相关性分数: 1.0(完全相关), 0.6(部分相关), 0.0(不相关)
        """
        if not retrieved_triple or not original_triple:
            return 0.0
        
        # 确保两个三元组都有3个元素
        if len(retrieved_triple) != 3 or len(original_triple) != 3:
            return 0.0
        
        # 计算匹配的元素数量
        matches = 0
        for i in range(3):
            if retrieved_triple[i] == original_triple[i]:
                matches += 1
        
        # 相关性分数:
        # - 3个元素完全匹配: 完全相关 (1.0)
        # - 2个元素匹配: 部分相关 (0.6)  
        # - 1个或0个元素匹配: 不相关 (0.0)
        
        if matches == 3:
            return 1.0  # 完全相关
        elif matches == 2:
            return 0.6  # 部分相关
        else:
            return 0.0  # 不相关
    
    def _is_relevant_by_text(self, item: Dict, expected_answer: str) -> bool:
        """基于文本内容判断相关性 (回退方法)"""
        triple = item.get('triple', [])
        text = item.get('text', '')
        document = item.get('document', '')
        
        expected_lower = expected_answer.lower()
        
        # 检查三元组的各个部分
        for part in triple:
            if isinstance(part, str):
                part_clean = part.replace('_', ' ').lower()
                if expected_lower in part_clean or part_clean in expected_lower:
                    return True
        
        # 检查文本内容
        if expected_lower in text.lower() or expected_lower in document.lower():
            return True
        
        return False
    
    def test_single_question(self, question: str, expected_answer: str, original_triple: List[str] = None) -> Dict:
        """测试单个问题的两种重排方法"""
        k_values = [1, 3, 5, 10]
        
        # 测试原有重排方法
        start_time = time.time()
        original_results = self.db_manager.multi_stage_retrieval(
            query=question,
            n_results=10,
            rerank_top_k=40,
            rerank_method='original'
        )
        original_time = time.time() - start_time
        
        # 测试Cross-Encoder重排方法
        start_time = time.time()
        cross_encoder_results = self.db_manager.multi_stage_retrieval(
            query=question,
            n_results=10,
            rerank_top_k=40,
            rerank_method='cross_encoder'
        )
        cross_encoder_time = time.time() - start_time
        
        # 计算指标
        original_precision = self.calculate_precision_at_k(original_results, expected_answer, k_values, original_triple)
        original_recall = self.calculate_recall_at_k(original_results, expected_answer, k_values, original_triple)
        original_ndcg = self.calculate_ndcg_at_k(original_results, expected_answer, k_values, original_triple)
        
        cross_encoder_precision = self.calculate_precision_at_k(cross_encoder_results, expected_answer, k_values, original_triple)
        cross_encoder_recall = self.calculate_recall_at_k(cross_encoder_results, expected_answer, k_values, original_triple)
        cross_encoder_ndcg = self.calculate_ndcg_at_k(cross_encoder_results, expected_answer, k_values, original_triple)
        
        return {
            'question': question,
            'expected_answer': expected_answer,
            'original_method': {
                'precision': original_precision,
                'recall': original_recall,
                'ndcg': original_ndcg,
                'time': original_time,
                'results_count': len(original_results)
            },
            'cross_encoder_method': {
                'precision': cross_encoder_precision,
                'recall': cross_encoder_recall,
                'ndcg': cross_encoder_ndcg,
                'time': cross_encoder_time,
                'results_count': len(cross_encoder_results)
            }
        }
    
    def run_comparison(self, test_questions: List[Dict]) -> Dict:
        """运行完整的对比测试"""
        print(f"🚀 开始重排方法对比测试")
        print(f"📊 测试问题数量: {len(test_questions)}")
        print("=" * 60)
        
        all_results = []
        
        for i, qa_item in enumerate(tqdm(test_questions, desc="测试进度")):
            try:
                # 获取原始三元组信息
                original_triple = qa_item.get('triple', None)
                result = self.test_single_question(qa_item['question'], qa_item['answer'], original_triple)
                result['test_id'] = i + 1
                result['source_file'] = qa_item['source_file']
                all_results.append(result)
                
            except Exception as e:
                print(f"⚠️ 测试问题 {i+1} 失败: {e}")
                continue
        
        # 计算平均指标
        summary = self._calculate_summary_metrics(all_results)
        
        return {
            'summary': summary,
            'detailed_results': all_results,
            'test_info': {
                'total_questions': len(test_questions),
                'successful_tests': len(all_results),
                'failed_tests': len(test_questions) - len(all_results)
            }
        }
    
    def _calculate_summary_metrics(self, results: List[Dict]) -> Dict:
        """计算汇总指标"""
        if not results:
            return {}
        
        k_values = [1, 3, 5, 10]
        
        # 初始化累计值
        original_precision_sum = {f'precision@{k}': 0.0 for k in k_values}
        original_recall_sum = {f'recall@{k}': 0.0 for k in k_values}
        original_ndcg_sum = {f'ndcg@{k}': 0.0 for k in k_values}
        cross_encoder_precision_sum = {f'precision@{k}': 0.0 for k in k_values}
        cross_encoder_recall_sum = {f'recall@{k}': 0.0 for k in k_values}
        cross_encoder_ndcg_sum = {f'ndcg@{k}': 0.0 for k in k_values}
        
        original_time_sum = 0.0
        cross_encoder_time_sum = 0.0
        
        # 累计所有结果
        for result in results:
            for k in k_values:
                original_precision_sum[f'precision@{k}'] += result['original_method']['precision'][f'precision@{k}']
                original_recall_sum[f'recall@{k}'] += result['original_method']['recall'][f'recall@{k}']
                original_ndcg_sum[f'ndcg@{k}'] += result['original_method']['ndcg'][f'ndcg@{k}']
                cross_encoder_precision_sum[f'precision@{k}'] += result['cross_encoder_method']['precision'][f'precision@{k}']
                cross_encoder_recall_sum[f'recall@{k}'] += result['cross_encoder_method']['recall'][f'recall@{k}']
                cross_encoder_ndcg_sum[f'ndcg@{k}'] += result['cross_encoder_method']['ndcg'][f'ndcg@{k}']
            
            original_time_sum += result['original_method']['time']
            cross_encoder_time_sum += result['cross_encoder_method']['time']
        
        # 计算平均值
        n = len(results)
        
        return {
            'original_method': {
                'avg_precision': {k: v/n for k, v in original_precision_sum.items()},
                'avg_recall': {k: v/n for k, v in original_recall_sum.items()},
                'avg_ndcg': {k: v/n for k, v in original_ndcg_sum.items()},
                'avg_time': original_time_sum / n
            },
            'cross_encoder_method': {
                'avg_precision': {k: v/n for k, v in cross_encoder_precision_sum.items()},
                'avg_recall': {k: v/n for k, v in cross_encoder_recall_sum.items()},
                'avg_ndcg': {k: v/n for k, v in cross_encoder_ndcg_sum.items()},
                'avg_time': cross_encoder_time_sum / n
            }
        }
    
    def print_comparison_results(self, comparison_results: Dict):
        """打印对比结果"""
        summary = comparison_results['summary']
        test_info = comparison_results['test_info']
        
        print("\n" + "="*60)
        print("📊 重排方法对比结果")
        print("="*60)
        
        print(f"📈 测试统计:")
        print(f"   - 总问题数: {test_info['total_questions']}")
        print(f"   - 成功测试: {test_info['successful_tests']}")
        print(f"   - 失败测试: {test_info['failed_tests']}")
        
        print(f"\n📋 Precision@K 对比:")
        print(f"{'指标':<12} {'原有方法':<12} {'Cross-Encoder':<15} {'提升':<10}")
        print("-" * 50)
        
        for k in [1, 3, 5, 10]:
            metric = f'precision@{k}'
            original_score = summary['original_method']['avg_precision'][metric]
            cross_encoder_score = summary['cross_encoder_method']['avg_precision'][metric]
            improvement = cross_encoder_score - original_score
            
            print(f"{metric:<12} {original_score:<12.4f} {cross_encoder_score:<15.4f} {improvement:+.4f}")
        
        print(f"\n📋 Recall@K 对比:")
        print(f"{'指标':<12} {'原有方法':<12} {'Cross-Encoder':<15} {'提升':<10}")
        print("-" * 50)
        
        for k in [1, 3, 5, 10]:
            metric = f'recall@{k}'
            original_score = summary['original_method']['avg_recall'][metric]
            cross_encoder_score = summary['cross_encoder_method']['avg_recall'][metric]
            improvement = cross_encoder_score - original_score
            
            print(f"{metric:<12} {original_score:<12.4f} {cross_encoder_score:<15.4f} {improvement:+.4f}")
        
        print(f"\n📋 nDCG@K 对比:")
        print(f"{'指标':<12} {'原有方法':<12} {'Cross-Encoder':<15} {'提升':<10}")
        print("-" * 50)
        
        for k in [1, 3, 5, 10]:
            metric = f'ndcg@{k}'
            original_score = summary['original_method']['avg_ndcg'][metric]
            cross_encoder_score = summary['cross_encoder_method']['avg_ndcg'][metric]
            improvement = cross_encoder_score - original_score
            
            print(f"{metric:<12} {original_score:<12.4f} {cross_encoder_score:<15.4f} {improvement:+.4f}")
        
        print(f"\n⏱️ 性能对比:")
        original_time = summary['original_method']['avg_time']
        cross_encoder_time = summary['cross_encoder_method']['avg_time']
        time_ratio = cross_encoder_time / original_time if original_time > 0 else 0
        
        print(f"   - 原有方法平均时间: {original_time:.4f}秒")
        print(f"   - Cross-Encoder平均时间: {cross_encoder_time:.4f}秒")
        print(f"   - 时间比率: {time_ratio:.2f}x")
        
        # 保存详细结果
        output_file = "reranking_comparison_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细结果已保存到: {output_file}")

def main():
    """主函数"""
    print("🔄 重排方法性能对比测试")
    print("🎯 对比原有多策略重排 vs Cross-Encoder重排")
    print("=" * 60)
    
    try:
        # 初始化对比器
        comparator = RerankingMethodComparator()
        
        # 加载测试问题
        test_questions = comparator.load_qa_questions(max_questions=1000)
        
        if not test_questions:
            print("❌ 没有可用的测试问题")
            return
        
        # 运行对比测试
        comparison_results = comparator.run_comparison(test_questions)
        
        # 打印结果
        comparator.print_comparison_results(comparison_results)
        
        print("\n✅ 重排方法对比测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()