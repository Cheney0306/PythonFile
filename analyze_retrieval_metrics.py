#!/usr/bin/env python3
# analyze_retrieval_metrics.py - 分析检索指标来诊断RAG问题

import json
from pathlib import Path
from collections import defaultdict
import numpy as np

class RetrievalMetricsAnalyzer:
    """检索指标分析器"""
    
    def __init__(self):
        pass
    
    def load_evaluation_results(self, results_file: str):
        """加载评估结果"""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ 加载评估结果失败: {e}")
            return None
    
    def analyze_retrieval_performance(self, results_data):
        """分析检索性能指标"""
        print("🎯 检索性能指标分析")
        print("=" * 50)
        
        # 提取检索指标
        retrieval_metrics = []
        answer_correctness = []
        
        for result in results_data.get('results', []):
            if 'rag_retrieval_metrics' in result:
                metrics = result['rag_retrieval_metrics']
                retrieval_metrics.append(metrics)
                
                # 同时记录答案正确性
                rag_correct = result['rag_scores']['composite_score'] > 0.5
                answer_correctness.append(rag_correct)
        
        if not retrieval_metrics:
            print("❌ 未找到检索指标数据")
            return
        
        print(f"📊 分析 {len(retrieval_metrics)} 个问题的检索指标")
        
        # 计算平均指标
        avg_metrics = self._calculate_average_metrics(retrieval_metrics)
        
        # 分析指标含义
        self._interpret_metrics(avg_metrics)
        
        # 分析检索与答案质量的关系
        self._analyze_retrieval_answer_correlation(retrieval_metrics, answer_correctness)
        
        # 生成诊断报告
        self._generate_diagnostic_report(avg_metrics, answer_correctness)
        
        return avg_metrics
    
    def _calculate_average_metrics(self, retrieval_metrics):
        """计算平均检索指标"""
        metrics_sum = defaultdict(list)
        
        for metrics in retrieval_metrics:
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    metrics_sum[metric_name].append(value)
        
        avg_metrics = {}
        for metric_name, values in metrics_sum.items():
            if values:
                avg_metrics[metric_name] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values)
                }
        
        return avg_metrics
    
    def _interpret_metrics(self, avg_metrics):
        """解释检索指标的含义"""
        print(f"\n📈 检索指标详细分析:")
        print("-" * 40)
        
        # Precision@k 分析
        precision_metrics = {k: v for k, v in avg_metrics.items() if 'precision@' in k}
        if precision_metrics:
            print(f"\n🎯 Precision@k (检索精度):")
            for metric, stats in precision_metrics.items():
                k = metric.split('@')[1]
                mean_val = stats['mean']
                print(f"   {metric}: {mean_val:.4f} (±{stats['std']:.4f})")
                
                # 解释含义
                if mean_val < 0.3:
                    print(f"     ❌ 很低 - 前{k}个结果中相关文档很少")
                elif mean_val < 0.5:
                    print(f"     ⚠️ 偏低 - 前{k}个结果中相关文档不足一半")
                elif mean_val < 0.7:
                    print(f"     ✅ 中等 - 前{k}个结果中有适量相关文档")
                else:
                    print(f"     🏆 很好 - 前{k}个结果中大部分都相关")
        
        # Recall@k 分析
        recall_metrics = {k: v for k, v in avg_metrics.items() if 'recall@' in k}
        if recall_metrics:
            print(f"\n🔍 Recall@k (检索召回率):")
            for metric, stats in recall_metrics.items():
                k = metric.split('@')[1]
                mean_val = stats['mean']
                print(f"   {metric}: {mean_val:.4f} (±{stats['std']:.4f})")
                
                # 解释含义
                if mean_val < 0.3:
                    print(f"     ❌ 很低 - 遗漏了大量相关文档")
                elif mean_val < 0.5:
                    print(f"     ⚠️ 偏低 - 遗漏了较多相关文档")
                elif mean_val < 0.7:
                    print(f"     ✅ 中等 - 找到了大部分相关文档")
                else:
                    print(f"     🏆 很好 - 找到了几乎所有相关文档")
        
        # nDCG@k 分析
        ndcg_metrics = {k: v for k, v in avg_metrics.items() if 'ndcg@' in k}
        if ndcg_metrics:
            print(f"\n📊 nDCG@k (排序质量):")
            for metric, stats in ndcg_metrics.items():
                k = metric.split('@')[1]
                mean_val = stats['mean']
                print(f"   {metric}: {mean_val:.4f} (±{stats['std']:.4f})")
                
                # 解释含义
                if mean_val < 0.3:
                    print(f"     ❌ 很差 - 相关文档排序很靠后")
                elif mean_val < 0.5:
                    print(f"     ⚠️ 偏差 - 相关文档排序不够靠前")
                elif mean_val < 0.7:
                    print(f"     ✅ 中等 - 相关文档排序较为合理")
                else:
                    print(f"     🏆 很好 - 相关文档排序很靠前")
    
    def _analyze_retrieval_answer_correlation(self, retrieval_metrics, answer_correctness):
        """分析检索质量与答案正确性的关系"""
        print(f"\n🔗 检索质量与答案正确性关联分析:")
        print("-" * 40)
        
        # 按答案正确性分组分析检索指标
        correct_metrics = []
        incorrect_metrics = []
        
        for i, is_correct in enumerate(answer_correctness):
            if i < len(retrieval_metrics):
                if is_correct:
                    correct_metrics.append(retrieval_metrics[i])
                else:
                    incorrect_metrics.append(retrieval_metrics[i])
        
        print(f"   正确答案数: {len(correct_metrics)}")
        print(f"   错误答案数: {len(incorrect_metrics)}")
        
        # 对比关键指标
        key_metrics = ['precision@1', 'recall@1', 'ndcg@1', 'precision@5', 'recall@5', 'ndcg@5']
        
        for metric in key_metrics:
            if correct_metrics and incorrect_metrics:
                correct_values = [m.get(metric, 0) for m in correct_metrics if metric in m]
                incorrect_values = [m.get(metric, 0) for m in incorrect_metrics if metric in m]
                
                if correct_values and incorrect_values:
                    correct_avg = np.mean(correct_values)
                    incorrect_avg = np.mean(incorrect_values)
                    diff = correct_avg - incorrect_avg
                    
                    print(f"\n   {metric}:")
                    print(f"     正确答案时: {correct_avg:.4f}")
                    print(f"     错误答案时: {incorrect_avg:.4f}")
                    print(f"     差异: {diff:+.4f}")
                    
                    if abs(diff) > 0.1:
                        if diff > 0:
                            print(f"     💡 检索质量与答案正确性正相关")
                        else:
                            print(f"     ⚠️ 检索质量与答案正确性负相关(异常)")
                    else:
                        print(f"     ❓ 检索质量与答案正确性关联较弱")
    
    def _generate_diagnostic_report(self, avg_metrics, answer_correctness):
        """生成诊断报告"""
        print(f"\n🔧 问题诊断与改进建议:")
        print("=" * 40)
        
        issues = []
        suggestions = []
        
        # 分析 Precision@1
        precision_1 = avg_metrics.get('precision@1', {}).get('mean', 0)
        if precision_1 < 0.3:
            issues.append("Precision@1过低 - 最相关的检索结果质量差")
            suggestions.extend([
                "🔧 优化嵌入模型或查询预处理",
                "🔧 调整相似度计算方法",
                "🔧 改进数据质量和标注"
            ])
        
        # 分析 Recall@5
        recall_5 = avg_metrics.get('recall@5', {}).get('mean', 0)
        if recall_5 < 0.5:
            issues.append("Recall@5过低 - 检索范围不够广")
            suggestions.extend([
                "📈 增加检索数量 (n_results)",
                "📈 降低相似度阈值",
                "📈 使用多种检索策略"
            ])
        
        # 分析 nDCG@k
        ndcg_1 = avg_metrics.get('ndcg@1', {}).get('mean', 0)
        ndcg_5 = avg_metrics.get('ndcg@5', {}).get('mean', 0)
        
        if ndcg_1 < 0.4:
            issues.append("nDCG@1过低 - 排序算法有问题")
            suggestions.extend([
                "🎯 改进重排序算法",
                "🎯 优化相似度权重",
                "🎯 使用学习排序方法"
            ])
        
        if ndcg_5 > ndcg_1 * 1.5:
            issues.append("nDCG差异大 - 相关文档排序靠后")
            suggestions.extend([
                "⬆️ 优化第一阶段检索",
                "⬆️ 改进查询扩展策略"
            ])
        
        # 分析答案正确率
        correct_rate = sum(answer_correctness) / len(answer_correctness) if answer_correctness else 0
        if correct_rate < 0.5:
            issues.append(f"答案正确率过低 ({correct_rate:.2%})")
            suggestions.extend([
                "💬 优化答案提取逻辑",
                "💬 改进CoTKR prompt",
                "💬 调整LLM参数"
            ])
        
        # 输出诊断结果
        if issues:
            print(f"\n❌ 发现的问题:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        if suggestions:
            print(f"\n💡 改进建议:")
            unique_suggestions = list(set(suggestions))
            for i, suggestion in enumerate(unique_suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        # 生成优先级建议
        self._generate_priority_suggestions(avg_metrics, correct_rate)
    
    def _generate_priority_suggestions(self, avg_metrics, correct_rate):
        """生成优先级改进建议"""
        print(f"\n🎯 优先级改进建议:")
        print("-" * 30)
        
        precision_1 = avg_metrics.get('precision@1', {}).get('mean', 0)
        recall_5 = avg_metrics.get('recall@5', {}).get('mean', 0)
        ndcg_1 = avg_metrics.get('ndcg@1', {}).get('mean', 0)
        
        priority_actions = []
        
        # 高优先级
        if precision_1 < 0.2:
            priority_actions.append(("高", "立即检查数据质量和嵌入模型"))
        
        if recall_5 < 0.3:
            priority_actions.append(("高", "增加检索数量到10-15个"))
        
        if correct_rate < 0.3:
            priority_actions.append(("高", "检查答案提取逻辑"))
        
        # 中优先级
        if ndcg_1 < 0.4:
            priority_actions.append(("中", "优化重排序算法"))
        
        if precision_1 < 0.5:
            priority_actions.append(("中", "改进查询预处理"))
        
        # 低优先级
        if recall_5 < 0.7:
            priority_actions.append(("低", "考虑查询扩展"))
        
        # 输出优先级建议
        for priority, action in priority_actions:
            print(f"   【{priority}】 {action}")

def analyze_specific_evaluation_file(file_path: str):
    """分析指定的评估结果文件"""
    print(f"🔍 分析评估结果文件: {file_path}")
    print("=" * 60)
    
    analyzer = RetrievalMetricsAnalyzer()
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 加载评估结果
    results_data = analyzer.load_evaluation_results(file_path)
    if not results_data:
        return
    
    # 分析检索性能
    avg_metrics = analyzer.analyze_retrieval_performance(results_data)
    
    print(f"\n✅ 分析完成！")
    print(f"\n📋 关键发现:")
    print(f"   - 通过检索指标可以精确定位问题")
    print(f"   - Precision@k 反映检索精度")
    print(f"   - Recall@k 反映检索覆盖度") 
    print(f"   - nDCG@k 反映排序质量")
    print(f"   - 这些指标的组合可以指导具体的改进方向")

def main():
    """主函数"""
    # 查找最新的评估结果文件
    evaluation_dir = Path("evaluation")
    
    if not evaluation_dir.exists():
        print("❌ evaluation 目录不存在")
        return
    
    # 查找完整的评估结果文件
    result_files = list(evaluation_dir.glob("rag_vs_llm_full_results_*.json"))
    
    if not result_files:
        print("❌ 未找到评估结果文件")
        print("💡 请先运行: python rag_vs_llm_evaluation.py --mode quick")
        return
    
    # 使用最新的文件
    latest_file = max(result_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📁 找到评估结果文件: {latest_file.name}")
    
    # 分析文件
    analyze_specific_evaluation_file(str(latest_file))

if __name__ == '__main__':
    main()