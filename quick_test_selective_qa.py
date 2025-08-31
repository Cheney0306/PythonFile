#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试选择性QA生成功能
"""

from enhanced_qa_generator import EnhancedQAGenerator

def quick_test():
    """快速测试"""
    print("🧪 快速测试选择性QA生成")
    print("=" * 50)
    
    # 测试排除类型问题
    print("📝 测试: 排除类型问题")
    generator = EnhancedQAGenerator(enabled_question_types=['sub', 'obj', 'rel'])
    
    print(f"✅ 生成器初始化成功")
    print(f"📋 启用的问题类型: {generator.question_types}")
    
    # 验证类型问题确实被排除
    if 'type' not in generator.question_types:
        print("✅ 类型问题已成功排除")
    else:
        print("❌ 类型问题未被排除")
    
    # 测试只生成主语问题
    print("\n📝 测试: 只生成主语问题")
    sub_generator = EnhancedQAGenerator(enabled_question_types=['sub'])
    
    print(f"📋 启用的问题类型: {sub_generator.question_types}")
    
    if sub_generator.question_types == ['sub']:
        print("✅ 主语问题配置正确")
    else:
        print("❌ 主语问题配置错误")

if __name__ == "__main__":
    quick_test()