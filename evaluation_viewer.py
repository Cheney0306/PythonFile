# evaluation_viewer.py - 评估结果查看器

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
import argparse

def list_evaluation_results(evaluation_dir: str = "evaluation"):
    """列出所有评估结果文件"""
    eval_path = Path(evaluation_dir)
    
    if not eval_path.exists():
        print(f"❌ 评估目录不存在: {evaluation_dir}")
        return []
    
    # 查找所有评估结果文件
    summary_files = list(eval_path.glob("evaluation_summary_*.json"))
    
    if not summary_files:
        print(f"📂 评估目录 {evaluation_dir} 中没有找到评估结果")
        return []
    
    print(f"📊 找到 {len(summary_files)} 个评估结果:")
    print("=" * 60)
    
    results_info = []
    
    for i, file_path in enumerate(sorted(summary_files, reverse=True), 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', 'unknown')
            total_questions = data.get('total_questions', 0)
            embedding_model = data.get('evaluation_config', {}).get('embedding_model', 'unknown')
            
            print(f"{i}. 时间戳: {timestamp}")
            print(f"   文件: {file_path.name}")
            print(f"   问题数: {total_questions}")
            print(f"   模型: {embedding_model}")
            print()
            
            results_info.append({
                'index': i,
                'timestamp': timestamp,
                'file_path': file_path,
                'total_questions': total_questions,
                'embedding_model': embedding_model
            })
            
        except Exception as e:
            print(f"⚠️ 读取文件 {file_path} 失败: {e}")
    
    return results_info

def view_evaluation_summary(file_path: Path):
    """查看评估结果摘要"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 评估结果摘要")
        print("=" * 50)
        print(f"时间戳: {data.get('timestamp', 'unknown')}")
        print(f"问题总数: {data.get('total_questions', 0)}")
        print(f"嵌入模型: {data.get('evaluation_config', {}).get('embedding_model', 'unknown')}")
        
        summary_metrics = data.get('summary_metrics', {})
        
        if 'original_system' in summary_metrics and 'enhanced_system' in summary_metrics:
            print(f"\n🔄 系统对比:")
            print("-" * 30)
            
            # 创建对比表格
            k_values = [1, 3, 5, 10]
            metrics = ['precision', 'recall', 'ndcg']
            
            for k in k_values:
                print(f"\nK={k} 指标对比:")
                print(f"{'指标':<12} {'原始系统':<12} {'增强系统':<12} {'改进幅度':<12}")
                print("-" * 50)
                
                for metric in metrics:
                    metric_key = f'{metric}@{k}'
                    
                    orig_data = summary_metrics['original_system'].get(metric_key, {})
                    enh_data = summary_metrics['enhanced_system'].get(metric_key, {})
                    
                    if orig_data and enh_data:
                        orig_val = orig_data['mean']
                        enh_val = enh_data['mean']
                        
                        if orig_val > 0:
                            improvement = ((enh_val - orig_val) / orig_val) * 100
                            improvement_str = f"{improvement:+.2f}%"
                        else:
                            improvement_str = "N/A"
                        
                        print(f"{metric.upper():<12} {orig_val:<12.4f} {enh_val:<12.4f} {improvement_str:<12}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取评估结果失败: {e}")
        return False

def compare_multiple_evaluations(evaluation_dir: str = "evaluation"):
    """对比多个评估结果"""
    eval_path = Path(evaluation_dir)
    summary_files = list(eval_path.glob("evaluation_summary_*.json"))
    
    if len(summary_files) < 2:
        print("❌ 需要至少2个评估结果才能进行对比")
        return
    
    print(f"📈 对比 {len(summary_files)} 个评估结果")
    print("=" * 60)
    
    # 收集所有结果数据
    all_results = []
    
    for file_path in sorted(summary_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', 'unknown')
            summary_metrics = data.get('summary_metrics', {})
            
            if 'enhanced_system' in summary_metrics:
                # 提取增强系统的关键指标
                enh_metrics = summary_metrics['enhanced_system']
                
                result_row = {'timestamp': timestamp}
                
                for k in [1, 3, 5]:
                    for metric in ['precision', 'recall', 'ndcg']:
                        metric_key = f'{metric}@{k}'
                        if metric_key in enh_metrics:
                            result_row[metric_key] = enh_metrics[metric_key]['mean']
                
                all_results.append(result_row)
                
        except Exception as e:
            print(f"⚠️ 处理文件 {file_path} 失败: {e}")
    
    if all_results:
        # 创建DataFrame并显示
        df = pd.DataFrame(all_results)
        df = df.set_index('timestamp')
        
        print("增强系统性能趋势 (均值):")
        print(df.round(4))
        
        # 计算改进趋势
        if len(df) > 1:
            print(f"\n📈 性能变化趋势:")
            for col in df.columns:
                first_val = df[col].iloc[0]
                last_val = df[col].iloc[-1]
                if first_val > 0:
                    change = ((last_val - first_val) / first_val) * 100
                    print(f"{col}: {change:+.2f}%")

def export_to_excel(evaluation_dir: str = "evaluation", output_file: str = "evaluation_comparison.xlsx"):
    """导出评估结果到Excel"""
    eval_path = Path(evaluation_dir)
    summary_files = list(eval_path.glob("evaluation_summary_*.json"))
    
    if not summary_files:
        print("❌ 没有找到评估结果文件")
        return
    
    print(f"📊 导出 {len(summary_files)} 个评估结果到Excel...")
    
    # 收集数据
    original_data = []
    enhanced_data = []
    
    for file_path in sorted(summary_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', 'unknown')
            summary_metrics = data.get('summary_metrics', {})
            
            # 原始系统数据
            if 'original_system' in summary_metrics:
                row = {'timestamp': timestamp, 'system': 'original'}
                for metric_name, metric_data in summary_metrics['original_system'].items():
                    row[metric_name] = metric_data['mean']
                original_data.append(row)
            
            # 增强系统数据
            if 'enhanced_system' in summary_metrics:
                row = {'timestamp': timestamp, 'system': 'enhanced'}
                for metric_name, metric_data in summary_metrics['enhanced_system'].items():
                    row[metric_name] = metric_data['mean']
                enhanced_data.append(row)
                
        except Exception as e:
            print(f"⚠️ 处理文件 {file_path} 失败: {e}")
    
    # 创建Excel文件
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        if original_data:
            df_orig = pd.DataFrame(original_data)
            df_orig.to_excel(writer, sheet_name='原始系统', index=False)
        
        if enhanced_data:
            df_enh = pd.DataFrame(enhanced_data)
            df_enh.to_excel(writer, sheet_name='增强系统', index=False)
        
        # 如果两个系统都有数据，创建对比表
        if original_data and enhanced_data:
            # 创建对比数据
            comparison_data = []
            
            for orig_row, enh_row in zip(original_data, enhanced_data):
                if orig_row['timestamp'] == enh_row['timestamp']:
                    comp_row = {'timestamp': orig_row['timestamp']}
                    
                    for metric in ['precision@1', 'precision@3', 'precision@5', 
                                  'recall@1', 'recall@3', 'recall@5',
                                  'ndcg@1', 'ndcg@3', 'ndcg@5']:
                        if metric in orig_row and metric in enh_row:
                            orig_val = orig_row[metric]
                            enh_val = enh_row[metric]
                            
                            comp_row[f'{metric}_original'] = orig_val
                            comp_row[f'{metric}_enhanced'] = enh_val
                            
                            if orig_val > 0:
                                improvement = ((enh_val - orig_val) / orig_val) * 100
                                comp_row[f'{metric}_improvement'] = improvement
                    
                    comparison_data.append(comp_row)
            
            if comparison_data:
                df_comp = pd.DataFrame(comparison_data)
                df_comp.to_excel(writer, sheet_name='系统对比', index=False)
    
    print(f"✅ 评估结果已导出到: {output_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="评估结果查看器")
    parser.add_argument('--action', choices=['list', 'view', 'compare', 'export'], 
                       default='list', help='操作类型')
    parser.add_argument('--dir', type=str, default='evaluation', 
                       help='评估结果目录')
    parser.add_argument('--index', type=int, help='查看指定索引的评估结果')
    parser.add_argument('--output', type=str, default='evaluation_comparison.xlsx',
                       help='Excel导出文件名')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        results_info = list_evaluation_results(args.dir)
        
        if results_info:
            print("💡 使用方法:")
            print(f"   查看详情: python evaluation_viewer.py --action view --index <序号>")
            print(f"   对比结果: python evaluation_viewer.py --action compare")
            print(f"   导出Excel: python evaluation_viewer.py --action export")
    
    elif args.action == 'view':
        if args.index is None:
            print("❌ 请指定要查看的评估结果索引: --index <序号>")
            return
        
        results_info = list_evaluation_results(args.dir)
        
        if args.index <= 0 or args.index > len(results_info):
            print(f"❌ 索引超出范围，请选择 1-{len(results_info)}")
            return
        
        selected_result = results_info[args.index - 1]
        view_evaluation_summary(selected_result['file_path'])
    
    elif args.action == 'compare':
        compare_multiple_evaluations(args.dir)
    
    elif args.action == 'export':
        export_to_excel(args.dir, args.output)

if __name__ == '__main__':
    main()