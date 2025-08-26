# retrieval_engine.py - 检索引擎

from typing import List, Dict, Optional
from vector_database import VectorDatabaseManager
from cotkr_rewriter import CoTKRRewriter
import config

class RetrievalEngine:
    """新系统的检索引擎 - 集成CoTKR重写功能"""
    
    def __init__(self):
        self.db_manager = VectorDatabaseManager()
        self.cotkr_rewriter = CoTKRRewriter()
        
        # 初始化数据库连接
        self.db_manager.initialize_collection()
        
    def retrieve_and_rewrite(self, question: str, n_results: int = 5, prompt_type: str = None) -> Dict:
        """
        执行检索并使用CoTKR重写知识
        这是新系统的核心方法
        
        Args:
            question: 查询问题或文本
            n_results: 检索结果数量
            prompt_type: 问题类型 ('sub', 'obj', 'rel', 'type')，如果提供则直接使用，不进行检测
        """
        # 1. 直接使用原始问题进行向量检索
        retrieved_items = self.db_manager.query_database(question, n_results)
        
        if not retrieved_items:
            return {
                'question': question,
                'retrieved_items': [],
                'cotkr_knowledge': "No relevant information found.",
                'final_answer': "I don't have enough information to answer this question."
            }
        
        # 2. 使用CoTKR方法重写检索到的知识，传入prompt_type
        cotkr_knowledge = self.cotkr_rewriter.rewrite_knowledge(retrieved_items, question, prompt_type)
        
        # 3. 从重写的知识中提取答案
        final_answer = self.cotkr_rewriter.extract_answer_from_knowledge(
            question, cotkr_knowledge, retrieved_items, prompt_type
        )
        
        # 确定问题类型
        if prompt_type:
            # 如果提供了prompt_type，直接使用
            question_type = prompt_type
        else:
            # 否则检测问题类型
            is_question = question.strip().endswith('?') or any(question.lower().startswith(word) for word in ['who', 'what', 'where', 'when', 'why', 'how'])
            question_type = self.cotkr_rewriter.detect_question_type(question) if is_question else 'statement'
        
        return {
            'question': question,
            'retrieved_items': retrieved_items,
            'cotkr_knowledge': cotkr_knowledge,
            'final_answer': final_answer,
            'retrieval_stats': {
                'num_retrieved': len(retrieved_items),
                'avg_distance': sum(item['distance'] for item in retrieved_items) / len(retrieved_items) if retrieved_items else 0.0,
                'question_type': question_type
            }
        }
    
    def batch_retrieve(self, questions: List[str], n_results: int = 5) -> List[Dict]:
        """批量检索和重写"""
        results = []
        
        for question in questions:
            result = self.retrieve_and_rewrite(question, n_results)
            results.append(result)
        
        return results
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        db_stats = self.db_manager.get_database_stats()
        
        return {
            'system_name': 'New KG-RAG System with CoTKR',
            'database_status': db_stats,
            'components': {
                'vector_database': 'ChromaDB',
                'embedding_model': config.EMBEDDING_MODEL,
                'rewriter': 'CoTKR (Chain-of-Thought Knowledge Rewriting)',
                'api_provider': 'SiliconFlow'
            }
        }

# 测试函数
def test_retrieval_engine():
    """测试检索引擎"""
    engine = RetrievalEngine()
    
    # 测试问题
    test_questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport located?",
        "What is the runway length of the airport?",
        "How many countries are in Europe?"
    ]
    
    print("🔍 测试新系统检索引擎")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\n问题: {question}")
        result = engine.retrieve_and_rewrite(question)
        
        print(f"问题类型: {result['retrieval_stats']['question_type']}")
        print(f"检索数量: {result['retrieval_stats']['num_retrieved']}")
        print(f"平均距离: {result['retrieval_stats']['avg_distance']:.4f}")
        
        print("\nCoTKR重写知识:")
        print(result['cotkr_knowledge'])
        
        print(f"\n最终答案: {result['final_answer']}")
        print("-" * 50)

if __name__ == '__main__':
    test_retrieval_engine()