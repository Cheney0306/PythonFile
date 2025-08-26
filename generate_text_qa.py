# generate_text_qa.py - 基于文本生成QA数据集的主脚本

import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from text_based_qa_generator import TextBasedQAGenerator

def show_usage_examples():
    """显示使用示例"""
    print("\n🔧 使用示例:")
    print("=" * 50)
    print("1. 测试模式（处理5个文本）:")
    print("   python generate_text_qa.py --test-mode")
    print()
    print("2. 处理全部文本（默认）:")
    print("   python generate_text_qa.py")
    print()
    print("3. 限制处理数量:")
    print("   python generate_text_qa.py --max-texts 100")
    print()
    print("4. 显示生成示例:")
    print("   python generate_text_qa.py --show-samples --test-mode")
    print()
    print("5. 指定输出文件:")
    print("   python generate_text_qa.py --output-file my_qa_dataset.json")
    print()
    print("6. 跳过已存在的文件:")
    print("   python generate_text_qa.py --skip-existing")
    print()
    print("7. 指定数据目录:")
    print("   python generate_text_qa.py --target-dir /path/to/train")
    print("=" * 50)

def main():
    """主函数 - 基于XML文本生成QA数据集"""
    parser = argparse.ArgumentParser(description="基于XML文本生成QA数据集")
    parser.add_argument('--max-texts', type=int, default=None, 
                       help='最大处理的文本数量 (默认: 处理全部)')
    parser.add_argument('--test-mode', action='store_true',
                       help='测试模式，只处理少量文本')
    parser.add_argument('--output-file', type=str, default=None,
                       help='输出文件名 (默认: 自动生成)')
    parser.add_argument('--show-samples', action='store_true',
                       help='显示生成的QA对示例')
    parser.add_argument('--target-dir', type=str, default=None,
                       help='指定train数据集目录路径')
    parser.add_argument('--skip-existing', action='store_true',
                       help='跳过已存在的输出文件')
    parser.add_argument('--help-examples', action='store_true',
                       help='显示详细的使用示例')
    
    args = parser.parse_args()
    
    # 如果请求显示示例，显示后退出
    if args.help_examples:
        show_usage_examples()
        return
    
    print("🚀 基于train数据集的QA数据集生成器")
    print("🎯 流程: train文本 → RAG系统 → prompt模板 → LLM → QA对")
    print("=" * 70)
    print(f"📊 配置信息:")
    print(f"   - 数据源: train数据集 (统一数据源)")
    print(f"   - 处理数量: {'测试模式(少量)' if args.test_mode else ('全部文本' if args.max_texts is None else f'{args.max_texts} 个文本')}")
    print(f"   - 向量数据库: 基于train数据集构建")
    print(f"   - 流程: 文本 → RAG检索 → prompt构建 → LLM生成")
    
    try:
        # 检查输出文件是否已存在
        if args.output_file:
            output_file = args.output_file
        else:
            if args.test_mode:
                output_file = "train_text_qa_dataset_test.json"
            else:
                text_count = args.max_texts if args.max_texts else 'all'
                output_file = f"train_text_qa_dataset_{text_count}_texts.json"
        
        output_path = Path("qa_datasets") / output_file
        if args.skip_existing and output_path.exists():
            print(f"⏭ 输出文件已存在，跳过生成: {output_path}")
            return
        
        # 初始化生成器
        print(f"\n🔧 初始化QA生成器...")
        generator = TextBasedQAGenerator()
        
        # 如果指定了目标目录，更新配置
        if args.target_dir:
            generator.train_dataset_path = args.target_dir
            print(f"📁 使用指定目录: {args.target_dir}")
        
        # 检查RAG系统状态
        print(f"\n🔧 检查RAG系统状态...")
        system_status = generator.retrieval_engine.get_system_status()
        print(f"   - 数据库状态: {system_status['database_status']['status']}")
        print(f"   - 文档数量: {system_status['database_status']['total_documents']}")
        
        if system_status['database_status']['total_documents'] == 0:
            print("⚠ 警告: 向量数据库为空，需要先初始化数据库")
            print("💡 建议运行: python main_system.py --mode setup")
            
            user_input = input("是否继续？(y/n): ")
            if user_input.lower() != 'y':
                print("❌ 用户取消操作")
                return
        
        # 生成QA数据集（统一使用train数据集）
        print(f"\n🔄 开始生成基于train数据集文本的QA数据集...")
        
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
        print(f"   - 质量率: {valid_qa_count / len(qa_dataset) * 100:.1f}%")
        
        # 数据集已通过增量写入保存，获取保存路径
        saved_path = str(Path("qa_datasets") / output_file)
        
        # 详细统计
        print(f"\n📊 生成统计:")
        print(f"   - 总QA对数: {len(qa_dataset)}")
        
        # 计算平均每文本的QA对数
        if args.test_mode:
            processed_texts = 5
        elif args.max_texts:
            processed_texts = args.max_texts
        else:
            # 估算处理的文本数量（假设每个文本平均生成4个QA对）
            processed_texts = len(qa_dataset) // 4 if len(qa_dataset) > 0 else 0
        
        if processed_texts > 0:
            print(f"   - 平均每文本: {len(qa_dataset) / processed_texts:.1f} 个QA对")
        print(f"   - 保存路径: {saved_path}")
        
        # 按生成方法统计
        method_counts = {}
        type_counts = {}
        
        for qa in qa_dataset:
            method = qa.get('generation_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
            
            q_type = qa.get('question_type', 'general')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        print(f"\n📋 生成方法分布:")
        for method, count in sorted(method_counts.items()):
            print(f"   - {method}: {count} 个QA对")
        
        print(f"\n📋 问题类型分布:")
        for q_type, count in sorted(type_counts.items()):
            percentage = count / len(qa_dataset) * 100
            print(f"   - {q_type}: {count} 个QA对 ({percentage:.1f}%)")
        
        # 长度统计
        question_lengths = [len(qa.get('question', '')) for qa in qa_dataset]
        answer_lengths = [len(qa.get('answer', '')) for qa in qa_dataset]
        
        if question_lengths and answer_lengths:
            print(f"\n📏 长度统计:")
            print(f"   - 问题平均长度: {sum(question_lengths) / len(question_lengths):.1f} 字符")
            print(f"   - 答案平均长度: {sum(answer_lengths) / len(answer_lengths):.1f} 字符")
            print(f"   - 问题长度范围: {min(question_lengths)} - {max(question_lengths)}")
            print(f"   - 答案长度范围: {min(answer_lengths)} - {max(answer_lengths)}")
        
        # 显示示例（如果请求）
        if args.show_samples and qa_dataset:
            print(f"\n📝 QA对示例:")
            
            # 按生成方法分组显示示例
            shown_methods = set()
            for qa in qa_dataset:
                method = qa.get('generation_method', 'unknown')
                if method not in shown_methods:
                    print(f"\n   【{method.upper()}方法生成】")
                    print(f"   问题: {qa['question']}")
                    print(f"   答案: {qa['answer'][:100]}{'...' if len(qa['answer']) > 100 else ''}")
                    if 'source_text' in qa:
                        print(f"   原文: {qa['source_text'][:80]}...")
                    shown_methods.add(method)
                    if len(shown_methods) >= 3:  # 最多显示3种方法的示例
                        break
        
        print(f"\n✅ 基于文本的QA数据集生成完成！")
        print(f"\n💡 使用提示:")
        print(f"   - 查看生成文件: {saved_path}")
        print(f"   - 查看更多示例: python generate_text_qa.py --show-samples")
        print(f"   - 测试模式: python generate_text_qa.py --test-mode")
        print(f"   - 限制处理数量: python generate_text_qa.py --max-texts 100")
        print(f"   - 处理全部文本: python generate_text_qa.py (默认)")
        
        print(f"\n🔍 生成流程说明:")
        print(f"   1. 从train数据集XML文件提取<text>标签内容")
        print(f"   2. 将文本作为查询输入RAG系统")
        print(f"   3. 通过RAG系统处理（检索+CoTKR重写）")
        print(f"   4. 使用prompt_templates构建专业prompt")
        print(f"   5. 发送给LLM生成4种类型的QA对")
        
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()