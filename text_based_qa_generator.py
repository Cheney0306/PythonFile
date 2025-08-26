# text_based_qa_generator.py - 基于文本的QA生成器

import json
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import config
from retrieval_engine import RetrievalEngine

# 导入prompt模板构建函数
import sys
sys.path.append('..')
try:
    from prompt_templates import build_prompt
except ImportError:
    print("⚠ 警告: 无法导入prompt_templates，将使用简化版本")
    def build_prompt(text, triple, schema, prompt_type):
        return f"Generate a {prompt_type} question based on: {text}"

class TextBasedQAGenerator:
    """基于文本的QA生成器 - 遍历train数据集文本，通过RAG系统生成QA对"""
    
    def __init__(self):
        self.openai_api_key = config.OPENAI_API_KEY
        self.output_dir = config.QA_OUTPUT_DIR
        self.train_dataset_path = config.DATASET_PATHS[0]  # 使用train数据集
        self.retrieval_engine = RetrievalEngine()
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # 初始化日志文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = Path(self.output_dir) / f"qa_generation_log_{timestamp}.txt"
        
        # 初始化日志文件
        self._init_log_file()
        
        # 检查OpenAI API密钥
        if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
            print("⚠ 警告: OpenAI API密钥未设置，将无法生成QA对")
    
    def _init_log_file(self):
        """初始化日志文件"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("QA生成详细日志\n")
            f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
        print(f"📝 日志文件已创建: {self.log_file}")
    
    def _log_qa_generation(self, entry_id: str, text: str, rag_result: Dict, 
                          prompt: str, qa_pair: Dict, prompt_type: str = ""):
        """记录QA生成过程到日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("🔸" + "=" * 78 + "🔸\n")
                f.write(f"📋 条目ID: {entry_id}\n")
                f.write(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if prompt_type:
                    f.write(f"🏷 问题类型: {prompt_type}\n")
                f.write("-" * 80 + "\n")
                
                f.write("📝 输入文本:\n")
                f.write(f"{text}\n")
                f.write("-" * 80 + "\n")
                
                f.write("🔍 RAG检索结果:\n")
                f.write(f"检索知识: {rag_result.get('cotkr_knowledge', 'N/A')[:300]}...\n")
                f.write(f"最终答案: {rag_result.get('final_answer', 'N/A')}\n")
                f.write(f"问题类型: {rag_result.get('retrieval_stats', {}).get('question_type', 'N/A')}\n")
                f.write("-" * 80 + "\n")
                
                f.write("💬 构建的Prompt:\n")
                f.write(f"{prompt}\n")
                f.write("-" * 80 + "\n")
                
                f.write("🤖 LLM生成的QA对:\n")
                if qa_pair:
                    f.write(f"问题: {qa_pair.get('question', 'N/A')}\n")
                    f.write(f"答案: {qa_pair.get('answer', 'N/A')}\n")
                    f.write(f"生成方法: {qa_pair.get('generation_method', 'N/A')}\n")
                else:
                    f.write("❌ QA生成失败\n")
                
                f.write("🔸" + "=" * 78 + "🔸\n\n")
                
        except Exception as e:
            print(f"⚠ 日志写入失败: {e}")
    
    def extract_texts_from_xml_files(self, target_dir: str = None) -> List[Dict]:
        """
        从train数据集的XML文件中提取所有<text>标签的文本内容
        """
        if target_dir is None:
            target_dir = self.train_dataset_path
        
        texts = []
        
        if not os.path.exists(target_dir):
            print(f"❌ 目录不存在: {target_dir}")
            return texts
        
        # 查找所有XML文件
        xml_files = list(Path(target_dir).rglob('*.xml'))
        print(f"📁 在train数据集 {target_dir} 中找到 {len(xml_files)} 个XML文件")
        
        for xml_file in tqdm(xml_files, desc="提取文本"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # 查找所有entry节点
                for entry_node in root.findall('.//entry'):
                    entry_id = entry_node.get('id', 'unknown')
                    
                    # 提取text标签内容
                    text_node = entry_node.find('text')
                    if text_node is not None and text_node.text:
                        text_content = text_node.text.strip()
                        if text_content and len(text_content) > 20:  # 过滤太短的文本
                            
                            # 同时提取三元组和schema信息（用于构建prompt）
                            triple_node = entry_node.find('triples/triple')
                            schema_node = entry_node.find('schemas/schema')
                            
                            triple = None
                            schema = None
                            
                            if triple_node is not None:
                                try:
                                    triple = (
                                        triple_node.find('sub').text,
                                        triple_node.find('rel').text,
                                        triple_node.find('obj').text
                                    )
                                except:
                                    pass
                            
                            if schema_node is not None:
                                try:
                                    schema = (
                                        schema_node.find('sub').text,
                                        schema_node.find('rel').text,
                                        schema_node.find('obj').text
                                    )
                                except:
                                    pass
                            
                            texts.append({
                                'id': entry_id,
                                'text': text_content,
                                'triple': triple,
                                'schema': schema,
                                'source_file': str(xml_file)
                            })
                            
            except ET.ParseError as e:
                print(f"⚠ 解析XML文件失败 {xml_file}: {e}")
            except Exception as e:
                print(f"⚠ 处理文件时出错 {xml_file}: {e}")
        
        print(f"✅ 成功提取 {len(texts)} 个文本片段")
        return texts
    
    def generate_qa_from_text_via_rag(self, text_item: Dict, output_filename: str = None) -> List[Dict]:
        """
        通过RAG系统处理文本，然后生成QA对
        
        流程：
        1. 对每种问题类型，将文本和类型作为查询输入RAG系统
        2. 获取RAG系统的检索和重写结果（针对特定问题类型）
        3. 使用prompt_templates构建prompt
        4. 发送给LLM生成QA对
        """
        qa_pairs = []
        
        text = text_item['text']
        entry_id = text_item['id']
        triple = text_item.get('triple')
        schema = text_item.get('schema')
        
        try:
            print(f"🔍 处理文本 (ID: {entry_id}): {text[:50]}...")
            
            # 如果有三元组和schema信息，生成四种类型的QA对
            if triple and schema and self.openai_api_key and self.openai_api_key != "your-openai-api-key-here":
                for prompt_type in ['sub', 'obj', 'rel', 'type']:
                    # 为每种问题类型单独调用RAG系统
                    rag_result = self.retrieval_engine.retrieve_and_rewrite(text, prompt_type=prompt_type)
                    
                    qa_pair = self._generate_qa_with_prompt_template(
                        text, triple, schema, prompt_type, rag_result, entry_id, output_filename
                    )
                    if qa_pair:
                        qa_pairs.append(qa_pair)
            else:
                # 如果没有三元组信息或API密钥，使用简化方法
                rag_result = self.retrieval_engine.retrieve_and_rewrite(text)
                qa_pair = self._generate_simple_qa_from_rag(text, rag_result, entry_id, output_filename)
                if qa_pair:
                    qa_pairs.append(qa_pair)
                
        except Exception as e:
            print(f"⚠ 处理文本时出错 (ID: {entry_id}): {e}")
        
        return qa_pairs
    
    def _generate_qa_with_prompt_template(self, text: str, triple: tuple, schema: tuple, 
                                         prompt_type: str, rag_result: Dict, entry_id: str, 
                                         output_filename: str = None) -> Optional[Dict]:
        """
        使用prompt_templates构建prompt，然后发送给LLM生成QA对
        """
        qa_pair = None
        prompt = ""
        
        try:
            # 1. 使用prompt_templates构建prompt
            prompt = build_prompt(text, triple, schema, prompt_type)
            
            # 2. 添加RAG系统的结果作为上下文
            rag_context = f"""
**RAG System Results:**
- Retrieved Knowledge: {rag_result['cotkr_knowledge'][:300]}...
- Final Answer: {rag_result['final_answer']}
- Question Type: {rag_result['retrieval_stats']['question_type']}

**Your Task:**
{prompt}

**Output Format:**
Please provide only:
Question: [your question]
Answer: [your answer]
"""
            
            # 3. 发送给LLM
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at generating high-quality question-answer pairs from knowledge graphs and text. Follow the instructions precisely and provide concise, accurate responses."
                    },
                    {
                        "role": "user", 
                        "content": rag_context
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            # 4. 解析响应
            content = response.choices[0].message.content.strip()
            question, answer = self._parse_qa_response(content)
            
            if question and answer:
                qa_pair = {
                    'question': question,
                    'answer': answer,
                    'question_type': prompt_type,
                    'source_text': text,
                    'triple': triple,
                    'schema': schema,
                    'entry_id': entry_id,
                    'generation_method': 'llm_with_prompt_template',
                    'rag_context': rag_result['cotkr_knowledge'][:200],
                    'rag_answer': rag_result['final_answer'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # 增量保存QA对到文件
                if output_filename:
                    self._append_qa_to_file(qa_pair, output_filename)
                    print(f"✅ QA对已保存 (类型: {prompt_type})")
            
        except Exception as e:
            print(f"⚠ LLM生成失败 (类型: {prompt_type}): {e}")
        
        # 记录到日志文件
        self._log_qa_generation(entry_id, text, rag_result, rag_context, qa_pair, prompt_type)
        
        return qa_pair
    
    def _parse_qa_response(self, response: str) -> tuple:
        """
        解析LLM响应，提取问题和答案
        """
        question = ""
        answer = ""
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Question:'):
                question = line.replace('Question:', '').strip()
            elif line.startswith('Answer:'):
                answer = line.replace('Answer:', '').strip()
        
        return question, answer
    
    def _generate_simple_qa_from_rag(self, text: str, rag_result: Dict, entry_id: str, 
                                    output_filename: str = None) -> Optional[Dict]:
        """
        当没有三元组信息时，基于RAG结果生成简单的QA对
        """
        qa_pair = None
        prompt = ""
        
        try:
            # 构建简单的prompt
            prompt = f"""
Based on the following text and RAG system analysis, generate one high-quality question-answer pair.

Original Text: "{text}"

RAG Analysis:
- Retrieved Knowledge: {rag_result['cotkr_knowledge'][:200]}...
- System Answer: {rag_result['final_answer']}

Generate a natural question about the text that can be answered using the RAG analysis.

Format:
Question: [your question]
Answer: [your answer]
"""
            
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Generate a single, high-quality question-answer pair based on the provided text and analysis."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            question, answer = self._parse_qa_response(content)
            
            if question and answer:
                qa_pair = {
                    'question': question,
                    'answer': answer,
                    'question_type': 'general',
                    'source_text': text,
                    'entry_id': entry_id,
                    'generation_method': 'llm_simple',
                    'rag_context': rag_result['cotkr_knowledge'][:200],
                    'rag_answer': rag_result['final_answer'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # 增量保存QA对到文件
                if output_filename:
                    self._append_qa_to_file(qa_pair, output_filename)
                    print(f"✅ 简单QA对已保存")
                
        except Exception as e:
            print(f"⚠ 简单QA生成失败: {e}")
        
        # 记录到日志文件
        self._log_qa_generation(entry_id, text, rag_result, prompt, qa_pair, "general")
        
        return qa_pair
    

    
    def generate_qa_dataset_from_texts(self, max_texts: int = None, output_filename: str = None) -> List[Dict]:
        """
        从train数据集的XML文件文本生成QA数据集（支持增量写入）
        
        流程：
        1. 遍历train数据集的XML文件
        2. 提取<text>标签内容
        3. 将文本通过RAG系统处理
        4. 使用prompt_templates构建prompt
        5. 发送给LLM生成QA对
        6. 每生成一个QA对就立即写入文件
        """
        print("🚀 基于train数据集文本的QA生成（增量写入模式）")
        print("🎯 流程: train文本 → RAG系统 → prompt模板 → LLM → QA对 → 立即保存")
        print("=" * 70)
        
        # 生成输出文件名
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            text_count = max_texts if max_texts else 'all'
            output_filename = f"train_text_qa_dataset_{text_count}_{timestamp}.json"
        
        print(f"📁 输出文件: {output_filename}")
        print(f"📝 日志文件: {self.log_file}")
        
        # 1. 从train数据集提取文本
        print("📚 从train数据集提取全部文本...")
        texts = self.extract_texts_from_xml_files()
        
        if not texts:
            print("❌ 没有找到文本内容")
            return []
        
        # 2. 处理数量控制
        if max_texts and len(texts) > max_texts:
            texts = texts[:max_texts]
            print(f"📊 限制处理数量为 {max_texts} 个文本（测试模式）")
        else:
            print(f"📊 处理全部 {len(texts)} 个文本")
        
        # 3. 检查RAG系统状态
        print("🔧 检查RAG系统状态...")
        try:
            system_status = self.retrieval_engine.get_system_status()
            db_count = system_status['database_status']['total_documents']
            print(f"   - 向量数据库文档数: {db_count}")
            if db_count == 0:
                print("⚠ 警告: 向量数据库为空，RAG系统可能无法正常工作")
        except Exception as e:
            print(f"⚠ 无法获取系统状态: {e}")
        
        # 4. 为每个文本生成QA对（增量写入）
        all_qa_pairs = []
        total_saved = 0
        
        print(f"🔄 开始处理 {len(texts)} 个文本...")
        print("   每个文本将通过: 文本 → RAG检索 → prompt构建 → LLM生成 → 立即保存")
        
        for i, text_item in enumerate(tqdm(texts, desc="生成QA对"), 1):
            try:
                qa_pairs = self.generate_qa_from_text_via_rag(text_item, output_filename)
                all_qa_pairs.extend(qa_pairs)
                total_saved += len(qa_pairs)
                
                # 每处理10个文本显示一次进度
                if i % 10 == 0:
                    print(f"📊 已处理 {i}/{len(texts)} 个文本，累计生成 {total_saved} 个QA对")
                    
            except Exception as e:
                print(f"⚠ 处理文本 {text_item.get('id', 'unknown')} 时出错: {e}")
                continue
        
        # 5. 完成文件写入
        self._finalize_qa_file(output_filename)
        
        print(f"✅ 生成完成，共 {len(all_qa_pairs)} 个QA对")
        print(f"💾 所有QA对已保存到: {Path(self.output_dir) / output_filename}")
        print(f"📝 详细日志已保存到: {self.log_file}")
        
        # 6. 统计信息
        method_counts = {}
        type_counts = {}
        
        for qa in all_qa_pairs:
            method = qa.get('generation_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
            
            q_type = qa.get('question_type', 'general')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        print(f"\n📊 生成方法统计:")
        for method, count in method_counts.items():
            print(f"   {method}: {count} 个")
        
        print(f"\n📊 问题类型统计:")
        for q_type, count in type_counts.items():
            print(f"   {q_type}: {count} 个")
        
        return all_qa_pairs
    
    def save_qa_dataset(self, qa_dataset: List[Dict], filename: str = "text_based_qa_dataset.json") -> str:
        """保存QA数据集到文件"""
        filepath = Path(self.output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(qa_dataset, f, ensure_ascii=False, indent=2)
        
        print(f"💾 QA数据集已保存到: {filepath}")
        return str(filepath)
    
    def _append_qa_to_file(self, qa_pair: Dict, filename: str):
        """增量追加QA对到文件"""
        filepath = Path(self.output_dir) / filename
        
        # 如果文件不存在，创建新文件并写入数组开始符号
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("[\n")
                json.dump(qa_pair, f, ensure_ascii=False, indent=2)
        else:
            # 读取现有文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 移除最后的 ] 符号，添加逗号和新的QA对
            if content.endswith(']'):
                content = content[:-1].rstrip()
                if not content.endswith('['):
                    content += ","
            
            # 写回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                if not content.endswith('['):
                    f.write("\n")
                f.write("  ")
                json.dump(qa_pair, f, ensure_ascii=False, indent=2)
                f.write("\n]")
    
    def _finalize_qa_file(self, filename: str):
        """完成QA文件的写入（确保JSON格式正确）"""
        filepath = Path(self.output_dir) / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 确保文件以 ] 结尾
            if not content.endswith(']'):
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write("\n]")

# 测试函数
def test_text_based_qa_generator():
    """测试基于文本的QA生成器"""
    print("🧪 测试改造后的基于文本的QA生成器")
    print("🎯 测试流程: train文本 → RAG系统 → prompt模板 → LLM")
    print("=" * 60)
    
    generator = TextBasedQAGenerator()
    
    # 测试文本提取
    print("1️⃣ 测试从train数据集提取文本...")
    texts = generator.extract_texts_from_xml_files()
    
    if texts:
        print(f"✅ 成功提取 {len(texts)} 个文本")
        
        # 显示示例
        sample = texts[0]
        print(f"📋 示例文本:")
        print(f"   ID: {sample['id']}")
        print(f"   文本: {sample['text'][:100]}...")
        print(f"   三元组: {sample.get('triple', 'N/A')}")
        print(f"   Schema: {sample.get('schema', 'N/A')}")
        
        # 测试QA生成
        print("\n2️⃣ 测试QA生成流程...")
        qa_pairs = generator.generate_qa_from_text_via_rag(sample)
        
        if qa_pairs:
            print(f"✅ 成功生成 {len(qa_pairs)} 个QA对")
            for i, qa in enumerate(qa_pairs, 1):
                print(f"\n{i}. 类型: {qa.get('question_type', 'N/A')}")
                print(f"   问题: {qa['question']}")
                print(f"   答案: {qa['answer']}")
                print(f"   方法: {qa.get('generation_method', 'unknown')}")
                if 'rag_answer' in qa:
                    print(f"   RAG答案: {qa['rag_answer']}")
        else:
            print("❌ QA生成失败")
            
        # 测试小规模数据集生成
        print("\n3️⃣ 测试小规模数据集生成...")
        qa_dataset = generator.generate_qa_dataset_from_texts(max_texts=2)
        
        if qa_dataset:
            print(f"✅ 数据集生成成功，共 {len(qa_dataset)} 个QA对")
        else:
            print("❌ 数据集生成失败")
            
    else:
        print("❌ 文本提取失败")

if __name__ == '__main__':
    test_text_based_qa_generator()