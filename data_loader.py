# data_loader.py - 数据加载器

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Tuple, Optional
import config

class KnowledgeDataLoader:
    """知识数据加载器"""
    
    def __init__(self):
        self.dataset_paths = config.DATASET_PATHS
        
    def parse_xml_file(self, file_path: str) -> List[Dict]:
        """解析单个XML文件，提取所有entry的数据"""
        entries = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for entry_node in root.findall('.//entry'):
                entry_id = entry_node.get('id')
                
                # 提取 triple
                triple_node = entry_node.find('triples/triple')
                if triple_node is None: 
                    continue
                    
                triple = (
                    triple_node.find('sub').text,
                    triple_node.find('rel').text,
                    triple_node.find('obj').text
                )

                # 提取 schema
                schema_node = entry_node.find('schemas/schema')
                if schema_node is None: 
                    continue
                    
                schema = (
                    schema_node.find('sub').text,
                    schema_node.find('rel').text,
                    schema_node.find('obj').text
                )
                
                # 提取 text（如果存在）
                text_node = entry_node.find('text')
                text = text_node.text if text_node is not None else ""
                
                entries.append({
                    "id": entry_id,
                    "triple": triple,
                    "schema": schema,
                    "text": text.strip() if text else "",
                    "source_file": str(file_path)
                })
                
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error parsing {file_path}: {e}")
            
        return entries

    def load_all_knowledge_entries(self) -> List[Dict]:
        """扫描所有配置的目录，加载所有XML文件中的知识"""
        all_knowledge_entries = []
        print(f"Scanning for XML files in: {self.dataset_paths}")
        
        xml_files = []
        for path in self.dataset_paths:
            if os.path.exists(path):
                for file_path in Path(path).rglob('*.xml'):
                    xml_files.append(file_path)
            else:
                print(f"Warning: Path does not exist: {path}")

        print(f"Found {len(xml_files)} XML files. Parsing...")
        
        # 使用tqdm显示解析进度
        for file_path in tqdm(xml_files, desc="Parsing XML files"):
            entries = self.parse_xml_file(file_path)
            all_knowledge_entries.extend(entries)
            
        print(f"Total knowledge entries loaded: {len(all_knowledge_entries)}")
        return all_knowledge_entries
    
    def get_text_entries(self) -> List[Dict]:
        """获取包含文本的条目（用于QA生成）"""
        all_entries = self.load_all_knowledge_entries()
        text_entries = [entry for entry in all_entries if entry['text']]
        
        print(f"Found {len(text_entries)} entries with text content")
        return text_entries
    
    def get_knowledge_entries(self) -> List[Dict]:
        """获取知识条目（用于向量化）"""
        return self.load_all_knowledge_entries()

# 测试函数
def test_data_loader():
    """测试数据加载器"""
    loader = KnowledgeDataLoader()
    
    # 测试知识条目加载
    knowledge_entries = loader.get_knowledge_entries()
    if knowledge_entries:
        print("\nSample knowledge entry:")
        print(knowledge_entries[0])
    
    # 测试文本条目加载
    text_entries = loader.get_text_entries()
    if text_entries:
        print("\nSample text entry:")
        print(text_entries[0])

if __name__ == '__main__':
    test_data_loader()