# rag_vs_llm_evaluation.py - RAG系统与纯LLM对比评估

import json
import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from tqdm import tqdm
import math
from collections import defaultdict
from datetime import datetime
import argparse

# 导入我们的系统
from enhanced_retrieval_engine import EnhancedRetrievalEngine
import config

class RAGvsLLMEvaluator:
    """RAG系统与纯LLM对比评估器"""
    
    def __init__(self):
        self.enhanced_engine = EnhancedRetrievalEngine()
        self.openai_api_key = config.OPENAI_API_KEY
        
        # 检查API密钥
        if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
            print("⚠️ 警告: OpenAI API密钥未设置，将无法进行LLM评估")
    
    def load_qa_dataset(self, dataset_path: str = "qa_datasets", limit: int = None, scan_all: bool = False) -> List[Dict]:
        """加载QA数据集"""
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
        
        # 根据参数决定是否限制数量
        if scan_all:
            print(f"🔍 扫描全部模式: 使用全部 {len(all_questions)} 个问题")
            final_questions = all_questions
        else:
            if limit and len(all_questions) > limit:
                final_questions = random.sample(all_questions, limit)
                print(f"🎲 随机采样: 从 {len(all_questions)} 个问题中选择 {len(final_questions)} 个")
            else:
                final_questions = all_questions
                print(f"✅ 使用全部 {len(final_questions)} 个问题")
        
        print(f"✅ 最终评估问题数: {len(final_questions)}")
        return final_questions
    
    def call_pure_llm(self, question: str) -> str:
        """调用纯LLM获取答案"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # 构造严格的prompt，要求LLM只回答问题，不要多说
            prompt = f"""You are a helpful assistant. Answer the following question directly and concisely. 

IMPORTANT INSTRUCTIONS:
- Provide ONLY the direct answer to the question
- Do NOT add explanations, context, or additional information
- Do NOT say "The answer is..." or similar phrases
- Keep your response as brief as possible
- If you don't know the answer, just say "Unknown"

Question: {question}

Answer:"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides direct, concise answers without additional explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # 低温度确保一致性
                max_tokens=50     # 限制输出长度
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            print(f"⚠ LLM调用失败: {e}")
            return "Error: LLM call failed"
    
    def calculate_retrieval_metrics(self, retrieved_items: List[Dict], expected_answer: str, 
                                  original_triple: List[str] = None, k_values: List[int] = [1, 3, 5]) -> Dict:
        """
        计算检索指标: Precision@k, Recall@k, nDCG@k
        
        Args:
            retrieved_items: 检索到的项目列表
            expected_answer: 期望答案
            original_triple: 生成问题所用的原始三元组
            k_values: 要计算的k值列表
        """
        if not retrieved_items:
            return {f'precision@{k}': 0.0 for k in k_values} | \
                   {f'recall@{k}': 0.0 for k in k_values} | \
                   {f'ndcg@{k}': 0.0 for k in k_values}
        
        # 计算每个检索项的相关性分数
        relevance_scores = []
        
        for item in retrieved_items:
            if original_triple and 'triple' in item:
                # 基于三元组的相关性判断
                retrieved_triple = item['triple']
                relevance, is_relevant = self._calculate_triple_relevance(retrieved_triple, original_triple)
            else:
                # 回退到基于词汇重叠的相关性判断
                relevance, is_relevant = self._calculate_text_relevance(item, expected_answer)
            
            relevance_scores.append((relevance, is_relevant))
        
        metrics = {}
        
        for k in k_values:
            k = min(k, len(retrieved_items))  # 确保k不超过检索项数量
            
            # Precision@k
            relevant_at_k = sum(score[1] for score in relevance_scores[:k])
            precision_k = relevant_at_k / k if k > 0 else 0.0
            metrics[f'precision@{k}'] = precision_k
            
            # Recall@k (假设总相关文档数为1，即期望答案)
            total_relevant = 1  # 简化假设
            recall_k = min(relevant_at_k / total_relevant, 1.0) if total_relevant > 0 else 0.0
            metrics[f'recall@{k}'] = recall_k
            
            # nDCG@k
            dcg_k = 0.0
            for i in range(k):
                relevance = relevance_scores[i][0]
                dcg_k += relevance / math.log2(i + 2)  # i+2 because log2(1) = 0
            
            # 理想DCG (假设最佳排序)
            ideal_relevances = sorted([score[0] for score in relevance_scores], reverse=True)[:k]
            idcg_k = 0.0
            for i, relevance in enumerate(ideal_relevances):
                idcg_k += relevance / math.log2(i + 2)
            
            ndcg_k = dcg_k / idcg_k if idcg_k > 0 else 0.0
            metrics[f'ndcg@{k}'] = ndcg_k
        
        return metrics
    
    def _calculate_triple_relevance(self, retrieved_triple: List[str], original_triple: List[str]) -> Tuple[float, int]:
        """
        基于三元组计算相关性分数
        
        Args:
            retrieved_triple: 检索到的三元组
            original_triple: 原始三元组
            
        Returns:
            (relevance_score, is_relevant): 相关性分数和二进制相关性
        """
        if not retrieved_triple or not original_triple:
            return 0.0, 0
        
        # 确保两个三元组都有3个元素
        if len(retrieved_triple) != 3 or len(original_triple) != 3:
            return 0.0, 0
        
        # 计算匹配的元素数量
        matches = 0
        for i in range(3):
            if retrieved_triple[i] == original_triple[i]:
                matches += 1
        
        # 相关性判断逻辑:
        # - 3个元素完全匹配: 最相关 (relevance=1.0, is_relevant=1)
        # - 2个元素匹配: 部分相关 (relevance=0.6, is_relevant=1)  
        # - 1个或0个元素匹配: 不相关 (relevance=0.0, is_relevant=0)
        
        if matches == 3:
            return 1.0, 1  # 完全相关
        elif matches == 2:
            return 0.6, 1  # 部分相关
        else:
            return 0.0, 0  # 不相关
    
    def _calculate_text_relevance(self, item: Dict, expected_answer: str) -> Tuple[float, int]:
        """
        基于文本重叠计算相关性分数 (回退方法)
        
        Args:
            item: 检索项
            expected_answer: 期望答案
            
        Returns:
            (relevance_score, is_relevant): 相关性分数和二进制相关性
        """
        expected_words = set(expected_answer.lower().split())
        
        # 从检索项中提取文本内容
        item_text = ""
        if 'text' in item and item['text']:
            item_text = item['text']
        elif 'document' in item and item['document']:
            item_text = item['document']
        elif 'triple' in item:
            # 从三元组构建文本
            triple = item['triple']
            item_text = f"{triple[0]} {triple[1]} {triple[2]}"
        
        # 计算相关性分数 (基于词汇重叠)
        item_words = set(item_text.lower().split())
        if len(expected_words) > 0:
            overlap = len(item_words.intersection(expected_words))
            relevance = overlap / len(expected_words)
        else:
            relevance = 0.0
        
        # 转换为二进制相关性 (阈值为0.1)
        is_relevant = 1 if relevance > 0.1 else 0
        return relevance, is_relevant

    def evaluate_answer_similarity(self, predicted: str, expected: str) -> Dict[str, float]:
        """评估答案相似度"""
        predicted = predicted.lower().strip()
        expected = expected.lower().strip()
        
        # 1. 精确匹配
        exact_match = 1.0 if predicted == expected else 0.0
        
        # 2. 包含匹配
        contains_match = 1.0 if expected in predicted or predicted in expected else 0.0
        
        # 3. 词汇重叠度
        pred_words = set(predicted.split())
        exp_words = set(expected.split())
        
        if len(exp_words) == 0:
            word_overlap = 0.0
        else:
            word_overlap = len(pred_words.intersection(exp_words)) / len(exp_words)
        
        # 4. 综合分数 (加权平均)
        composite_score = (exact_match * 0.5 + contains_match * 0.3 + word_overlap * 0.2)
        
        return {
            'exact_match': exact_match,
            'contains_match': contains_match,
            'word_overlap': word_overlap,
            'composite_score': composite_score
        }
    
    def evaluate_single_question(self, qa_item: Dict) -> Dict:
        """评估单个问题"""
        question = qa_item['question']
        expected_answer = qa_item['expected_answer']
        
        # 1. 获取RAG系统答案和检索详情
        rag_retrieval_metrics = {}
        try:
            rag_result = self.enhanced_engine.retrieve_and_rewrite(question)
            rag_answer = rag_result.get('final_answer', 'No answer')
            
            # 计算检索指标
            retrieved_items = rag_result.get('retrieved_items', [])
            if retrieved_items:
                # 获取原始三元组信息
                original_triple = qa_item.get('triple', None)
                rag_retrieval_metrics = self.calculate_retrieval_metrics(
                    retrieved_items, expected_answer, original_triple, k_values=[1, 3, 5]
                )
            
        except Exception as e:
            rag_answer = f"Error: {e}"
            rag_retrieval_metrics = {
                'precision@1': 0.0, 'precision@3': 0.0, 'precision@5': 0.0,
                'recall@1': 0.0, 'recall@3': 0.0, 'recall@5': 0.0,
                'ndcg@1': 0.0, 'ndcg@3': 0.0, 'ndcg@5': 0.0
            }
        
        # 2. 获取纯LLM答案
        llm_answer = self.call_pure_llm(question)
        
        # 3. 评估两个答案
        rag_scores = self.evaluate_answer_similarity(rag_answer, expected_answer)
        llm_scores = self.evaluate_answer_similarity(llm_answer, expected_answer)
        
        return {
            'question': question,
            'expected_answer': expected_answer,
            'rag_answer': rag_answer,
            'llm_answer': llm_answer,
            'rag_scores': rag_scores,
            'llm_scores': llm_scores,
            'rag_retrieval_metrics': rag_retrieval_metrics,
            'question_type': qa_item.get('question_type', 'unknown'),
            'source_file': qa_item.get('source_file', 'unknown')
        }
    
    def evaluate_dataset(self, questions: List[Dict]) -> Dict:
        """评估整个数据集"""
        print(f"🔄 开始评估 {len(questions)} 个问题...")
        print("⚠️ 注意: 包含LLM调用，可能需要较长时间")
        
        results = []
        
        for qa_item in tqdm(questions, desc="评估进度"):
            result = self.evaluate_single_question(qa_item)
            results.append(result)
        
        # 计算汇总统计
        summary = self.calculate_summary_statistics(results)
        
        return {
            'results': results,
            'summary': summary,
            'total_questions': len(questions),
            'timestamp': datetime.now().isoformat(),
            'evaluation_config': {
                'embedding_model': config.EMBEDDING_MODEL,
                'llm_model': 'gpt-3.5-turbo'
            }
        }
    
    def calculate_summary_statistics(self, results: List[Dict]) -> Dict:
        """计算汇总统计"""
        rag_metrics = defaultdict(list)
        llm_metrics = defaultdict(list)
        rag_retrieval_metrics = defaultdict(list)
        
        # 按问题类型分组
        by_type = defaultdict(lambda: {
            'rag': defaultdict(list), 
            'llm': defaultdict(list),
            'rag_retrieval': defaultdict(list)
        })
        
        for result in results:
            q_type = result['question_type']
            
            # 收集RAG答案质量指标
            for metric, score in result['rag_scores'].items():
                rag_metrics[metric].append(score)
                by_type[q_type]['rag'][metric].append(score)
            
            # 收集RAG检索指标
            for metric, score in result.get('rag_retrieval_metrics', {}).items():
                rag_retrieval_metrics[metric].append(score)
                by_type[q_type]['rag_retrieval'][metric].append(score)
            
            # 收集LLM指标
            for metric, score in result['llm_scores'].items():
                llm_metrics[metric].append(score)
                by_type[q_type]['llm'][metric].append(score)
        
        # 计算总体统计
        def calc_stats(values):
            if not values:
                return {'mean': 0.0, 'std': 0.0}
            return {
                'mean': np.mean(values),
                'std': np.std(values)
            }
        
        summary = {
            'overall': {
                'rag': {metric: calc_stats(scores) for metric, scores in rag_metrics.items()},
                'llm': {metric: calc_stats(scores) for metric, scores in llm_metrics.items()},
                'rag_retrieval': {metric: calc_stats(scores) for metric, scores in rag_retrieval_metrics.items()}
            },
            'by_question_type': {}
        }
        
        # 按问题类型统计
        for q_type, type_data in by_type.items():
            summary['by_question_type'][q_type] = {
                'rag': {metric: calc_stats(scores) for metric, scores in type_data['rag'].items()},
                'llm': {metric: calc_stats(scores) for metric, scores in type_data['llm'].items()},
                'rag_retrieval': {metric: calc_stats(scores) for metric, scores in type_data['rag_retrieval'].items()}
            }
        
        return summary
    
    def save_evaluation_results(self, results: Dict, output_dir: str = "evaluation"):
        """保存评估结果"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整结果
        full_results_file = output_path / f"rag_vs_llm_full_results_{timestamp}.json"
        with open(full_results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 保存汇总结果
        summary_file = output_path / f"rag_vs_llm_summary_{timestamp}.json"
        summary_data = {
            'timestamp': results['timestamp'],
            'total_questions': results['total_questions'],
            'evaluation_config': results['evaluation_config'],
            'summary': results['summary']
        }
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        # 保存问答对比
        self._save_qa_comparison(results, output_path, timestamp)
        
        # 保存简化的问答记录 (每行一个问题)
        self._save_simple_qa_records(results, output_path, timestamp)
        
        # 生成Markdown报告
        self._generate_markdown_report(results, output_path, timestamp)
        
        print(f"💾 评估结果已保存到目录: {output_dir}")
        print(f"📁 生成的文件:")
        print(f"   - 完整结果: {full_results_file.name}")
        print(f"   - 汇总结果: {summary_file.name}")
        print(f"   - 问答对比: rag_vs_llm_qa_comparison_{timestamp}.json")
        print(f"   - 问答对比(易读): rag_vs_llm_qa_comparison_{timestamp}.txt")
        print(f"   - 问答对比(CSV): rag_vs_llm_qa_comparison_{timestamp}.csv")
        print(f"   - 简化问答记录: simple_qa_records_{timestamp}.jsonl")
        print(f"   - Markdown报告: rag_vs_llm_report_{timestamp}.md")
    
    def _save_qa_comparison(self, results: Dict, output_path: Path, timestamp: str):
        """
        保存RAG系统与LLM的问答对比
        
        Args:
            results: 完整的评估结果
            output_path: 输出路径
            timestamp: 时间戳
        """
        # 1. 保存JSON格式（便于程序处理）
        qa_comparison_file = output_path / f"rag_vs_llm_qa_comparison_{timestamp}.json"
        
        qa_comparisons = []
        
        for result in results.get('results', []):
            qa_comparison = {
                'question': result['question'],
                'expected_answer': result['expected_answer'],
                'question_type': result.get('question_type', 'unknown'),
                'rag_system': {
                    'answer': result['rag_answer'],
                    'scores': {
                        'exact_match': result['rag_scores']['exact_match'],
                        'contains_match': result['rag_scores']['contains_match'],
                        'word_overlap': result['rag_scores']['word_overlap'],
                        'composite_score': result['rag_scores']['composite_score']
                    }
                },
                'llm_system': {
                    'answer': result['llm_answer'],
                    'scores': {
                        'exact_match': result['llm_scores']['exact_match'],
                        'contains_match': result['llm_scores']['contains_match'],
                        'word_overlap': result['llm_scores']['word_overlap'],
                        'composite_score': result['llm_scores']['composite_score']
                    }
                },
                'winner': self._determine_winner(result['rag_scores'], result['llm_scores']),
                'score_difference': {
                    'exact_match': result['rag_scores']['exact_match'] - result['llm_scores']['exact_match'],
                    'contains_match': result['rag_scores']['contains_match'] - result['llm_scores']['contains_match'],
                    'word_overlap': result['rag_scores']['word_overlap'] - result['llm_scores']['word_overlap'],
                    'composite_score': result['rag_scores']['composite_score'] - result['llm_scores']['composite_score']
                }
            }
            qa_comparisons.append(qa_comparison)
        
        # 保存JSON格式
        with open(qa_comparison_file, 'w', encoding='utf-8') as f:
            json.dump(qa_comparisons, f, ensure_ascii=False, indent=2)
        
        # 2. 保存易读的文本格式
        txt_comparison_file = output_path / f"rag_vs_llm_qa_comparison_{timestamp}.txt"
        with open(txt_comparison_file, 'w', encoding='utf-8') as f:
            f.write("RAG系统 vs 纯LLM 问答对比报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间: {results.get('timestamp', timestamp)}\n")
            f.write(f"总问题数: {results.get('total_questions', len(qa_comparisons))}\n\n")
            
            # 统计胜负情况
            rag_wins = sum(1 for qa in qa_comparisons if qa['winner'] == 'RAG')
            llm_wins = sum(1 for qa in qa_comparisons if qa['winner'] == 'LLM')
            ties = sum(1 for qa in qa_comparisons if qa['winner'] == 'TIE')
            
            total_questions = len(qa_comparisons)
            
            f.write(f"胜负统计:\n")
            if total_questions > 0:
                f.write(f"  RAG系统获胜: {rag_wins} 次 ({rag_wins/total_questions*100:.1f}%)\n")
                f.write(f"  纯LLM获胜: {llm_wins} 次 ({llm_wins/total_questions*100:.1f}%)\n")
                f.write(f"  平局: {ties} 次 ({ties/total_questions*100:.1f}%)\n\n")
            else:
                f.write(f"  RAG系统获胜: {rag_wins} 次 (0.0%)\n")
                f.write(f"  纯LLM获胜: {llm_wins} 次 (0.0%)\n")
                f.write(f"  平局: {ties} 次 (0.0%)\n\n")
            
            for i, qa in enumerate(qa_comparisons, 1):
                f.write(f"问题 {i}:\n")
                f.write("-" * 40 + "\n")
                f.write(f"问题: {qa['question']}\n")
                f.write(f"期望答案: {qa['expected_answer']}\n")
                f.write(f"问题类型: {qa['question_type']}\n\n")
                
                f.write("RAG系统:\n")
                f.write(f"  答案: {qa['rag_system']['answer']}\n")
                f.write(f"  精确匹配: {qa['rag_system']['scores']['exact_match']:.3f}\n")
                f.write(f"  包含匹配: {qa['rag_system']['scores']['contains_match']:.3f}\n")
                f.write(f"  词汇重叠: {qa['rag_system']['scores']['word_overlap']:.3f}\n")
                f.write(f"  综合分数: {qa['rag_system']['scores']['composite_score']:.3f}\n\n")
                
                f.write("纯LLM:\n")
                f.write(f"  答案: {qa['llm_system']['answer']}\n")
                f.write(f"  精确匹配: {qa['llm_system']['scores']['exact_match']:.3f}\n")
                f.write(f"  包含匹配: {qa['llm_system']['scores']['contains_match']:.3f}\n")
                f.write(f"  词汇重叠: {qa['llm_system']['scores']['word_overlap']:.3f}\n")
                f.write(f"  综合分数: {qa['llm_system']['scores']['composite_score']:.3f}\n\n")
                
                f.write(f"胜负结果: {qa['winner']}\n")
                f.write(f"分数差异 (RAG - LLM):\n")
                f.write(f"  精确匹配: {qa['score_difference']['exact_match']:+.3f}\n")
                f.write(f"  包含匹配: {qa['score_difference']['contains_match']:+.3f}\n")
                f.write(f"  词汇重叠: {qa['score_difference']['word_overlap']:+.3f}\n")
                f.write(f"  综合分数: {qa['score_difference']['composite_score']:+.3f}\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
        
        # 3. 保存CSV格式（便于Excel查看）
        csv_comparison_file = output_path / f"rag_vs_llm_qa_comparison_{timestamp}.csv"
        import csv
        
        with open(csv_comparison_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                '问题', '期望答案', '问题类型',
                'RAG答案', 'LLM答案', '胜负结果',
                'RAG精确匹配', 'LLM精确匹配', '精确匹配差异',
                'RAG包含匹配', 'LLM包含匹配', '包含匹配差异',
                'RAG词汇重叠', 'LLM词汇重叠', '词汇重叠差异',
                'RAG综合分数', 'LLM综合分数', '综合分数差异'
            ])
            
            # 写入数据行
            for qa in qa_comparisons:
                writer.writerow([
                    qa['question'],
                    qa['expected_answer'],
                    qa['question_type'],
                    qa['rag_system']['answer'],
                    qa['llm_system']['answer'],
                    qa['winner'],
                    f"{qa['rag_system']['scores']['exact_match']:.3f}",
                    f"{qa['llm_system']['scores']['exact_match']:.3f}",
                    f"{qa['score_difference']['exact_match']:+.3f}",
                    f"{qa['rag_system']['scores']['contains_match']:.3f}",
                    f"{qa['llm_system']['scores']['contains_match']:.3f}",
                    f"{qa['score_difference']['contains_match']:+.3f}",
                    f"{qa['rag_system']['scores']['word_overlap']:.3f}",
                    f"{qa['llm_system']['scores']['word_overlap']:.3f}",
                    f"{qa['score_difference']['word_overlap']:+.3f}",
                    f"{qa['rag_system']['scores']['composite_score']:.3f}",
                    f"{qa['llm_system']['scores']['composite_score']:.3f}",
                    f"{qa['score_difference']['composite_score']:+.3f}"
                ])
    
    def _determine_winner(self, rag_scores: Dict, llm_scores: Dict) -> str:
        """根据综合分数判断胜负"""
        rag_composite = rag_scores['composite_score']
        llm_composite = llm_scores['composite_score']
        
        if rag_composite > llm_composite:
            return 'RAG'
        elif llm_composite > rag_composite:
            return 'LLM'
        else:
            return 'TIE'

    def _save_simple_qa_records(self, results: Dict, output_path: Path, timestamp: str):
        """
        保存简化的问答记录，每行一个JSON对象
        格式: {"question": "...", "expected_answer": "...", "rag_answer": "...", "llm_answer": "..."}
        """
        simple_records_file = output_path / f"simple_qa_records_{timestamp}.jsonl"
        
        with open(simple_records_file, 'w', encoding='utf-8') as f:
            for result in results.get('results', []):
                record = {
                    "question": result['question'],
                    "expected_answer": result['expected_answer'],
                    "rag_answer": result['rag_answer'],
                    "llm_answer": result['llm_answer']
                }
                # 写入一行JSON
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

    def _generate_markdown_report(self, results: Dict, output_path: Path, timestamp: str):
        """生成Markdown报告"""
        report_file = output_path / f"rag_vs_llm_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# RAG系统 vs 纯LLM 评估报告\n\n")
            f.write(f"**生成时间**: {results['timestamp']}\n")
            f.write(f"**评估问题数**: {results['total_questions']}\n")
            f.write(f"**RAG模型**: {results['evaluation_config']['embedding_model']}\n")
            f.write(f"**LLM模型**: {results['evaluation_config']['llm_model']}\n\n")
            
            # 总体性能对比
            f.write("## 📊 总体性能对比\n\n")
            
            overall = results['summary']['overall']
            
            f.write("### 答案质量对比\n\n")
            f.write("| 指标 | RAG系统 | 纯LLM | RAG优势 |\n")
            f.write("|------|---------|-------|--------|\n")
            
            for metric in ['exact_match', 'contains_match', 'word_overlap', 'composite_score']:
                rag_score = overall['rag'][metric]['mean']
                llm_score = overall['llm'][metric]['mean']
                improvement = ((rag_score - llm_score) / llm_score * 100) if llm_score > 0 else 0
                
                f.write(f"| {metric} | {rag_score:.4f} | {llm_score:.4f} | {improvement:+.1f}% |\n")
            
            # RAG检索性能指标
            if 'rag_retrieval' in overall and overall['rag_retrieval']:
                f.write("\n### RAG检索性能指标\n\n")
                f.write("| 指标 | 平均值 | 标准差 |\n")
                f.write("|------|--------|--------|\n")
                
                retrieval_metrics = ['precision@1', 'precision@3', 'precision@5', 
                                   'recall@1', 'recall@3', 'recall@5',
                                   'ndcg@1', 'ndcg@3', 'ndcg@5']
                
                for metric in retrieval_metrics:
                    if metric in overall['rag_retrieval']:
                        mean_score = overall['rag_retrieval'][metric]['mean']
                        std_score = overall['rag_retrieval'][metric]['std']
                        f.write(f"| {metric} | {mean_score:.4f} | {std_score:.4f} |\n")
            
            # 按问题类型分析
            f.write("\n## 📋 按问题类型分析\n\n")
            
            for q_type, type_data in results['summary']['by_question_type'].items():
                f.write(f"### {q_type.upper()} 类型问题\n\n")
                
                f.write("| 指标 | RAG系统 | 纯LLM | RAG优势 |\n")
                f.write("|------|---------|-------|--------|\n")
                
                for metric in ['exact_match', 'contains_match', 'word_overlap', 'composite_score']:
                    rag_score = type_data['rag'][metric]['mean']
                    llm_score = type_data['llm'][metric]['mean']
                    improvement = ((rag_score - llm_score) / llm_score * 100) if llm_score > 0 else 0
                    
                    f.write(f"| {metric} | {rag_score:.4f} | {llm_score:.4f} | {improvement:+.1f}% |\n")
                
                f.write("\n")
            
            # 示例对比
            f.write("## 📝 答案示例对比\n\n")
            
            # 选择几个有代表性的例子
            sample_results = results['results'][:5]
            
            for i, result in enumerate(sample_results, 1):
                f.write(f"### 示例 {i}\n\n")
                f.write(f"**问题**: {result['question']}\n\n")
                f.write(f"**标准答案**: {result['expected_answer']}\n\n")
                f.write(f"**RAG答案**: {result['rag_answer']}\n\n")
                f.write(f"**LLM答案**: {result['llm_answer']}\n\n")
                f.write(f"**RAG综合分数**: {result['rag_scores']['composite_score']:.4f}\n\n")
                f.write(f"**LLM综合分数**: {result['llm_scores']['composite_score']:.4f}\n\n")
                f.write("---\n\n")
    
    def print_summary_report(self, results: Dict):
        """打印汇总报告"""
        print(f"\n📊 RAG vs LLM 评估报告 (共 {results['total_questions']} 个问题)")
        print("=" * 80)
        
        overall = results['summary']['overall']
        
        print(f"\n🔍 总体性能对比:")
        print("-" * 40)
        
        metrics_names = {
            'exact_match': '精确匹配',
            'contains_match': '包含匹配', 
            'word_overlap': '词汇重叠',
            'composite_score': '综合分数'
        }
        
        for metric, name in metrics_names.items():
            rag_score = overall['rag'][metric]['mean']
            rag_std = overall['rag'][metric]['std']
            llm_score = overall['llm'][metric]['mean']
            llm_std = overall['llm'][metric]['std']
            
            improvement = ((rag_score - llm_score) / llm_score * 100) if llm_score > 0 else 0
            
            print(f"\n  {name}:")
            print(f"    RAG系统: {rag_score:.4f} (±{rag_std:.4f})")
            print(f"    纯LLM:   {llm_score:.4f} (±{llm_std:.4f})")
            print(f"    RAG优势: {improvement:+.1f}%")
        
        # 显示RAG检索指标
        if 'rag_retrieval' in overall and overall['rag_retrieval']:
            print(f"\n🎯 RAG检索性能指标:")
            print("-" * 40)
            
            retrieval_metrics_names = {
                'precision@1': 'Precision@1',
                'precision@3': 'Precision@3',
                'precision@5': 'Precision@5',
                'recall@1': 'Recall@1',
                'recall@3': 'Recall@3',
                'recall@5': 'Recall@5',
                'ndcg@1': 'nDCG@1',
                'ndcg@3': 'nDCG@3',
                'ndcg@5': 'nDCG@5'
            }
            
            for metric, name in retrieval_metrics_names.items():
                if metric in overall['rag_retrieval']:
                    score = overall['rag_retrieval'][metric]['mean']
                    std = overall['rag_retrieval'][metric]['std']
                    print(f"  {name}: {score:.4f} (±{std:.4f})")
        
        # 按问题类型显示最佳表现
        print(f"\n📋 按问题类型表现 (综合分数):")
        print("-" * 40)
        
        for q_type, type_data in results['summary']['by_question_type'].items():
            rag_score = type_data['rag']['composite_score']['mean']
            llm_score = type_data['llm']['composite_score']['mean']
            improvement = ((rag_score - llm_score) / llm_score * 100) if llm_score > 0 else 0
            
            print(f"  {q_type.upper()}: RAG {rag_score:.4f} vs LLM {llm_score:.4f} ({improvement:+.1f}%)")


def run_quick_rag_vs_llm_evaluation(sample_size: int = 20):
    """运行快速RAG vs LLM评估"""
    print("⚡ 启动快速RAG vs LLM评估")
    print(f"📊 样本数量: {sample_size}")
    print("=" * 50)
    
    evaluator = RAGvsLLMEvaluator()
    
    # 加载少量数据进行快速测试
    questions = evaluator.load_qa_dataset(limit=sample_size)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    # 运行评估
    results = evaluator.evaluate_dataset(questions)
    
    # 保存结果
    evaluator.save_evaluation_results(results)
    
    # 打印简化报告
    evaluator.print_summary_report(results)
    
    print(f"\n✅ 快速RAG vs LLM评估完成！")


def run_full_rag_vs_llm_evaluation(dataset_path: str = "qa_datasets"):
    """运行完整RAG vs LLM评估"""
    print("🔍 启动完整RAG vs LLM评估")
    print(f"📁 数据集路径: {dataset_path}")
    print("=" * 50)
    
    evaluator = RAGvsLLMEvaluator()
    
    # 加载全部数据
    questions = evaluator.load_qa_dataset(dataset_path=dataset_path, scan_all=True)
    
    if not questions:
        print("❌ 无法加载评估数据")
        return
    
    print(f"\n🚀 开始评估 {len(questions)} 个问题...")
    print("⚠️ 注意: 完整评估包含大量LLM调用，可能需要很长时间和较高费用")
    
    user_input = input("是否继续？(y/n): ")
    if user_input.lower() != 'y':
        print("❌ 用户取消评估")
        return
    
    # 运行评估
    results = evaluator.evaluate_dataset(questions)
    
    # 保存结果
    evaluator.save_evaluation_results(results)
    
    # 打印详细报告
    evaluator.print_summary_report(results)
    
    print(f"\n✅ 完整RAG vs LLM评估完成！")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="RAG系统与纯LLM对比评估")
    parser.add_argument('--mode', choices=['quick', 'full'], default='quick',
                       help='评估模式: quick(快速评估), full(完整评估)')
    parser.add_argument('--sample-size', type=int, default=20,
                       help='快速评估的样本数量')
    parser.add_argument('--qa-path', type=str, default="qa_datasets",
                       help='QA数据集路径')
    
    args = parser.parse_args()
    
    if args.mode == 'quick':
        run_quick_rag_vs_llm_evaluation(args.sample_size)
    elif args.mode == 'full':
        run_full_rag_vs_llm_evaluation(args.qa_path)