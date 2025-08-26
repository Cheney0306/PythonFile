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
        """查询向量数据库"""
        if not self.collection:
            print("❌ 集合未初始化")
            return []
        
        # 获取查询嵌入
        query_embedding = self.embedding_client.get_embeddings_batch([query])
        if not query_embedding:
            print("❌ 查询嵌入失败")
            return []
        
        # 执行查询
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
                    'source_file': metadata.get('source_file', '')
                })
        
        return formatted_results
    
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