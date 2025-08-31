# generate_enhanced_qa.py - 使用增强系统生成QA数据集

import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from enhanced_qa_generator import EnhancedQAGenerator

def main():
    """主函数 - 使用增强系统生成QA数据集"""
    parser = argparse.ArgumentParser(description="使用增强系统生成QA数据集")
    parser.add_argument('--max-texts', type=int, default=None, 
                       help='最大处理的文本数量 (默认: 处理全部)')
    parser.add_argument('--test-mode', action='store_true',
                       help='测试模式，只处理少量文本')
    parser.add_argument('--output-file', type=str, default=None,
                       help='输出文件名 (默认: 自动生成)')
    parser.add_argument('--show-samples', action='store_true',
                       help='显示生成的QA对示例')
    parser.add_argument('--question-types', type=str, nargs='+', 
                       choices=['sub', 'obj', 'rel', 'type'], default=None,
                       help='指定要生成的问题类型 (默认: 全部类型)')
    parser.add_argument('--exclude-type', action='store_true',
                       help='排除类型问题 (推荐，因为类型问题效果较差)')
    parser.add_argument('--only-basic', action='store_true',
                       help='只生成基础问题类型 (sub, obj, rel)，排除type')
    
    args = parser.parse_args()
    
    print("🚀 增强系统QA数据集生成器")
    print("🎯 流程: train文本 → 增强RAG系统 → prompt模板 → LLM → QA对")
    print("=" * 70)
    print(f"📊 配置信息:")
    print(f"   - 数据源: train数据集")
    print(f"   - 检索系统: 增强RAG系统 (多阶段检索)")
    print(f"   - 处理数量: {'测试模式(少量)' if args.test_mode else ('全部文本' if args.max_texts is None else f'{args.max_texts} 个文本')}")
    
    try:
        # 确定要生成的问题类型
        enabled_types = None
        if args.exclude_type:
            enabled_types = ['sub', 'obj', 'rel']
            print("🎯 排除类型问题模式")
        elif args.only_basic:
            enabled_types = ['sub', 'obj', 'rel'] 
            print("🎯 只生成基础问题类型")
        elif args.question_types:
            enabled_types = args.question_types
            print(f"🎯 自定义问题类型: {', '.join(enabled_types)}")
        else:
            print("🎯 生成所有问题类型")
        
        # 使用增强QA生成器
        print(f"\n🔧 初始化增强QA生成器...")
        generator = EnhancedQAGenerator(enabled_question_types=enabled_types)
        
        # 验证使用的是增强系统
        engine_type = type(generator.retrieval_engine).__name__
        print(f"   - 检索引擎: {engine_type}")
        print(f"   - 生成策略: 跳过重写，直接用三元组+One-shot提示")
        
        # 检查增强系统状态
        print(f"\n🔧 检查增强RAG系统状态...")
        system_status = generator.retrieval_engine.get_system_status()
        print(f"   - 数据库状态: {system_status['database_status']['status']}")
        print(f"   - 文档数量: {system_status['database_status']['total_documents']}")
        
        if system_status['database_status']['total_documents'] == 0:
            print("⚠ 警告: 增强向量数据库为空，需要先初始化增强数据库")
            print("💡 建议运行: python initialize_enhanced_database.py")
            
            user_input = input("是否继续？(y/n): ")
            if user_input.lower() != 'y':
                print("❌ 用户取消操作")
                return
        
        # 设置输出文件名
        if args.output_file:
            output_file = args.output_file
        else:
            # 构建文件名，包含问题类型信息
            type_suffix = ""
            if args.exclude_type or args.only_basic:
                type_suffix = "_no_type"
            elif args.question_types:
                type_suffix = f"_{'_'.join(args.question_types)}"
            
            if args.test_mode:
                output_file = f"enhanced_qa_dataset_test{type_suffix}.json"
            else:
                text_count = args.max_texts if args.max_texts else 'all'
                output_file = f"enhanced_qa_dataset_{text_count}_texts{type_suffix}.json"
        
        # 生成QA数据集
        print(f"\n🔄 开始使用增强系统生成QA数据集...")
        
        # 根据模式设置处理数量
        if args.test_mode:
            max_texts = 5  # 测试模式只处理5个文本
            print(f"🧪 测试模式: 只处理 {max_texts} 个文本")
        else:
            max_texts = args.max_texts  # None表示处理全部
            if max_texts is None:
                print(f"📊 全量模式: 处理全部文本")
            else:
                print(f"📊 限量模式: 处理 {max_texts} 个文本")
        
        # 生成QA数据集（增量写入模式）
        qa_dataset = generator.generate_qa_dataset_from_texts(
            max_texts=max_texts, 
            output_filename=output_file
        )
        
        if not qa_dataset:
            print("❌ QA数据集生成失败")
            return
        
        # 质量检查
        print(f"\n🔍 质量检查...")
        valid_qa_count = 0
        invalid_qa_count = 0
        
        for qa in qa_dataset:
            if (qa.get('question', '').strip() and 
                qa.get('answer', '').strip() and 
                len(qa.get('question', '')) > 10 and 
                len(qa.get('answer', '')) > 20):
                valid_qa_count += 1
            else:
                invalid_qa_count += 1
        
        print(f"   - 有效QA对: {valid_qa_count}")
        print(f"   - 无效QA对: {invalid_qa_count}")
        print(f"   - 质量率: {valid_qa_count/(valid_qa_count+invalid_qa_count)*100:.1f}%")
        
        # 显示示例
        if args.show_samples and qa_dataset:
            print(f"\n📋 QA对示例 (前3个):")
            for i, qa in enumerate(qa_dataset[:3], 1):
                print(f"\n{i}. 问题: {qa.get('question', 'N/A')}")
                print(f"   答案: {qa.get('answer', 'N/A')}")
                print(f"   类型: {qa.get('question_type', 'N/A')}")
                print(f"   方法: {qa.get('generation_method', 'N/A')}")
        
        # 保存位置信息
        output_path = Path("qa_datasets") / output_file
        print(f"\n✅ 增强系统QA数据集生成完成！")
        print(f"📁 保存位置: {output_path}")
        print(f"📊 总计: {len(qa_dataset)} 个QA对")
        print(f"🎯 使用系统: {engine_type}")
        
        # 使用建议
        print(f"\n💡 使用建议:")
        print(f"   - 评估对比: python retrieval_evaluation_system.py --mode quick")
        print(f"   - 查看结果: python evaluation_viewer.py --action list")
        print(f"   - 排除类型问题: python generate_enhanced_qa.py --exclude-type")
        print(f"   - 只生成特定类型: python generate_enhanced_qa.py --question-types sub obj")
        
    except Exception as e:
        print(f"❌ 生成过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()