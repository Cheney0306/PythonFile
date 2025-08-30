#!/usr/bin/env python3
# diagnose_rag_issues.py - 诊断RAG系统问题

import json
from pathlib import Path
from collections import defaultdict, Counter
from enhanced_retrieval_engine import EnhancedRetrievalEngine
from enhanced_embedding_system import EnhancedVectorDatabaseManager

class RAGDiagnostics:
    """RAG系统诊断工具"""
    
    def __init__(self):
        self.engine = EnhancedRetrievalEngine()
        self.db_manager = EnhancedVectorDatabaseManager()
        self.db_manager.initialize_collection()
    
    def analyze_validation_results(self, validation_file: str):
        """分析验证结果，找出问题模式"""
        print("🔍 分析RAG系统问题")
        print("=" * 50)
        
        # 加载验证结果
        with open(validation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        detailed_results = data.get('detailed_results', [])
        
        print(f"📊 基本统计:")
        print(f"   总问题数: {data['total_questions']}")
        print(f"   RAG正确率: {data['rag_accuracy']:.2%}")
        print(f"   LLM正确率: {data['llm_accuracy']:.2%}")
        
        # 分析错误类型
        self._analyze_error_patterns(detailed_results)
        
        # 分析问题类型表现
        self._analyze_question_type_performance(detailed_results)
        
        # 分析答案长度影响
        self._analyze_answer_length_impact(detailed_results)
        
        # 检查检索质量
        self._check_retrieval_quality(detailed_results)
        
        return detailed_results
    
    def _analyze_error_patterns(self, results):
        """分析错误模式"""
        print(f"\n🔍 错误模式分析:")
        print("-" * 30)
        
        error_types = {
            'empty_answer': 0,      # 空答案
            'wrong_entity': 0,      # 错误实体
            'partial_correct': 0,   # 部分正确
            'completely_wrong': 0   # 完全错误
        }
        
        rag_errors = [r for r in results if not r['rag_correct']]
        
        for result in rag_errors:
            expected = result['expected'].lower().strip()
            rag_answer = result['rag_answer'].lower().strip()
            
            if not rag_answer or rag_answer in ['no answer', 'unknown', 'error']:
                error_types['empty_answer'] += 1
            elif any(word in rag_answer for word in expected.split()) or any(word in expected for word in rag_answer.split()):
                error_types['partial_correct'] += 1
            else:
                error_types['completely_wrong'] += 1
        
        total_errors = len(rag_errors)
        if total_errors > 0:
            for error_type, count in error_types.items():
                percentage = count / total_errors * 100
                print(f"   {error_type}: {count} ({percentage:.1f}%)")
        
        # 显示典型错误案例
        print(f"\n❌ 典型错误案例:")
        for i, result in enumerate(rag_errors[:5], 1):
            print(f"\n   案例 {i}:")
            print(f"     问题: {result['question']}")
            print(f"     期望: {result['expected']}")
            print(f"     RAG: {result['rag_answer']}")
    
    def _analyze_question_type_performance(self, results):
        """分析不同问题类型的表现"""
        print(f"\n📋 问题类型表现分析:")
        print("-" * 30)
        
        # 从问题中推断类型
        type_performance = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        for result in results:
            question = result['question'].lower()
            
            # 简单的问题类型分类
            if question.startswith(('who', 'which person')):
                q_type = 'person'
            elif question.startswith(('what', 'which')):
                q_type = 'entity'
            elif question.startswith(('where', 'in which')):
                q_type = 'location'
            elif question.startswith(('when')):
                q_type = 'time'
            elif question.startswith(('how')):
                q_type = 'method'
            else:
                q_type = 'other'
            
            type_performance[q_type]['total'] += 1
            if result['rag_correct']:
                type_performance[q_type]['correct'] += 1
        
        for q_type, stats in type_performance.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                print(f"   {q_type}: {stats['correct']}/{stats['total']} ({accuracy:.2%})")
    
    def _analyze_answer_length_impact(self, results):
        """分析答案长度对正确率的影响"""
        print(f"\n📏 答案长度影响分析:")
        print("-" * 30)
        
        length_buckets = {
            'short': {'range': (0, 20), 'total': 0, 'correct': 0},
            'medium': {'range': (21, 50), 'total': 0, 'correct': 0},
            'long': {'range': (51, 999), 'total': 0, 'correct': 0}
        }
        
        for result in results:
            expected_len = len(result['expected'])
            
            for bucket_name, bucket in length_buckets.items():
                if bucket['range'][0] <= expected_len <= bucket['range'][1]:
                    bucket['total'] += 1
                    if result['rag_correct']:
                        bucket['correct'] += 1
                    break
        
        for bucket_name, bucket in length_buckets.items():
            if bucket['total'] > 0:
                accuracy = bucket['correct'] / bucket['total']
                print(f"   {bucket_name} ({bucket['range'][0]}-{bucket['range'][1]} chars): {bucket['correct']}/{bucket['total']} ({accuracy:.2%})")
    
    def _check_retrieval_quality(self, results):
        """检查检索质量"""
        print(f"\n🎯 检索质量检查:")
        print("-" * 30)
        
        # 随机选择几个错误案例进行深度检索分析
        rag_errors = [r for r in results if not r['rag_correct']][:5]
        
        for i, result in enumerate(rag_errors, 1):
            print(f"\n   案例 {i}: {result['question']}")
            
            try:
                # 执行检索
                rag_result = self.engine.retrieve_and_rewrite(result['question'])
                retrieved_items = rag_result.get('retrieved_items', [])
                
                print(f"     检索到 {len(retrieved_items)} 个项目")
                
                if retrieved_items:
                    # 显示最相关的检索结果
                    top_item = retrieved_items[0]
                    print(f"     最佳匹配: {top_item.get('triple', 'N/A')}")
                    print(f"     距离: {top_item.get('distance', 'N/A'):.4f}")
                    print(f"     文档: {top_item.get('document', 'N/A')[:100]}...")
                    
                    # 检查是否检索到相关信息
                    expected_words = set(result['expected'].lower().split())
                    retrieved_text = ' '.join([item.get('document', '') for item in retrieved_items[:3]]).lower()
                    
                    overlap = len(expected_words.intersection(set(retrieved_text.split())))
                    print(f"     词汇重叠: {overlap}/{len(expected_words)} 个词")
                else:
                    print(f"     ❌ 未检索到任何相关项目")
                    
            except Exception as e:
                print(f"     ❌ 检索失败: {e}")
    
    def check_database_coverage(self):
        """检查数据库覆盖度"""
        print(f"\n📊 数据库覆盖度检查:")
        print("-" * 30)
        
        try:
            # 获取数据库统计
            stats = self.db_manager.get_database_stats()
            print(f"   总文档数: {stats['total_documents']}")
            print(f"   集合状态: {stats['status']}")
            
            # 检查关系类型分布
            all_data = self.db_manager.collection.get()
            if all_data and all_data['metadatas']:
                relations = Counter()
                entities = Counter()
                
                for metadata in all_data['metadatas']:
                    rel = metadata.get('rel', 'unknown')
                    sub = metadata.get('sub', 'unknown')
                    obj = metadata.get('obj', 'unknown')
                    
                    relations[rel] += 1
                    entities[sub] += 1
                    entities[obj] += 1
                
                print(f"\n   关系类型分布 (Top 10):")
                for rel, count in relations.most_common(10):
                    print(f"     {rel}: {count}")
                
                print(f"\n   实体频率 (Top 10):")
                for entity, count in entities.most_common(10):
                    print(f"     {entity}: {count}")
            
        except Exception as e:
            print(f"   ❌ 数据库检查失败: {e}")
    
    def generate_improvement_suggestions(self, results):
        """生成改进建议"""
        print(f"\n💡 改进建议:")
        print("=" * 30)
        
        rag_accuracy = sum(1 for r in results if r['rag_correct']) / len(results)
        
        suggestions = []
        
        if rag_accuracy < 0.5:
            suggestions.extend([
                "1. 🔍 检查数据质量: 确保向量数据库包含足够的相关信息",
                "2. 🎯 优化检索策略: 调整检索参数，增加检索数量",
                "3. 📝 改进答案提取: 优化CoTKR重写逻辑",
                "4. 🔧 调整嵌入模型: 考虑使用更适合的嵌入模型"
            ])
        
        # 检查空答案比例
        empty_answers = sum(1 for r in results if not r['rag_answer'].strip())
        if empty_answers > len(results) * 0.1:
            suggestions.append("5. ❌ 减少空答案: 检查答案提取逻辑，避免返回空结果")
        
        # 检查检索覆盖度
        suggestions.extend([
            "6. 📊 增加数据覆盖: 补充缺失的知识领域数据",
            "7. 🔄 优化重排序: 改进多阶段检索的重排序算法",
            "8. 🎨 调整prompt: 优化CoTKR的prompt模板"
        ])
        
        for suggestion in suggestions:
            print(f"   {suggestion}")
        
        return suggestions

def main():
    """主函数"""
    # 指定验证结果文件
    validation_file = r"D:\PythonFile\newSystem\evaluation\evaluation_result\validation_results_20250831_010000.json"
    
    # 检查文件是否存在
    if not Path(validation_file).exists():
        print(f"❌ 验证结果文件不存在: {validation_file}")
        print("💡 请先运行 quick_validate.py 生成验证结果")
        return
    
    # 创建诊断器
    diagnostics = RAGDiagnostics()
    
    # 分析验证结果
    results = diagnostics.analyze_validation_results(validation_file)
    
    # 检查数据库覆盖度
    diagnostics.check_database_coverage()
    
    # 生成改进建议
    diagnostics.generate_improvement_suggestions(results)
    
    print(f"\n✅ 诊断完成！")
    print(f"\n🎯 关键改进方向:")
    print(f"   1. 检查并补充数据库内容")
    print(f"   2. 优化检索和答案提取逻辑")
    print(f"   3. 调整系统参数")
    print(f"   4. 改进prompt模板")

if __name__ == '__main__':
    main()