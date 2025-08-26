# simple_qa.py - 简单问答接口

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from retrieval_engine import RetrievalEngine

def main():
    """简单的问答系统主函数"""
    print("🤖 KG-RAG 问答系统")
    print("🔄 RAG流程: 问题 → 向量检索 → CoTKR重写 → 答案生成")
    print("=" * 50)
    
    # 初始化系统
    try:
        engine = RetrievalEngine()
        status = engine.get_system_status()
        print(f"✅ 系统就绪 - 数据库文档数: {status['database_status']['total_documents']}")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        return
    
    print("\n💡 输入问题开始问答，输入 'quit' 退出")
    print("=" * 50)
    
    while True:
        try:
            # 获取用户输入
            question = input("\n❓ 请输入问题: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！")
                break
            
            if not question:
                print("⚠ 请输入有效问题")
                continue
            
            # 执行RAG问答
            print("🔄 正在处理...")
            result = engine.retrieve_and_rewrite(question)
            
            # 显示结果
            print(f"💡 答案: {result['final_answer']}")
            print(f"🏷 问题类型: {result['retrieval_stats']['question_type']}")
            print(f"📊 检索到 {result['retrieval_stats']['num_retrieved']} 个相关文档")
            
            # 询问是否显示详细信息
            show_detail = input("🔍 显示详细RAG流程？(y/n): ").strip().lower()
            if show_detail in ['y', 'yes', '是']:
                print("\n📚 检索到的知识:")
                for i, item in enumerate(result['retrieved_items'][:3], 1):
                    triple = item['triple']
                    similarity = 1 - item['distance']
                    print(f"   {i}. {triple} (相似度: {similarity:.3f})")
                
                print(f"\n🧠 CoTKR重写知识:")
                knowledge_lines = result['cotkr_knowledge'].split('\n')
                for line in knowledge_lines[:3]:
                    if line.strip():
                        print(f"   {line}")
                if len(knowledge_lines) > 3:
                    print(f"   ... (共 {len(knowledge_lines)} 行)")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 处理问题时出错: {e}")

def test_questions():
    """测试一些预设问题"""
    print("🧪 测试预设问题")
    print("=" * 30)
    
    engine = RetrievalEngine()
    
    questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport located?", 
        "What is the runway length?",
        "What type of entity is Belgium?",
        "What country is Amsterdam Airport in?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. ❓ {question}")
        result = engine.retrieve_and_rewrite(question)
        print(f"   💡 {result['final_answer']}")
        print(f"   🏷 {result['retrieval_stats']['question_type']}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_questions()
    else:
        main()