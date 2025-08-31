# enhanced_retrieval_engine.py - 增强的检索引擎

from typing import List, Dict, Optional
from enhanced_embedding_system import EnhancedVectorDatabaseManager
from cotkr_rewriter import CoTKRRewriter
import config

class EnhancedRetrievalEngine:
    """增强的检索引擎 - 使用多阶段检索和更好的嵌入策略"""
    
    def __init__(self):
        self.db_manager = EnhancedVectorDatabaseManager()
        self.cotkr_rewriter = CoTKRRewriter()
        
        # 初始化数据库连接
        self.db_manager.initialize_collection()
        
    def retrieve_and_rewrite(self, question: str, n_results: int = 5, 
                           prompt_type: str = None, use_reranking: bool = True) -> Dict:
        """
        执行增强的检索并使用CoTKR重写知识
        
        Args:
            question: 查询问题或文本
            n_results: 检索结果数量
            prompt_type: 问题类型 ('sub', 'obj', 'rel', 'type')
            use_reranking: 是否使用多阶段重排
        """
        # 1. 使用增强的多阶段检索 (使用Cross-Encoder重排)
        if use_reranking:
            retrieved_items = self.db_manager.multi_stage_retrieval(
                query=question, 
                n_results=n_results,
                rerank_top_k=n_results * config.RERANK_TOP_K_MULTIPLIER,  # 扩大初始检索范围
                rerank_method='cross_encoder'  # 使用Cross-Encoder重排方法
            )
        else:
            # 回退到基础检索（用于对比）
            retrieved_items = self._basic_retrieval(question, n_results)
        
        if not retrieved_items:
            return {
                'question': question,
                'retrieved_items': [],
                'cotkr_knowledge': "No relevant information found.",
                'final_answer': "I don't have enough information to answer this question.",
                'retrieval_method': 'enhanced_multi_stage' if use_reranking else 'basic'
            }
        
        # 2. 使用CoTKR方法重写检索到的知识
        cotkr_knowledge = self.cotkr_rewriter.rewrite_knowledge(retrieved_items, question, prompt_type)
        
        # 3. 从重写的知识中提取答案
        final_answer = self.cotkr_rewriter.extract_answer_from_knowledge(
            question, cotkr_knowledge, retrieved_items, prompt_type
        )
        
        # 确定问题类型
        if prompt_type:
            question_type = prompt_type
        else:
            is_question = question.strip().endswith('?') or any(question.lower().startswith(word) for word in ['who', 'what', 'where', 'when', 'why', 'how'])
            question_type = self.cotkr_rewriter.detect_question_type(question) if is_question else 'statement'
        
        # 计算增强的统计信息
        enhanced_stats = self._calculate_enhanced_stats(retrieved_items, use_reranking)
        
        return {
            'question': question,
            'retrieved_items': retrieved_items,
            'cotkr_knowledge': cotkr_knowledge,
            'final_answer': final_answer,
            'retrieval_stats': {
                'num_retrieved': len(retrieved_items),
                'avg_distance': sum(item['distance'] for item in retrieved_items) / len(retrieved_items) if retrieved_items else 0.0,
                'question_type': question_type,
                'retrieval_method': 'enhanced_multi_stage' if use_reranking else 'basic',
                **enhanced_stats
            }
        }
    
    def _basic_retrieval(self, query: str, n_results: int) -> List[Dict]:
        """基础检索方法（用于对比）"""
        # 获取查询嵌入
        query_embedding = self.db_manager.embedding_client.get_embeddings_batch([query])
        if not query_embedding:
            return []
        
        # 执行查询
        results = self.db_manager.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # 格式化结果
        formatted_results = []
        
        if results and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'triple': (metadata['sub'], metadata['rel'], metadata['obj']),
                    'schema': (metadata['sub_type'], metadata['rel_type'], metadata['obj_type']),
                    'distance': results['distances'][0][i],
                    'document': results['documents'][0][i],
                    'text': metadata.get('text', ''),
                    'source_file': metadata.get('source_file', ''),
                    'metadata': metadata if 'sub_clean' in metadata else None
                })
        
        return formatted_results
    
    def _calculate_enhanced_stats(self, retrieved_items: List[Dict], use_reranking: bool) -> Dict:
        """计算增强的统计信息"""
        stats = {}
        
        if use_reranking and retrieved_items:
            # 重排分数统计
            rerank_scores = [item.get('rerank_score', 0) for item in retrieved_items]
            if rerank_scores:
                stats['avg_rerank_score'] = sum(rerank_scores) / len(rerank_scores)
                stats['max_rerank_score'] = max(rerank_scores)
                stats['min_rerank_score'] = min(rerank_scores)
            
            # 详细分数统计
            if 'detailed_scores' in retrieved_items[0]:
                detailed_scores = retrieved_items[0]['detailed_scores']
                for score_type, score_value in detailed_scores.items():
                    stats[f'top1_{score_type}'] = score_value
        
        return stats
    
    def compare_retrieval_methods(self, question: str, n_results: int = 5) -> Dict:
        """对比不同检索方法的效果"""
        
        # 基础检索
        basic_result = self.retrieve_and_rewrite(question, n_results, use_reranking=False)
        
        # 增强检索
        enhanced_result = self.retrieve_and_rewrite(question, n_results, use_reranking=True)
        
        return {
            'question': question,
            'basic_method': {
                'retrieved_items': basic_result['retrieved_items'],
                'final_answer': basic_result['final_answer'],
                'stats': basic_result['retrieval_stats']
            },
            'enhanced_method': {
                'retrieved_items': enhanced_result['retrieved_items'],
                'final_answer': enhanced_result['final_answer'],
                'stats': enhanced_result['retrieval_stats']
            }
        }
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        db_stats = self.db_manager.get_database_stats()
        
        return {
            'system_name': 'Enhanced KG-RAG System with Multi-Stage Retrieval',
            'database_status': db_stats,
            'components': {
                'vector_database': 'ChromaDB Enhanced',
                'embedding_model': config.EMBEDDING_MODEL,
                'rewriter': 'CoTKR (Chain-of-Thought Knowledge Rewriting)',
                'api_provider': 'SiliconFlow',
                'enhancements': [
                    'Natural language templates',
                    'Rich metadata',
                    'Multi-stage retrieval',
                    'Reranking with multiple signals'
                ]
            }
        }

# 测试函数
def test_enhanced_retrieval_engine():
    """测试增强检索引擎"""
    engine = EnhancedRetrievalEngine()
    
    # 测试问题
    test_questions = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport located?",
        "What is the runway length of the airport?",
        "What type of entity is Belgium?"
    ]
    
    print("🔍 测试增强检索引擎")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        # 对比两种方法
        comparison = engine.compare_retrieval_methods(question)
        
        print("📊 基础方法:")
        print(f"   答案: {comparison['basic_method']['final_answer']}")
        print(f"   平均距离: {comparison['basic_method']['stats']['avg_distance']:.4f}")
        
        print("🚀 增强方法:")
        print(f"   答案: {comparison['enhanced_method']['final_answer']}")
        print(f"   平均距离: {comparison['enhanced_method']['stats']['avg_distance']:.4f}")
        if 'avg_rerank_score' in comparison['enhanced_method']['stats']:
            print(f"   平均重排分数: {comparison['enhanced_method']['stats']['avg_rerank_score']:.4f}")
        
        print("-" * 50)

if __name__ == '__main__':
    test_enhanced_retrieval_engine()