# quick_demo.py - 新系统快速演示

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

def demo_basic_functionality():
    """演示基本功能"""
    print("🚀 新KG-RAG系统快速演示")
    print("=" * 50)
    
    try:
        from main_system import NewKGRAGSystem
        
        # 初始化系统
        print("🔧 初始化系统...")
        system = NewKGRAGSystem()
        
        # 设置数据库
        print("📚 设置数据库...")
        system.setup_database(reset=False)
        
        # 演示问题
        demo_questions = [
            "Who is the leader of Belgium?",
            "Where is Amsterdam Airport located?",
            "What is the runway length of the airport?",
        ]
        
        print(f"\n🔍 演示查询功能 - 测试 {len(demo_questions)} 个问题:")
        print("-" * 50)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{i}. 问题: {question}")
            
            try:
                result = system.retrieval_engine.retrieve_and_rewrite(question)
                
                print(f"   🎯 问题类型: {result['retrieval_stats']['question_type']}")
                print(f"   📊 检索数量: {result['retrieval_stats']['num_retrieved']}")
                print(f"   📏 平均距离: {result['retrieval_stats']['avg_distance']:.4f}")
                
                print(f"\n   🧠 CoTKR重写知识:")
                # 只显示前两行，避免输出过长
                knowledge_lines = result['cotkr_knowledge'].split('\n')[:2]
                for line in knowledge_lines:
                    if line.strip():
                        print(f"      {line}")
                if len(result['cotkr_knowledge'].split('\n')) > 2:
                    print("      ...")
                
                print(f"\n   💡 最终答案: {result['final_answer']}")
                
            except Exception as e:
                print(f"   ❌ 查询失败: {e}")
        
        print("\n" + "=" * 50)
        print("✅ 基本功能演示完成！")
        
        # 显示系统信息
        info = system.get_system_info()
        print(f"\n📊 系统状态:")
        print(f"   - 系统名称: {info['system_name']}")
        print(f"   - 数据库文档数: {info['database_status']['total_documents']}")
        print(f"   - 嵌入模型: {info['components']['embedding_model']}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        print("\n💡 可能的解决方案:")
        print("   1. 检查config.py中的API密钥和数据路径设置")
        print("   2. 确保数据文件存在")
        print("   3. 运行 python main_system.py --mode setup 初始化数据库")

def demo_cotkr_rewriter():
    """演示CoTKR重写器功能"""
    print("\n🧠 CoTKR重写器功能演示")
    print("=" * 50)
    
    try:
        from cotkr_rewriter import CoTKRRewriter
        
        rewriter = CoTKRRewriter()
        
        # 模拟检索结果
        mock_retrieval_results = [
            {
                'triple': ('Belgium', 'leader', 'Philippe_of_Belgium'),
                'schema': ('Country', 'leader', 'Royalty'),
                'distance': 0.31
            },
            {
                'triple': ('Belgium', 'leader', 'Charles_Michel'),
                'schema': ('Country', 'leader', 'PrimeMinister'),
                'distance': 0.33
            }
        ]
        
        test_questions = [
            ("Who is the leader of Belgium?", "who"),
            ("Where is Amsterdam Airport located?", "where"),
            ("What is the runway length?", "what"),
            ("How many countries are there?", "how_many")
        ]
        
        for question, expected_type in test_questions:
            print(f"\n🔍 问题: {question}")
            
            # 检测问题类型
            detected_type = rewriter.detect_question_type(question)
            print(f"   🎯 检测类型: {detected_type} (预期: {expected_type})")
            
            # 重写知识
            rewritten_knowledge = rewriter.rewrite_knowledge(mock_retrieval_results, question)
            print(f"   🧠 重写知识:")
            for line in rewritten_knowledge.split('\n')[:2]:
                if line.strip():
                    print(f"      {line}")
            
            # 提取答案
            answer = rewriter.extract_answer_from_knowledge(question, rewritten_knowledge, mock_retrieval_results)
            print(f"   💡 提取答案: {answer}")
        
        print("\n✅ CoTKR重写器演示完成！")
        
    except Exception as e:
        print(f"❌ CoTKR演示失败: {e}")

def demo_system_components():
    """演示系统各组件"""
    print("\n🔧 系统组件演示")
    print("=" * 50)
    
    # 1. 数据加载器演示
    print("\n1️⃣ 数据加载器演示:")
    try:
        from data_loader import KnowledgeDataLoader
        loader = KnowledgeDataLoader()
        entries = loader.get_knowledge_entries()
        
        if entries:
            print(f"   ✅ 成功加载 {len(entries)} 个知识条目")
            print(f"   📋 示例条目: {entries[0]['triple']}")
        else:
            print("   ⚠ 没有找到知识条目")
    except Exception as e:
        print(f"   ❌ 数据加载器测试失败: {e}")
    
    # 2. 嵌入客户端演示
    print("\n2️⃣ 嵌入客户端演示:")
    try:
        from embedding_client import EmbeddingClient
        client = EmbeddingClient()
        
        test_text = "Belgium leader Philippe of Belgium"
        print(f"   🔤 测试文本: {test_text}")
        
        embedding = client.get_single_embedding(test_text)
        if embedding:
            print(f"   ✅ 成功获取嵌入向量，维度: {len(embedding)}")
            print(f"   📊 向量前5个值: {embedding[:5]}")
        else:
            print("   ❌ 嵌入向量获取失败")
    except Exception as e:
        print(f"   ❌ 嵌入客户端测试失败: {e}")
    
    # 3. 向量数据库演示
    print("\n3️⃣ 向量数据库演示:")
    try:
        from vector_database import VectorDatabaseManager
        db_manager = VectorDatabaseManager()
        db_manager.initialize_collection()
        
        stats = db_manager.get_database_stats()
        print(f"   ✅ 数据库连接成功")
        print(f"   📊 文档数量: {stats['total_documents']}")
        print(f"   🏷 集合名称: {stats['collection_name']}")
        
        if stats['total_documents'] > 0:
            results = db_manager.query_database("Belgium leader", n_results=2)
            print(f"   🔍 测试查询返回 {len(results)} 个结果")
            if results:
                print(f"   📋 最佳匹配: {results[0]['triple']} (距离: {results[0]['distance']:.4f})")
    except Exception as e:
        print(f"   ❌ 向量数据库测试失败: {e}")
    
    print("\n✅ 系统组件演示完成！")

def main():
    """主演示函数"""
    print("🎭 新KG-RAG系统完整演示")
    print("🌟 集成CoTKR知识重写技术")
    print("=" * 60)
    
    # 运行各项演示
    demo_basic_functionality()
    demo_cotkr_rewriter()
    demo_system_components()
    
    print("\n🎉 所有演示完成！")
    print("=" * 60)
    
    print("\n📖 更多使用方式:")
    print("   • 交互式查询: python main_system.py --mode interactive")
    print("   • 批量查询: python main_system.py --mode batch --questions '问题1' '问题2'")
    print("   • 性能评估: python main_system.py --mode evaluate")
    print("   • 完整测试: python test_new_system.py")
    print("   • 生成图表: python visualize_system_flow.py")

if __name__ == '__main__':
    main()