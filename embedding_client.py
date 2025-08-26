# embedding_client.py - 嵌入客户端

import requests
import time
from typing import List, Optional
import config

class EmbeddingClient:
    """嵌入客户端，负责调用API获取向量表示"""
    
    def __init__(self):
        self.api_url = config.SILICONFLOW_API_URL
        self.api_key = config.SILICONFLOW_API_KEY
        self.model = config.EMBEDDING_MODEL
        self.log_file = config.EMBEDDING_LOG_FILE
        
    def save_log(self, texts: List[str], embeddings: List[List[float]]):
        """将文本和其对应的向量追加写入到日志文件中"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for text, embedding in zip(texts, embeddings):
                    f.write(f"Input: {text}\n")
                    embedding_str = ",".join(map(str, embedding))
                    f.write(f"Output: {embedding_str}\n")
                    f.write("--\n")
        except IOError as e:
            print(f"Error writing to log file {self.log_file}: {e}")

    def get_embeddings_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        使用SiliconFlow API为一批文本获取embeddings
        包含针对特定错误的智能处理和重试逻辑
        """
        if not texts:
            return None
            
        payload = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float"
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code == 413:
                    print(f"API Error (413): Payload is too large. "
                          f"The current batch of {len(texts)} items is too big for the API. "
                          f"Consider reducing BATCH_SIZE further in config.py.")
                    return None

                response.raise_for_status()
                
                response_data = response.json()
                embeddings = [item['embedding'] for item in response_data['data']]
                
                # 保存到日志文件
                if embeddings:
                    self.save_log(texts, embeddings)
                
                return embeddings
                
            except requests.exceptions.RequestException as e:
                print(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print("Max retries reached. Failed to get embeddings for this batch.")
                    return None
        return None
    
    def get_single_embedding(self, text: str) -> Optional[List[float]]:
        """获取单个文本的嵌入向量"""
        result = self.get_embeddings_batch([text])
        return result[0] if result else None

# 全局实例
embedding_client = EmbeddingClient()

# 向后兼容的函数
def get_embeddings_batch(texts: List[str]) -> Optional[List[List[float]]]:
    """向后兼容的函数"""
    return embedding_client.get_embeddings_batch(texts)

# 测试函数
def test_embedding_client():
    """测试嵌入客户端"""
    client = EmbeddingClient()
    
    test_texts = [
        "Belgium leader Philippe of Belgium. Types: Country leader Royalty.",
        "Amsterdam Airport Schiphol location Haarlemmermeer. Types: Airport location City."
    ]
    
    print("Testing embedding client...")
    embeddings = client.get_embeddings_batch(test_texts)
    
    if embeddings:
        print(f"✅ Successfully got embeddings for {len(embeddings)} texts")
        print(f"   Embedding dimension: {len(embeddings[0])}")
    else:
        print("❌ Failed to get embeddings")

if __name__ == '__main__':
    test_embedding_client()