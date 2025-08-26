# test_new_system.py - 新系统完整测试

import sys
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from main_system import NewKGRAGSystem
import config

def test_system_components():
    """测试系统各个组件"""
    print("🧪 开始测试新KG-RAG系统组件")
    print("=" * 60)
    
    # 1. 测试数据加载器
    print("\n1️⃣ 测试数据加载器")
    try:
        from data_loader import KnowledgeDataLoader
        loader = KnowledgeDataLoader()
        entries = loader.get_knowledge_entries()
        print(f"   ✅ 成功加载 {len(entries)} 个知识条目")
        
        if entries:
            print(f"   📋 示例条目: {entries[0]['triple']}")
    except Exception as e:
        print(f"   ❌ 数据加载器测试失败: {e}")
    
    # 2. 测试嵌入客户端
    print("\n2️⃣ 测试嵌入客户端")
    try:
        from embedding_client import EmbeddingClient
        client = EmbeddingClient()
        test_text = "Belgium leader Philippe of Belgium"
        embedding = client.get_single_embedding(test_text)
        
        if embedding:
            print(f"   ✅ 成功获取嵌入向量，维度: {len(embedding)}")
        else:
            print("   ❌ 嵌入向量获取失败")
    except Exception as e:
        print(f"   ❌ 嵌入客户端测试失败: {e}")
    
    # 3. 测试向量数据库
    print("\n3️⃣ 测试向量数据库")
    try:
        from vector_database import VectorDatabaseManager
        db_manager = VectorDatabaseManager()
        db_manager.initialize_collection()
        
        stats = db_manager.get_database_stats()
        print(f"   ✅ 数据库连接成功，文档数: {stats['total_documents']}")
        
        # 测试查询
        if stats['total_documents'] > 0:
            results = db_manager.query_database("Belgium leader", n_results=3)
            print(f"   🔍 测试查询返回 {len(results)} 个结果")
    except Exception as e:
        print(f"   ❌ 向量数据库测试失败: {e}")
    
    # 4. 测试CoTKR重写器
    print("\n4️⃣ 测试CoTKR重写器")
    try:
        from cotkr_rewriter import CoTKRRewriter
        rewriter = CoTKRRewriter()
        
        # 模拟检索结果
        mock_items = [
            {
                'triple': ('Belgium', 'leader', 'Philippe_of_Belgium'),
                'schema': ('Country', 'leader', 'Royalty'),
                'distance': 0.31
            }
        ]
        
        question = "Who is the leader of Belgium?"
        question_type = rewriter.detect_question_type(question)
        rewritten = rewriter.rewrite_knowledge(mock_items, question)
        answer = rewriter.extract_answer_from_knowledge(question, rewritten, mock_items)
        
        print(f"   ✅ 问题类型检测: {question_type}")
        print(f"   ✅ 知识重写成功")
        print(f"   ✅ 答案提取: {answer}")
    except Exception as e:
        print(f"   ❌ CoTKR重写器测试失败: {e}")
    
    # 5. 测试检索引擎
    print("\n5️⃣ 测试检索引擎")
    try:
        from retrieval_engine import RetrievalEngine
        engine = RetrievalEngine()
        
        test_question = "Who is the leader of Belgium?"
        result = engine.retrieve_and_rewrite(test_question)
        
        print(f"   ✅ 检索引擎测试成功")
        print(f"   📊 检索统计: {result['retrieval_stats']}")
        print(f"   💡 最终答案: {result['final_answer']}")
    except Exception as e:
        print(f"   ❌ 检索引擎测试失败: {e}")

def test_end_to_end():
    """端到端测试"""
    print("\n🔄 端到端系统测试")
    print("=" * 60)
    
    try:
        # 初始化系统
        system = NewKGRAGSystem()
        
        # 设置数据库（如果需要）
        system.setup_database(reset=False)
        
        # 测试问题列表
        test_questions = [
            "Who is the leader of Belgium?",
            "Where is Amsterdam Airport located?",
            "What is the runway length of the airport?",
            "How many countries are mentioned?"
        ]
        
        print(f"\n🔍 测试 {len(test_questions)} 个问题:")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. 问题: {question}")
            
            start_time = time.time()
            result = system.retrieval_engine.retrieve_and_rewrite(question)
            end_time = time.time()
            
            print(f"   ⏱ 响应时间: {end_time - start_time:.2f}秒")
            print(f"   🎯 问题类型: {result['retrieval_stats']['question_type']}")
            print(f"   📊 检索数量: {result['retrieval_stats']['num_retrieved']}")
            print(f"   💡 答案: {result['final_answer']}")
        
        print("\n✅ 端到端测试完成")
        
    except Exception as e:
        print(f"❌ 端到端测试失败: {e}")

def test_qa_generation():
    """测试QA生成功能"""
    print("\n📝 测试QA生成功能")
    print("=" * 60)
    
    try:
        from qa_generator import QAGenerator
        generator = QAGenerator()
        
        # 生成小规模测试数据集
        qa_dataset = generator.generate_qa_dataset(max_entries=5)
        
        if qa_dataset:
            print(f"✅ 成功生成 {len(qa_dataset)} 个QA对")
            
            # 显示示例
            for i, qa in enumerate(qa_dataset[:3], 1):
                print(f"\n{i}. 问题: {qa['question']}")
                print(f"   答案: {qa['answer']}")
                print(f"   类型: {qa['question_type']}")
        else:
            print("❌ QA生成失败")
            
    except Exception as e:
        print(f"❌ QA生成测试失败: {e}")

def test_evaluation():
    """测试评估功能"""
    print("\n📊 测试评估功能")
    print("=" * 60)
    
    try:
        from evaluation_engine import EvaluationEngine
        evaluator = EvaluationEngine()
        
        # 生成小规模测试数据
        qa_dataset = evaluator.qa_generator.generate_qa_dataset(max_entries=3)
        
        if qa_dataset:
            # 评估系统
            results = evaluator.evaluate_qa_dataset(qa_dataset, k_values=[1, 3])
            
            print("✅ 评估完成")
            print(f"📊 平均指标:")
            for metric, value in results['average_metrics'].items():
                print(f"   {metric}: {value:.4f}")
        else:
            print("❌ 评估测试失败：无法生成QA数据")
            
    except Exception as e:
        print(f"❌ 评估测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 新KG-RAG系统完整测试")
    print("=" * 60)
    print(f"📋 配置信息:")
    print(f"   - 嵌入模型: {config.EMBEDDING_MODEL}")
    print(f"   - 数据库路径: {config.CHROMA_DB_PATH}")
    print(f"   - 数据集路径: {config.DATASET_PATHS}")
    
    # 运行各项测试
    test_system_components()
    test_end_to_end()
    test_qa_generation()
    test_evaluation()
    
    print("\n🎉 所有测试完成！")
    print("=" * 60)
    
    # 系统信息
    try:
        system = NewKGRAGSystem()
        info = system.get_system_info()
        print("\n🔍 系统状态:")
        print(f"   - 系统名称: {info['system_name']}")
        print(f"   - 数据库状态: {info['database_status']['status']}")
        print(f"   - 文档总数: {info['database_status']['total_documents']}")
    except Exception as e:
        print(f"❌ 获取系统信息失败: {e}")

if __name__ == '__main__':
    main()