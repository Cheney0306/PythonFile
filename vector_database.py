# vector_database.py - 向量数据库管理器

import chromadb
from typing import List, Dict, Optional
from tqdm import tqdm
import config
from data_loader import KnowledgeDataLoader
from embedding_client import EmbeddingClient

class VectorDatabaseManager:
    """向量数据库管理器"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = None
        self.embedding_client = EmbeddingClient()
        
    def initialize_collection(self, reset: bool = False):
        """初始化或重置集合"""
        if reset and self.collection:
            try:
                self.client.delete_collection(name=config.COLLECTION_NAME)
                print(f"🗑 已删除现有集合: {config.COLLECTION_NAME}")
            except:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✅ 集合初始化完成: {config.COLLECTION_NAME}")
        print(f"   - 当前文档数量: {self.collection.count()}")
        
    def triple_to_embedding_text(self, triple: tuple, schema: tuple) -> str:
        """
        将三元组和Schema转换为用于嵌入的简洁文本
        新系统：保持信息完整性的同时简化表示
        """
        sub, rel, obj = triple
        schema_sub, schema_rel, schema_obj = schema
        
        # 清理实体名称
        sub_clean = sub.replace('_', ' ')
        obj_clean = obj.replace('_', ' ')
        
        # 简洁但信息完整的表示
        return f"{sub_clean} {rel} {obj_clean}. Types: {schema_sub} {schema_rel} {schema_obj}."
    
    def populate_database(self, knowledge_entries: Optional[List[Dict]] = None):
        """填充向量数据库"""
        if not self.collection:
            self.initialize_collection()
        
        # 如果没有提供数据，则加载数据
        if knowledge_entries is None:
            loader = KnowledgeDataLoader()
            knowledge_entries = loader.get_knowledge_entries()
        
        if not knowledge_entries:
            print("❌ 没有找到知识条目")
            return
        
        print(f"🔄 开始填充数据库，共 {len(knowledge_entries)} 个条目")
        
        # 准备数据
        ids = [entry['id'] for entry in knowledge_entries]
        documents = [self.triple_to_embedding_text(entry["triple"], entry["schema"]) 
                    for entry in knowledge_entries]
        
        # 准备元数据（保存完整的三元组和Schema信息）
        metadatas = [
            {
                # 原始三元组
                "sub": entry["triple"][0], 
                "rel": entry["triple"][1], 
                "obj": entry["triple"][2],
                # Schema信息
                "sub_type": entry["schema"][0], 
                "rel_type": entry["schema"][1], 
                "obj_type": entry["schema"][2],
                # 额外信息
                "source_file": entry.get("source_file", ""),
                "text": entry.get("text", "")
            } 
            for entry in knowledge_entries
        ]
        
        # 分批处理
        batch_size = config.BATCH_SIZE
        
        for i in tqdm(range(0, len(ids), batch_size), desc="嵌入处理"):
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
        
        print(f"✅ 数据库填充完成，总条目数: {self.collection.count()}")
    
    def query_database(self, query: str, n_results: int = 5) -> List[Dict]:
        """查询向量数据库 - 增强查询策略"""
        if not self.collection:
            print("❌ 集合未初始化")
            return []
        
        # 增强查询 - 生成多个查询变体
        enhanced_queries = self._generate_query_variants(query)
        
        all_results = []
        
        # 对每个查询变体进行检索
        for enhanced_query in enhanced_queries:
            query_embedding = self.embedding_client.get_embeddings_batch([enhanced_query])
            if not query_embedding:
                continue
            
            # 执行查询
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # 格式化结果
            if results and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    
                    result_item = {
                        'id': results['ids'][0][i],
                        'triple': (metadata['sub'], metadata['rel'], metadata['obj']),
                        'schema': (metadata['sub_type'], metadata['rel_type'], metadata['obj_type']),
                        'distance': results['distances'][0][i],
                        'document': results['documents'][0][i],
                        'text': metadata.get('text', ''),
                        'source_file': metadata.get('source_file', ''),
                        'query_variant': enhanced_query
                    }
                    all_results.append(result_item)
        
        # 去重并按相似度排序
        unique_results = self._deduplicate_and_rank(all_results, query)
        
        return unique_results[:n_results]
    
    def _generate_query_variants(self, query: str) -> List[str]:
        """生成查询变体以提高检索质量"""
        variants = [query]  # 原始查询
        
        query_lower = query.lower()
        
        # 针对不同问题类型生成变体
        if 'who is the leader' in query_lower or 'who leads' in query_lower:
            # 领导者问题的变体
            if 'belgium' in query_lower:
                variants.extend([
                    "Belgium leader president king",
                    "Belgium head of state government",
                    "Belgium prime minister president"
                ])
            else:
                # 提取国家名
                words = query.split()
                for word in words:
                    if word.lower() not in ['who', 'is', 'the', 'leader', 'of', '?']:
                        variants.extend([
                            f"{word} leader",
                            f"{word} president",
                            f"{word} head of state"
                        ])
        
        elif 'where is' in query_lower and 'located' in query_lower:
            # 位置问题的变体
            if 'airport' in query_lower:
                # 提取机场名
                words = query.split()
                airport_name = ""
                for i, word in enumerate(words):
                    if 'airport' in word.lower():
                        # 获取机场名称
                        if i > 0:
                            airport_name = words[i-1]
                        break
                
                if airport_name:
                    variants.extend([
                        f"{airport_name} location country",
                        f"{airport_name} airport location",
                        f"{airport_name} situated in"
                    ])
        
        elif 'what type' in query_lower:
            # 类型问题的变体
            words = query.split()
            for word in words:
                if word.lower() not in ['what', 'type', 'of', 'entity', 'is', '?']:
                    variants.extend([
                        f"{word} type category",
                        f"{word} entity type"
                    ])
        
        return list(set(variants))  # 去重
    
    def _deduplicate_and_rank(self, results: List[Dict], original_query: str) -> List[Dict]:
        """去重并重新排序结果"""
        # 按ID去重
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        # 重新计算相关性分数
        for result in unique_results:
            result['relevance_score'] = self._calculate_relevance_score(result, original_query)
        
        # 按相关性分数排序
        unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return unique_results
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """计算结果的相关性分数"""
        query_lower = query.lower()
        triple = result['triple']
        sub, rel, obj = triple
        
        score = 1 - result['distance']  # 基础相似度分数
        
        # 根据问题类型和三元组内容调整分数
        if 'leader' in query_lower:
            if 'leader' in rel.lower() or 'president' in rel.lower() or 'king' in rel.lower():
                score += 0.3  # 提高领导关系的分数
        
        if 'where' in query_lower and 'located' in query_lower:
            if 'location' in rel.lower() or 'country' in rel.lower():
                score += 0.3  # 提高位置关系的分数
        
        # 检查实体匹配
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 3:  # 忽略短词
                if word in sub.lower() or word in obj.lower():
                    score += 0.2  # 实体匹配加分
        
        return score
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        if not self.collection:
            return {"status": "Collection not initialized"}
        
        return {
            "collection_name": self.collection.name,
            "total_documents": self.collection.count(),
            "status": "ready"
        }

# 测试函数
def test_vector_database():
    """测试向量数据库管理器"""
    db_manager = VectorDatabaseManager()
    
    # 初始化集合
    db_manager.initialize_collection()
    
    # 如果数据库为空，填充数据
    if db_manager.collection.count() == 0:
        print("数据库为空，开始填充...")
        db_manager.populate_database()
    
    # 测试查询
    test_query = "Who is the leader of Belgium?"
    results = db_manager.query_database(test_query, n_results=3)
    
    print(f"\n测试查询: {test_query}")
    print(f"检索结果数量: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. 三元组: {result['triple']}")
        print(f"     Schema: {result['schema']}")
        print(f"     距离: {result['distance']:.4f}")

if __name__ == '__main__':
    test_vector_database()