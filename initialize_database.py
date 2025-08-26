# initialize_database.py - 专门用于初始化向量数据库的脚本

import sys
import argparse
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from data_loader import KnowledgeDataLoader
from vector_database import VectorDatabaseManager
from embedding_client import EmbeddingClient
import config

def main():
    """主函数 - 初始化向量数据库"""
    parser = argparse.ArgumentParser(description="初始化向量数据库")
    parser.add_argument('--reset', action='store_true',
                       help='重置数据库（删除现有数据）')
    parser.add_argument('--max-entries', type=int, default=None,
                       help='限制处理的条目数量（用于测试，默认处理全部）')
    parser.add_argument('--batch-size', type=int, default=None,
                       help='批处理大小（覆盖配置文件设置）')
    parser.add_argument('--test-connection', action='store_true',
                       help='仅测试API连接，不处理数据')
    
    args = parser.parse_args()
    
    print("🚀 向量数据库初始化器")
    print("=" * 60)
    print(f"📊 配置信息:")
    print(f"   - 数据源: {config.DATASET_PATHS}")
    print(f"   - 数据库路径: {config.CHROMA_DB_PATH}")
    print(f"   - 集合名称: {config.COLLECTION_NAME}")
    print(f"   - 嵌入模型: {config.EMBEDDING_MODEL}")
    print(f"   - 批处理大小: {args.batch_size or config.BATCH_SIZE}")
    
    if args.reset:
        print("⚠ 警告: 将重置现有数据库")
    
    try:
        # 1. 测试API连接
        print(f"\n🔧 测试SiliconFlow API连接...")
        client = EmbeddingClient()
        
        test_text = "Belgium leader Philippe of Belgium. Types: Country leader Royalty."
        test_embedding = client.get_single_embedding(test_text)
        
        if test_embedding:
            print(f"✅ API连接成功，嵌入维度: {len(test_embedding)}")
        else:
            print("❌ API连接失败")
            return
        
        if args.test_connection:
            print("✅ API连接测试完成")
            return
        
        # 2. 加载知识数据
        print(f"\n📚 加载知识数据...")
        loader = KnowledgeDataLoader()
        knowledge_entries = loader.get_knowledge_entries()
        
        if not knowledge_entries:
            print("❌ 没有找到知识条目")
            return
        
        print(f"✅ 成功加载 {len(knowledge_entries)} 个知识条目")
        
        # 限制条目数量（仅在指定时）
        if args.max_entries and args.max_entries < len(knowledge_entries):
            knowledge_entries = knowledge_entries[:args.max_entries]
            print(f"📊 限制处理数量为 {args.max_entries} 个条目（测试模式）")
        else:
            print(f"📊 处理全部 {len(knowledge_entries)} 个条目")
        
        # 显示示例条目
        if knowledge_entries:
            sample = knowledge_entries[0]
            print(f"\n📋 示例条目:")
            print(f"   ID: {sample['id']}")
            print(f"   三元组: {sample['triple']}")
            print(f"   Schema: {sample['schema']}")
            if sample.get('text'):
                print(f"   文本: {sample['text'][:100]}...")
        
        # 3. 初始化向量数据库
        print(f"\n🗄 初始化向量数据库...")
        db_manager = VectorDatabaseManager()
        
        # 临时修改批处理大小
        if args.batch_size:
            original_batch_size = config.BATCH_SIZE
            config.BATCH_SIZE = args.batch_size
            print(f"📊 使用自定义批处理大小: {args.batch_size}")
        
        db_manager.initialize_collection(reset=args.reset)
        
        # 检查是否需要填充数据
        current_count = db_manager.collection.count()
        print(f"📊 当前数据库文档数: {current_count}")
        
        if current_count == 0 or args.reset:
            print(f"\n🔄 开始填充向量数据库...")
            start_time = time.time()
            
            db_manager.populate_database(knowledge_entries)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            final_count = db_manager.collection.count()
            print(f"\n✅ 数据库填充完成!")
            print(f"📊 处理统计:")
            print(f"   - 处理条目: {len(knowledge_entries)}")
            print(f"   - 最终文档数: {final_count}")
            print(f"   - 处理时间: {processing_time:.2f} 秒")
            print(f"   - 平均速度: {len(knowledge_entries)/processing_time:.2f} 条目/秒")
            
            # 恢复原始批处理大小
            if args.batch_size:
                config.BATCH_SIZE = original_batch_size
        else:
            print(f"✅ 数据库已包含数据，跳过填充")
        
        # 4. 测试查询功能
        print(f"\n🔍 测试查询功能...")
        test_queries = [
            "Belgium leader",
            "Airport location",
            "Movie director"
        ]
        
        for query in test_queries:
            results = db_manager.query_database(query, n_results=3)
            print(f"\n   查询: '{query}'")
            print(f"   结果数: {len(results)}")
            if results:
                best_result = results[0]
                print(f"   最佳匹配: {best_result['triple']} (距离: {best_result['distance']:.4f})")
        
        # 5. 显示最终状态
        stats = db_manager.get_database_stats()
        print(f"\n📊 数据库最终状态:")
        print(f"   - 集合名称: {stats['collection_name']}")
        print(f"   - 文档总数: {stats['total_documents']}")
        print(f"   - 状态: {stats['status']}")
        
        print(f"\n🎉 向量数据库初始化完成!")
        print(f"💡 现在可以运行以下命令:")
        print(f"   - 交互式查询: python main_system.py --mode interactive")
        print(f"   - 生成QA数据集: python generate_qa_dataset.py")
        print(f"   - 基于文本生成QA: python generate_text_qa.py")
        print(f"   - 系统评估: python main_system.py --mode evaluate")
        
    except Exception as e:
        print(f"❌ 初始化过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()