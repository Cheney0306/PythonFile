# qa_system_demo.py - 问答系统演示

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from retrieval_engine import RetrievalEngine
import json
from datetime import datetime
from typing import Dict, List

class QASystem:
    """完整的问答系统"""
    
    def __init__(self):
        self.engine = RetrievalEngine()
        print("🚀 问答系统初始化完成")
        
        # 检查系统状态
        status = self.engine.get_system_status()
        print(f"📊 系统状态: {status['system_name']}")
        print(f"📚 数据库文档数: {status['database_status']['total_documents']}")
        print("=" * 60)
    
    def ask_question(self, question: str, show_details: bool = False) -> Dict:
        """
        问答系统的主要接口
        
        Args:
            question: 用户问题
            show_details: 是否显示详细的RAG流程信息
        
        Returns:
            包含答案和详细信息的字典
        """
        print(f"❓ 问题: {question}")
        
        # 执行完整的RAG流程
        result = self.engine.retrieve_and_rewrite(question)
        
        # 显示答案
        print(f"💡 答案: {result['final_answer']}")
        
        if show_details:
            self._show_rag_details(result)
        
        return result
    
    def _show_rag_details(self, result: Dict):
        """显示RAG流程的详细信息"""
        print("\n🔍 RAG流程详情:")
        print("-" * 40)
        
        # 1. 检索统计
        stats = result['retrieval_stats']
        print(f"📊 检索统计:")
        print(f"   - 问题类型: {stats['question_type']}")
        print(f"   - 检索文档数: {stats['num_retrieved']}")
        print(f"   - 平均相似度: {1 - stats['avg_distance']:.4f}")
        
        # 2. 检索到的知识
        print(f"\n📚 检索到的知识:")
        for i, item in enumerate(result['retrieved_items'][:3], 1):  # 只显示前3个
            triple = item['triple']
            schema = item['schema']
            distance = item['distance']
            
            print(f"   {i}. 三元组: {triple}")
            print(f"      Schema: {schema}")
            print(f"      相似度: {1 - distance:.4f}")
        
        # 3. CoTKR重写的知识
        print(f"\n🧠 CoTKR重写知识:")
        knowledge_lines = result['cotkr_knowledge'].split('\n')
        for line in knowledge_lines[:5]:  # 只显示前5行
            if line.strip():
                print(f"   {line}")
        if len(knowledge_lines) > 5:
            print(f"   ... (还有 {len(knowledge_lines) - 5} 行)")
        
        print("-" * 40)
    
    def interactive_qa(self):
        """交互式问答模式"""
        print("\n🎯 进入交互式问答模式")
        print("💡 输入问题，系统将通过RAG流程为您提供答案")
        print("💡 输入 'quit' 或 'exit' 退出")
        print("💡 输入 'details on/off' 切换详细信息显示")
        print("=" * 60)
        
        show_details = False
        
        while True:
            try:
                user_input = input("\n❓ 请输入您的问题: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 感谢使用问答系统！")
                    break
                
                if user_input.lower() == 'details on':
                    show_details = True
                    print("✅ 已开启详细信息显示")
                    continue
                
                if user_input.lower() == 'details off':
                    show_details = False
                    print("✅ 已关闭详细信息显示")
                    continue
                
                if not user_input:
                    print("⚠ 请输入有效问题")
                    continue
                
                # 执行问答
                result = self.ask_question(user_input, show_details)
                
            except KeyboardInterrupt:
                print("\n👋 感谢使用问答系统！")
                break
            except Exception as e:
                print(f"❌ 处理问题时出错: {e}")
    
    def batch_qa(self, questions: List[str], save_results: bool = False) -> List[Dict]:
        """批量问答"""
        print(f"\n📋 批量问答模式 - 处理 {len(questions)} 个问题")
        print("=" * 60)
        
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}/{len(questions)}. {question}")
            result = self.engine.retrieve_and_rewrite(question)
            print(f"💡 {result['final_answer']}")
            results.append(result)
        
        if save_results:
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qa_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 结果已保存到: {filename}")
        
        return results

def demo_qa_system():
    """演示问答系统的功能"""
    print("🎯 问答系统演示")
    print("🔄 完整RAG流程: 问题 → 向量检索 → CoTKR重写 → 答案提取")
    print("=" * 70)
    
    # 初始化问答系统
    qa_system = QASystem()
    
    # 演示问题
    demo_questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport Schiphol located?",
        "What is the runway length of Amsterdam Airport?",
        "What type of entity is Belgium?",
        "What is the relationship between Amsterdam Airport and Netherlands?"
    ]
    
    print("\n📝 演示问题:")
    for i, q in enumerate(demo_questions, 1):
        print(f"   {i}. {q}")
    
    print("\n🔄 开始演示...")
    
    # 逐个回答问题，显示详细信息
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'='*60}")
        print(f"演示 {i}/{len(demo_questions)}")
        qa_system.ask_question(question, show_details=True)
        
        if i < len(demo_questions):
            input("\n⏸ 按回车键继续下一个问题...")
    
    print(f"\n{'='*60}")
    print("✅ 演示完成！")
    
    # 询问是否进入交互模式
    user_choice = input("\n🤔 是否进入交互式问答模式？(y/n): ").strip().lower()
    if user_choice in ['y', 'yes', '是']:
        qa_system.interactive_qa()

def quick_test():
    """快速测试问答功能"""
    print("⚡ 快速测试问答系统")
    print("=" * 40)
    
    qa_system = QASystem()
    
    # 快速测试几个问题
    test_questions = [
        "Who leads Belgium?",
        "Where is Amsterdam Airport?",
        "What is Belgium?"
    ]
    
    for question in test_questions:
        print(f"\n❓ {question}")
        result = qa_system.engine.retrieve_and_rewrite(question)
        print(f"💡 {result['final_answer']}")
        print(f"🏷 类型: {result['retrieval_stats']['question_type']}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        quick_test()
    else:
        demo_qa_system()