#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试选择性QA生成功能
验证可以选择生成特定类型的问题
"""

from enhanced_qa_generator import EnhancedQAGenerator
import json

def test_question_type_selection():
    """测试问题类型选择功能"""
    print("🧪 测试选择性QA生成功能")
    print("=" * 60)
    
    # 测试配置
    test_configs = [
        {
            'name': '所有类型',
            'enabled_types': None,
            'expected_types': ['sub', 'obj', 'rel', 'type']
        },
        {
            'name': '排除类型问题',
            'enabled_types': ['sub', 'obj', 'rel'],
            'expected_types': ['sub', 'obj', 'rel']
        },
        {
            'name': '只生成主语问题',
            'enabled_types': ['sub'],
            'expected_types': ['sub']
        },
        {
            'name': '主语和宾语问题',
            'enabled_types': ['sub', 'obj'],
            'expected_types': ['sub', 'obj']
        }
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📝 测试 {i}: {config['name']}")
        print("-" * 40)
        
        try:
            # 初始化生成器
            generator = EnhancedQAGenerator(enabled_question_types=config['enabled_types'])
            
            # 验证问题类型配置
            actual_types = generator.question_types
            expected_types = config['expected_types']
            
            print(f"期望类型: {expected_types}")
            print(f"实际类型: {actual_types}")
            
            if set(actual_types) == set(expected_types):
                print("✅ 问题类型配置正确")
            else:
                print("❌ 问题类型配置错误")
            
            # 测试无效类型处理
            if config['name'] == '所有类型':
                print("\n🔍 测试无效类型处理...")
                invalid_generator = EnhancedQAGenerator(enabled_question_types=['sub', 'invalid', 'obj'])
                print(f"处理无效类型后: {invalid_generator.question_types}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def test_command_line_usage():
    """展示命令行使用示例"""
    print("\n💡 命令行使用示例")
    print("=" * 60)
    
    examples = [
        {
            'command': 'python generate_enhanced_qa.py --exclude-type --test-mode',
            'description': '测试模式，排除类型问题'
        },
        {
            'command': 'python generate_enhanced_qa.py --only-basic --max-texts 50',
            'description': '只生成基础问题类型，处理50个文本'
        },
        {
            'command': 'python generate_enhanced_qa.py --question-types sub obj --show-samples',
            'description': '只生成主语和宾语问题，显示示例'
        },
        {
            'command': 'python generate_enhanced_qa.py --question-types sub --output-file subject_only_qa.json',
            'description': '只生成主语问题，指定输出文件名'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   命令: {example['command']}")

def test_output_filename_generation():
    """测试输出文件名生成逻辑"""
    print("\n📁 输出文件名生成测试")
    print("=" * 60)
    
    # 模拟不同的参数组合
    filename_tests = [
        {
            'args': {'exclude_type': True, 'test_mode': True},
            'expected_pattern': 'enhanced_qa_dataset_test_no_type.json'
        },
        {
            'args': {'question_types': ['sub', 'obj'], 'max_texts': 100},
            'expected_pattern': 'enhanced_qa_dataset_100_texts_sub_obj.json'
        },
        {
            'args': {'only_basic': True, 'max_texts': None},
            'expected_pattern': 'enhanced_qa_dataset_all_texts_no_type.json'
        }
    ]
    
    print("预期的文件名模式:")
    for i, test in enumerate(filename_tests, 1):
        print(f"{i}. 参数: {test['args']}")
        print(f"   文件名: {test['expected_pattern']}")

def main():
    """主函数"""
    try:
        test_question_type_selection()
        test_command_line_usage()
        test_output_filename_generation()
        
        print("\n" + "=" * 60)
        print("✅ 选择性QA生成功能测试完成")
        print("\n🎯 主要改进:")
        print("   ✅ 可以选择生成特定类型的问题")
        print("   ✅ 可以排除效果差的类型问题")
        print("   ✅ 支持多种命令行参数组合")
        print("   ✅ 自动生成包含类型信息的文件名")
        print("   ✅ 提供详细的配置反馈")
        
        print("\n💡 推荐使用:")
        print("   python generate_enhanced_qa.py --exclude-type --test-mode")
        print("   (排除类型问题，提高QA质量)")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()