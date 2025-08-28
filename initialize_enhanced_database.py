# initialize_enhanced_database.py - 增强系统数据库初始化

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from enhanced_embedding_system import EnhancedVectorDatabaseManager
from data_loader import KnowledgeDataLoader
import config

def initialize_enhanced_database(reset: bool = False, show_progress: bool = True):
    """
    初始化增强系统的向量数据库
    
    Args:
        reset: 是否重置现有数据库
        show_progress: 是否显示详细进度
    """
    print("🚀 增强RAG系统数据库初始化")
    print("=" * 50)
    
    # 显示配置信息
    print("📋 系统配置:")
    print(f"   - 数据源: {config.DATASET_PATHS}")
    print(f"   - 嵌入模型: {config.EMBEDDING_MODEL}")
    print(f"   - 数据库路径: {config.CHROMA_DB_PATH}")
    print(f"   - 集合名称: {config.ENHANCED_COLLECTION_NAME}")
    print(f"   - 批处理大小: {config.BATCH_SIZE}")
    
    try:
        # 1. 初始化增强数据库管理器
        print(f"\n🔧 初始化增强数据库管理器...")
        enhanced_db = EnhancedVectorDatabaseManager()
        
        # 2. 创建或重置集合
        enhanced_db.initialize_collection(
            collection_name=config.ENHANCED_COLLECTION_NAME,
            reset=reset
        )
        
        # 3. 检查现有数据
        current_count = enhanced_db.collection.count()
        print(f"📊 当前数据库状态: {current_count} 个文档")
        
        if current_count > 0 and not reset:
            user_input = input("数据库已有数据，是否重新填充？(y/n): ")
            if user_input.lower() != 'y':
                print("✅ 保持现有数据，初始化完成")
                return True
            
            # 用户选择重新填充，重置数据库
            enhanced_db.initialize_collection(
                collection_name=config.ENHANCED_COLLECTION_NAME,
                reset=True
            )
        
        # 4. 加载知识数据
        print(f"\n📚 加载知识数据...")
        loader = KnowledgeDataLoader()
        knowledge_entries = loader.get_knowledge_entries()
        
        if not knowledge_entries:
            print("❌ 未找到知识数据，请检查数据路径配置")
            return False
        
        print(f"✅ 成功加载 {len(knowledge_entries)} 个知识条目")
        
        # 5. 显示数据样例
        if show_progress and knowledge_entries:
            print(f"\n📋 数据样例:")
            sample = knowledge_entries[0]
            print(f"   ID: {sample['id']}")
            print(f"   三元组: {sample['triple']}")
            print(f"   Schema: {sample['schema']}")
            
            # 显示增强文本转换
            enhanced_text = enhanced_db.enhanced_triple_to_text(
                sample['triple'], sample['schema']
            )
            print(f"   增强文本: {enhanced_text}")
        
        # 6. 填充数据库
        print(f"\n🔄 开始填充增强数据库...")
        print(f"   使用增强嵌入策略和丰富元数据")
        
        enhanced_db.populate_enhanced_database(knowledge_entries)
        
        # 7. 验证结果
        final_count = enhanced_db.collection.count()
        print(f"\n✅ 数据库初始化完成！")
        print(f"   - 最终文档数: {final_count}")
        print(f"   - 集合名称: {enhanced_db.collection.name}")
        
        # 8. 测试检索功能
        print(f"\n🔍 测试检索功能...")
        test_query = "Belgium leader"
        test_results = enhanced_db.multi_stage_retrieval(test_query, n_results=3)
        
        if test_results:
            print(f"✅ 检索测试成功，找到 {len(test_results)} 个结果")
            
            # 显示第一个结果
            top_result = test_results[0]
            print(f"   Top-1结果: {top_result['triple']}")
            if 'rerank_score' in top_result:
                print(f"   重排分数: {top_result['rerank_score']:.4f}")
        else:
            print("⚠️ 检索测试未找到结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_status():
    """检查数据库状态"""
    print("📊 检查增强数据库状态")
    print("=" * 30)
    
    try:
        enhanced_db = EnhancedVectorDatabaseManager()
        enhanced_db.initialize_collection(collection_name=config.ENHANCED_COLLECTION_NAME)
        
        stats = enhanced_db.get_database_stats()
        
        print(f"集合名称: {stats['collection_name']}")
        print(f"文档总数: {stats['total_documents']}")
        print(f"状态: {stats['status']}")
        print(f"增强功能: {stats.get('enhancement', 'N/A')}")
        
        if stats['total_documents'] > 0:
            # 测试查询
            test_results = enhanced_db.multi_stage_retrieval("test query", n_results=1)
            if test_results:
                print("✅ 数据库可正常查询")
            else:
                print("⚠️ 数据库查询异常")
        else:
            print("⚠️ 数据库为空，需要初始化")
            
        return stats['total_documents'] > 0
        
    except Exception as e:
        print(f"❌ 检查数据库状态失败: {e}")
        return False

def compare_embedding_methods():
    """对比原始和增强的嵌入方法"""
    print("\n🔄 对比嵌入方法")
    print("=" * 30)
    
    try:
        # 示例数据
        example_triple = ("Belgium", "leader", "Philippe_of_Belgium")
        example_schema = ("Country", "leader", "King")
        
        print(f"示例三元组: {example_triple}")
        print(f"示例Schema: {example_schema}")
        
        # 原始方法
        from vector_database import VectorDatabaseManager
        original_db = VectorDatabaseManager()
        original_text = original_db.triple_to_embedding_text(example_triple, example_schema)
        
        # 增强方法
        enhanced_db = EnhancedVectorDatabaseManager()
        enhanced_text = enhanced_db.enhanced_triple_to_text(example_triple, example_schema)
        
        print(f"\n📝 文本对比:")
        print(f"原始方法:")
        print(f"  \"{original_text}\"")
        print(f"增强方法:")
        print(f"  \"{enhanced_text}\"")
        
        # 元数据对比
        entry = {
            "id": "demo_001",
            "triple": example_triple,
            "schema": example_schema,
            "text": "Belgium's leader is King Philippe.",
            "source_file": "demo.xml"
        }
        
        enhanced_metadata = enhanced_db.create_enhanced_metadata(entry)
        
        print(f"\n📊 增强元数据字段:")
        for key in enhanced_metadata.keys():
            if key not in ['source_file', 'text', 'sub', 'rel', 'obj', 'sub_type', 'rel_type', 'obj_type']:
                print(f"  + {key}: {enhanced_metadata[key]}")
        
    except Exception as e:
        print(f"❌ 对比失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强RAG系统数据库初始化")
    parser.add_argument('--reset', action='store_true', help='重置现有数据库')
    parser.add_argument('--check', action='store_true', help='只检查数据库状态')
    parser.add_argument('--compare', action='store_true', help='对比嵌入方法')
    parser.add_argument('--quiet', action='store_true', help='静默模式，减少输出')
    
    args = parser.parse_args()
    
    if args.check:
        # 只检查状态
        status_ok = check_database_status()
        if not status_ok:
            print("\n💡 建议运行: python initialize_enhanced_database.py")
        return
    
    if args.compare:
        # 对比嵌入方法
        compare_embedding_methods()
        return
    
    # 执行初始化
    success = initialize_enhanced_database(
        reset=args.reset, 
        show_progress=not args.quiet
    )
    
    if success:
        print(f"\n🎉 增强系统数据库初始化成功！")
        print(f"\n💡 下一步可以:")
        print(f"   1. 运行测试: python simple_enhanced_test.py")
        print(f"   2. 查看演示: python demo_enhanced_system.py")
        print(f"   3. 进行评估: python retrieval_evaluation_system.py")
        print(f"   4. 检查状态: python initialize_enhanced_database.py --check")
    else:
        print(f"\n❌ 初始化失败，请检查错误信息")

if __name__ == '__main__':
    main()