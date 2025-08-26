# main_system.py - 新系统主入口

import argparse
import json
from pathlib import Path
from typing import List, Dict
import config
from data_loader import KnowledgeDataLoader
from vector_database import VectorDatabaseManager
from retrieval_engine import RetrievalEngine
from qa_generator import QAGenerator
from evaluation_engine import EvaluationEngine

class NewKGRAGSystem:
    """新的知识图谱RAG系统 - 集成CoTKR重写功能"""
    
    def __init__(self):
        self.data_loader = KnowledgeDataLoader()
        self.db_manager = VectorDatabaseManager()
        self.retrieval_engine = RetrievalEngine()
        self.qa_generator = QAGenerator()
        self.evaluator = EvaluationEngine()
        
        print("🚀 新KG-RAG系统初始化完成")
        print(f"   - 嵌入模型: {config.EMBEDDING_MODEL}")
        print(f"   - 数据库路径: {config.CHROMA_DB_PATH}")
        print(f"   - 集合名称: {config.COLLECTION_NAME}")
    
    def setup_database(self, reset: bool = False):
        """设置数据库"""
        print("🔧 设置向量数据库...")
        
        # 初始化集合
        self.db_manager.initialize_collection(reset=reset)
        
        # 如果数据库为空或需要重置，填充数据
        if reset or self.db_manager.collection.count() == 0:
            print("📚 加载知识数据...")
            knowledge_entries = self.data_loader.get_knowledge_entries()
            
            if knowledge_entries:
                print("🔄 填充向量数据库...")
                self.db_manager.populate_database(knowledge_entries)
            else:
                print("❌ 没有找到知识数据")
        
        # 显示数据库状态
        stats = self.db_manager.get_database_stats()
        print(f"✅ 数据库设置完成: {stats['total_documents']} 个文档")
    
    def interactive_query(self):
        """交互式查询模式"""
        print("\n🤖 进入交互式查询模式")
        print("输入问题进行查询，输入 'quit' 退出")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n❓ 请输入问题: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if not question:
                    continue
                
                print("🔍 正在检索和重写知识...")
                result = self.retrieval_engine.retrieve_and_rewrite(question)
                
                print(f"\n📊 检索统计:")
                stats = result['retrieval_stats']
                print(f"   - 问题类型: {stats['question_type']}")
                print(f"   - 检索数量: {stats['num_retrieved']}")
                print(f"   - 平均距离: {stats['avg_distance']:.4f}")
                
                print(f"\n🧠 CoTKR重写知识:")
                print(result['cotkr_knowledge'])
                
                print(f"\n💡 最终答案: {result['final_answer']}")
                
                # 显示检索到的原始三元组
                print(f"\n📋 检索到的三元组:")
                for i, item in enumerate(result['retrieved_items'][:3], 1):
                    print(f"   {i}. {item['triple']} (距离: {item['distance']:.4f})")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def batch_query(self, questions: List[str], output_file: str = None):
        """批量查询"""
        print(f"🔄 批量查询 {len(questions)} 个问题")
        
        results = self.retrieval_engine.batch_retrieve(questions)
        
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {output_path}")
        
        return results
    
    def generate_and_evaluate(self, max_qa_pairs: int = 50):
        """生成QA数据集并评估系统性能"""
        print(f"🔄 生成和评估流程开始")
        
        # 1. 生成QA数据集
        print("📝 生成QA数据集...")
        qa_dataset = self.qa_generator.generate_qa_dataset(max_entries=max_qa_pairs)
        
        if not qa_dataset:
            print("❌ QA数据集生成失败")
            return
        
        # 保存QA数据集
        qa_file = self.qa_generator.save_qa_dataset(qa_dataset, "new_system_qa_dataset.json")
        
        # 2. 评估系统性能
        print("📊 评估系统性能...")
        evaluation_results = self.evaluator.evaluate_qa_dataset(qa_dataset)
        
        # 保存评估结果
        eval_file = self.evaluator.save_evaluation_results(
            evaluation_results, "new_system_evaluation.json"
        )
        
        # 打印摘要
        self.evaluator.print_evaluation_summary(evaluation_results)
        
        return {
            'qa_dataset_file': qa_file,
            'evaluation_file': eval_file,
            'results': evaluation_results
        }
    
    def get_system_info(self):
        """获取系统信息"""
        return self.retrieval_engine.get_system_status()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新KG-RAG系统")
    parser.add_argument('--mode', choices=['setup', 'interactive', 'batch', 'evaluate', 'info'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--reset-db', action='store_true', help='重置数据库')
    parser.add_argument('--questions', nargs='+', help='批量查询的问题列表')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--max-qa', type=int, default=50, help='生成的QA对数量')
    
    args = parser.parse_args()
    
    # 初始化系统
    system = NewKGRAGSystem()
    
    if args.mode == 'setup':
        # 设置数据库
        system.setup_database(reset=args.reset_db)
        
    elif args.mode == 'interactive':
        # 确保数据库已设置
        system.setup_database(reset=args.reset_db)
        # 交互式查询
        system.interactive_query()
        
    elif args.mode == 'batch':
        # 批量查询
        if not args.questions:
            print("❌ 批量模式需要提供问题列表")
            return
        
        system.setup_database(reset=args.reset_db)
        results = system.batch_query(args.questions, args.output)
        
        # 打印结果摘要
        print(f"\n📊 批量查询完成:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['question']}")
            print(f"     答案: {result['final_answer']}")
        
    elif args.mode == 'evaluate':
        # 生成和评估
        system.setup_database(reset=args.reset_db)
        system.generate_and_evaluate(max_qa_pairs=args.max_qa)
        
    elif args.mode == 'info':
        # 显示系统信息
        info = system.get_system_info()
        print("\n🔍 系统信息:")
        print(json.dumps(info, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()