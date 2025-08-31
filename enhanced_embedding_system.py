# enhanced_embedding_system.py - 增强的嵌入系统

import chromadb
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm
import config
from data_loader import KnowledgeDataLoader
from embedding_client import EmbeddingClient
import numpy as np
from collections import defaultdict

# 新增：导入sentence-transformers的CrossEncoder
try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers未安装，将使用原有的重排方法")
    CROSS_ENCODER_AVAILABLE = False

class EnhancedVectorDatabaseManager:
    """增强的向量数据库管理器 - 实现更好的嵌入策略和多阶段检索"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = None
        self.embedding_client = EmbeddingClient()
        
        # 【新】初始化Cross-Encoder重排模型
        self.rerank_model = None
        if CROSS_ENCODER_AVAILABLE:
            try:
                print("🔄 加载Cross-Encoder重排模型...")
                self.rerank_model = CrossEncoder('BAAI/bge-reranker-base', max_length=512)
                print("✅ Cross-Encoder模型加载成功")
            except Exception as e:
                print(f"⚠️ Cross-Encoder模型加载失败: {e}")
                self.rerank_model = None
        
    def initialize_collection(self, collection_name: str = None, reset: bool = False):
        """初始化或重置集合"""
        if collection_name is None:
            collection_name = config.COLLECTION_NAME + "_enhanced"
            
        if reset and self.collection:
            try:
                self.client.delete_collection(name=collection_name)
                print(f"🗑 已删除现有集合: {collection_name}")
            except:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✅ 增强集合初始化完成: {collection_name}")
        print(f"   - 当前文档数量: {self.collection.count()}")
        
    def enhanced_triple_to_text(self, triple: tuple, schema: tuple) -> str:
        """
        增强的三元组到文本转换 - 使用更自然的模板句子
        
        Args:
            triple: (subject, relation, object)
            schema: (subject_type, relation_type, object_type)
        """
        sub, rel, obj = triple
        schema_sub, schema_rel, schema_obj = schema
        
        # 清理实体名称
        sub_clean = sub.replace('_', ' ')
        obj_clean = obj.replace('_', ' ')
        rel_clean = rel.replace('_', ' ')
        
        # 使用更自然的模板句子
        template = (f"An instance of a '{schema_sub}' named '{sub_clean}' "
                   f"has a relation '{rel_clean}' "
                   f"with an instance of a '{schema_obj}' which is '{obj_clean}'.")
        
        return template
    
    def create_enhanced_metadata(self, entry: Dict) -> Dict:
        """
        创建增强的元数据，包含完整的结构化信息
        
        Args:
            entry: 包含triple, schema等信息的条目
        """
        triple = entry["triple"]
        schema = entry["schema"]
        
        sub, rel, obj = triple
        sub_type, rel_type, obj_type = schema
        
        # 清理名称
        sub_clean = sub.replace('_', ' ')
        obj_clean = obj.replace('_', ' ')
        rel_clean = rel.replace('_', ' ')
        
        metadata = {
            # 原始三元组信息
            "sub": sub,
            "rel": rel, 
            "obj": obj,
            "sub_type": sub_type,
            "rel_type": rel_type,
            "obj_type": obj_type,
            
            # 清理后的名称
            "sub_clean": sub_clean,
            "rel_clean": rel_clean,
            "obj_clean": obj_clean,
            
            # 额外的检索辅助信息
            "entities": f"{sub_clean} {obj_clean}",  # 实体组合
            "relation_context": f"{sub_type} {rel_clean} {obj_type}",  # 关系上下文
            "full_context": f"{sub_clean} {rel_clean} {obj_clean} {sub_type} {obj_type}",  # 完整上下文
            
            # 原有信息
            "source_file": entry.get("source_file", ""),
            "text": entry.get("text", "")
        }
        
        return metadata
    
    def populate_enhanced_database(self, knowledge_entries: Optional[List[Dict]] = None):
        """使用增强策略填充向量数据库"""
        if not self.collection:
            self.initialize_collection()
        
        # 如果没有提供数据，则加载数据
        if knowledge_entries is None:
            loader = KnowledgeDataLoader()
            knowledge_entries = loader.get_knowledge_entries()
        
        if not knowledge_entries:
            print("❌ 没有找到知识条目")
            return
        
        print(f"🔄 开始填充增强数据库，共 {len(knowledge_entries)} 个条目")
        
        # 准备数据
        ids = [entry['id'] for entry in knowledge_entries]
        
        # 使用增强的文本转换
        documents = [self.enhanced_triple_to_text(entry["triple"], entry["schema"]) 
                    for entry in knowledge_entries]
        
        # 创建增强的元数据
        metadatas = [self.create_enhanced_metadata(entry) for entry in knowledge_entries]
        
        # 分批处理
        batch_size = config.BATCH_SIZE
        
        for i in tqdm(range(0, len(ids), batch_size), desc="增强嵌入处理"):
            batch_ids = ids[i:i+batch_size]
            batch_documents = documents[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            
            # 获取嵌入向量
            batch_embeddings = self.embedding_client.get_embeddings_batch(batch_documents)
            
            if batch_embeddings:
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
            else:
                print(f"⚠ 跳过批次 {i}，嵌入失败")
        
        print(f"✅ 增强数据库填充完成，总条目数: {self.collection.count()}")
    
    def multi_stage_retrieval(self, query: str, n_results: int = 10, 
                             rerank_top_k: int = 20, rerank_method: str = 'original') -> List[Dict]:
        """
        多阶段检索重排
        
        Args:
            query: 查询问题
            n_results: 最终返回的结果数量
            rerank_top_k: 第一阶段检索的数量，用于重排
            rerank_method: 重排方法 ('original' 或 'cross_encoder')
        """
        if not self.collection:
            print("❌ 集合未初始化")
            return []
        
        # 第一阶段：扩大检索范围
        stage1_results = self._stage1_retrieval(query, rerank_top_k)
        
        if not stage1_results:
            return []
        
        # 第二阶段：选择重排方法
        if rerank_method == 'cross_encoder' and self.rerank_model is not None:
            stage2_results = self._stage2_cross_encoder_reranking(query, stage1_results)
        else:
            # 使用原有的多策略重排
            stage2_results = self._stage2_reranking(query, stage1_results)
        
        # 返回Top-K结果
        return stage2_results[:n_results]
    
    def _stage1_retrieval(self, query: str, n_results: int) -> List[Dict]:
        """第一阶段：基础向量检索"""
        # 获取查询嵌入
        query_embedding = self.embedding_client.get_embeddings_batch([query])
        if not query_embedding:
            print("❌ 查询嵌入失败")
            return []
        
        # 执行向量检索
        results = self.collection.query(
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
                    'metadata': metadata,
                    'stage1_score': 1 - results['distances'][0][i]  # 转换为相似度分数
                })
        
        return formatted_results
    
    def _stage2_reranking(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """第二阶段：多策略重排"""
        
        # 计算多种相关性分数
        for candidate in candidates:
            scores = {}
            
            # 1. 实体匹配分数
            scores['entity_match'] = self._calculate_entity_match_score(query, candidate)
            
            # 2. 关系匹配分数  
            scores['relation_match'] = self._calculate_relation_match_score(query, candidate)
            
            # 3. 类型匹配分数
            scores['type_match'] = self._calculate_type_match_score(query, candidate)
            
            # 4. 语义相似度分数 (来自第一阶段)
            scores['semantic_similarity'] = candidate['stage1_score']
            
            # 5. 综合分数 (可调权重)
            weights = {
                'entity_match': 0.3,
                'relation_match': 0.25, 
                'type_match': 0.2,
                'semantic_similarity': 0.25
            }
            
            final_score = sum(weights[key] * scores[key] for key in weights)
            candidate['rerank_score'] = final_score
            candidate['detailed_scores'] = scores
        
        # 按重排分数排序
        candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return candidates
    
    def _stage2_cross_encoder_reranking(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """第二阶段：【新方法】使用Cross-Encoder模型进行重排"""
        if not candidates:
            return []
        
        if self.rerank_model is None:
            print("⚠️ Cross-Encoder模型未加载，回退到原有重排方法")
            return self._stage2_reranking(query, candidates)
        
        try:
            # 创建模型需要输入的句子对：(查询, 候选文档的文本)
            sentence_pairs = [[query, candidate['document']] for candidate in candidates]
            
            # 模型会为每个句子对计算一个相关性分数
            scores = self.rerank_model.predict(sentence_pairs)
            
            # 将分数添加回候选文档中
            for i in range(len(candidates)):
                candidates[i]['rerank_score'] = float(scores[i])
                candidates[i]['rerank_method'] = 'cross_encoder'
                # 保留原有的详细分数用于对比
                candidates[i]['original_stage1_score'] = candidates[i].get('stage1_score', 0)
            
            # 按新的重排分数降序排序
            candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            return candidates
            
        except Exception as e:
            print(f"⚠️ Cross-Encoder重排失败: {e}")
            # 回退到原有重排方法
            return self._stage2_reranking(query, candidates)
    
    def _calculate_entity_match_score(self, query: str, candidate: Dict) -> float:
        """计算实体匹配分数"""
        query_lower = query.lower()
        metadata = candidate['metadata']
        
        score = 0.0
        
        # 检查主语实体匹配
        sub_clean = metadata['sub_clean'].lower()
        if sub_clean in query_lower:
            score += 0.5
        
        # 检查宾语实体匹配
        obj_clean = metadata['obj_clean'].lower()
        if obj_clean in query_lower:
            score += 0.5
        
        # 部分匹配
        sub_words = sub_clean.split()
        obj_words = obj_clean.split()
        query_words = query_lower.split()
        
        for word in sub_words + obj_words:
            if len(word) > 3 and word in query_words:
                score += 0.1
        
        return min(score, 1.0)  # 限制在[0,1]范围
    
    def _calculate_relation_match_score(self, query: str, candidate: Dict) -> float:
        """计算关系匹配分数"""
        query_lower = query.lower()
        metadata = candidate['metadata']
        
        score = 0.0
        
        # 关系词匹配
        rel_clean = metadata['rel_clean'].lower()
        rel_words = rel_clean.split()
        
        # 定义关系关键词映射
        relation_keywords = {
            'leader': ['leader', 'president', 'king', 'queen', 'head', 'chief'],
            'location': ['location', 'located', 'place', 'where', 'country', 'city'],
            'capital': ['capital'],
            'type': ['type', 'kind', 'category'],
            'runway': ['runway', 'strip'],
            'owner': ['owner', 'owned', 'belong']
        }
        
        # 检查直接匹配
        for rel_word in rel_words:
            if rel_word in query_lower:
                score += 0.4
        
        # 检查语义匹配
        for rel_type, keywords in relation_keywords.items():
            if rel_type in rel_clean:
                for keyword in keywords:
                    if keyword in query_lower:
                        score += 0.3
                        break
        
        return min(score, 1.0)
    
    def _calculate_type_match_score(self, query: str, candidate: Dict) -> float:
        """计算类型匹配分数"""
        query_lower = query.lower()
        metadata = candidate['metadata']
        
        score = 0.0
        
        # 类型关键词映射
        type_keywords = {
            'country': ['country', 'nation'],
            'airport': ['airport'],
            'city': ['city', 'town'],
            'person': ['person', 'people', 'who'],
            'organization': ['organization', 'company'],
            'location': ['location', 'place', 'where']
        }
        
        sub_type = metadata['sub_type'].lower()
        obj_type = metadata['obj_type'].lower()
        
        # 检查类型匹配
        for entity_type in [sub_type, obj_type]:
            if entity_type in query_lower:
                score += 0.4
            
            # 检查语义匹配
            for type_name, keywords in type_keywords.items():
                if type_name in entity_type:
                    for keyword in keywords:
                        if keyword in query_lower:
                            score += 0.2
                            break
        
        return min(score, 1.0)
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        if not self.collection:
            return {"status": "Collection not initialized"}
        
        return {
            "collection_name": self.collection.name,
            "total_documents": self.collection.count(),
            "status": "ready",
            "enhancement": "multi-stage retrieval with reranking"
        }

# 测试函数
def test_enhanced_system():
    """测试增强系统"""
    print("🧪 测试增强嵌入系统")
    print("=" * 50)
    
    # 初始化增强系统
    enhanced_db = EnhancedVectorDatabaseManager()
    enhanced_db.initialize_collection(reset=True)
    
    # 填充数据库
    print("📊 填充增强数据库...")
    enhanced_db.populate_enhanced_database()
    
    # 测试查询
    test_queries = [
        "Who is the leader of Belgium?",
        "Where is Amsterdam Airport Schiphol located?",
        "What type of entity is Belgium?"
    ]
    
    for query in test_queries:
        print(f"\n❓ 查询: {query}")
        
        # 多阶段检索
        results = enhanced_db.multi_stage_retrieval(query, n_results=5)
        
        print("🔍 多阶段检索结果:")
        for i, result in enumerate(results, 1):
            triple = result['triple']
            rerank_score = result['rerank_score']
            detailed_scores = result['detailed_scores']
            
            print(f"   {i}. {triple}")
            print(f"      重排分数: {rerank_score:.4f}")
            print(f"      详细分数: {detailed_scores}")

if __name__ == '__main__':
    test_enhanced_system()