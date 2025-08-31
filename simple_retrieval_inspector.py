#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的检索数据检查器 - 只显示原始内容
"""

from enhanced_embedding_system import EnhancedVectorDatabaseManager

def main():
    # 初始化系统
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_db.initialize_collection()
    
    # 测试查询
    query = "Who is the leader of Belgium?"
    print(f"查询: {query}")
    
    # 获取检索结果
    results = enhanced_db.multi_stage_retrieval(query, n_results=3)
    
    if not results:
        print("没有检索结果")
        return
    
    print(f"\n检索到 {len(results)} 个结果:")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"三元组: {result['triple']}")
        print(f"类型: {result['schema']}")
        print(f"原始文本: {result['text']}")
        print(f"来源文件: {result['source_file']}")

if __name__ == "__main__":
    main()