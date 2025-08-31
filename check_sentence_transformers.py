#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查sentence-transformers库是否可用
"""

def check_sentence_transformers():
    """检查sentence-transformers库"""
    try:
        from sentence_transformers import CrossEncoder
        print("✅ sentence-transformers库已安装")
        
        # 尝试加载模型
        try:
            print("🔄 尝试加载BAAI/bge-reranker-base模型...")
            model = CrossEncoder('BAAI/bge-reranker-base', max_length=512)
            print("✅ 模型加载成功")
            
            # 测试模型
            test_pairs = [
                ["Who is the leader of Belgium?", "Belgium is led by Philippe of Belgium"],
                ["Who is the leader of Belgium?", "Amsterdam Airport is located in Netherlands"]
            ]
            
            scores = model.predict(test_pairs)
            print(f"🧪 测试预测: {scores}")
            print("✅ 模型功能正常")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False
            
    except ImportError:
        print("❌ sentence-transformers库未安装")
        print("💡 安装命令: pip install sentence-transformers")
        return False
    
    return True

if __name__ == "__main__":
    check_sentence_transformers()