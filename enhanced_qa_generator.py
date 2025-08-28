# enhanced_qa_generator.py - 增强的QA生成器

import json
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import config
from enhanced_retrieval_engine import EnhancedRetrievalEngine
import random

class EnhancedQAGenerator:
    """增强的QA生成器 - 使用增强检索系统，跳过重写模块，直接用三元组生成QA对"""
    
    def __init__(self):
        self.openai_api_key = config.OPENAI_API_KEY
        self.output_dir = config.QA_OUTPUT_DIR
        self.train_dataset_path = config.DATASET_PATHS[0]
        self.retrieval_engine = EnhancedRetrievalEngine()
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # 初始化日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = Path(self.output_dir) / f"enhanced_qa_generation_log_{timestamp}.txt"
        self._init_log_file()
        
        # 检查OpenAI API密钥
        if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
            print("⚠ 警告: OpenAI API密钥未设置，将无法生成QA对")
            
        # 问题类型定义
        self.question_types = ['sub', 'obj', 'rel', 'type']
    
    def _init_log_file(self):
        """初始化日志文件"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("增强QA生成详细日志\n")
            f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
        print(f"📝 日志文件已创建: {self.log_file}")
    
    def _get_one_shot_example(self, question_type: str) -> str:
        """根据问题类型获取One-shot示例"""
        examples = {
            'rel': """**Example:**
- Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
- Question: What is the relationship between Amsterdam Airport Schiphol and Haarlemmermeer?
- Answer: location""",
            
            'sub': """**Example:**
- Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)  
- Question: What is located in Haarlemmermeer?
- Answer: Amsterdam Airport Schiphol""",
            
            'obj': """**Example:**
- Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
- Question: Where is Amsterdam Airport Schiphol located?
- Answer: Haarlemmermeer""",
            
            'type': """**Example:**
- Triple: (Amsterdam Airport Schiphol, location, Haarlemmermeer)
- Schema: (Airport, location, City)
- Question: What is Amsterdam Airport Schiphol?
- Answer: Airport"""
        }
        
        return examples.get(question_type, examples['obj'])  # 默认使用obj示例
    
    def _construct_enhanced_prompt(self, triple: Tuple, schema: Tuple, question_type: str, source_text: str) -> str:
        """构造增强的prompt，包含One-shot示例"""
        
        one_shot_example = self._get_one_shot_example(question_type)
        
        # 根据问题类型构造不同的prompt
        if question_type == 'rel':
            task_instruction = f"""Generate a question asking about the relationship between the subject and object in the triple.
The answer should be the predicate/relation."""
        elif question_type == 'sub':
            task_instruction = f"""Generate a question asking about what entity has the given relationship with the object.
The answer should be the subject."""
        elif question_type == 'obj':
            task_instruction = f"""Generate a question asking about what the subject is related to through the given relationship.
The answer should be the object."""
        elif question_type == 'type':
            task_instruction = f"""Generate a question asking about what type/category the subject entity belongs to.
The answer should be the subject's type from the schema."""
        else:
            task_instruction = "Generate a relevant question and answer based on the triple."
        
        # 构造完整prompt
        if question_type == 'type' and schema:
            prompt = f"""You are an expert at generating high-quality question-answer pairs from knowledge graph triples.

{one_shot_example}

**Your Task:**
{task_instruction}

**Given Information:**
- Triple: {triple}
- Schema: {schema}
- Source Text: {source_text[:200]}...

**Instructions:**
1. Generate a natural, clear question based on the triple and schema
2. Provide a concise, accurate answer
3. Follow the example format above
4. Make the question sound natural and conversational

**Output Format:**
Question: [your question]
Answer: [your answer]"""
        else:
            prompt = f"""You are an expert at generating high-quality question-answer pairs from knowledge graph triples.

{one_shot_example}

**Your Task:**
{task_instruction}

**Given Information:**
- Triple: {triple}
- Source Text: {source_text[:200]}...

**Instructions:**
1. Generate a natural, clear question based on the triple
2. Provide a concise, accurate answer  
3. Follow the example format above
4. Make the question sound natural and conversational

**Output Format:**
Question: [your question]
Answer: [your answer]"""
        
        return prompt
    
    def _call_llm_for_qa_generation(self, prompt: str) -> Optional[Dict[str, str]]:
        """调用LLM生成QA对"""
        try:
            # 检查API密钥
            if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
                print("⚠ OpenAI API密钥未设置，使用模拟QA生成")
                return self._generate_mock_qa_response(prompt)
            
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at generating high-quality question-answer pairs from knowledge graphs. Follow the instructions precisely and provide concise, accurate responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_qa_response(content)
            
        except Exception as e:
            print(f"⚠ LLM调用失败: {e}")
            return self._generate_mock_qa_response(prompt)
    
    def _generate_mock_qa_response(self, prompt: str) -> Optional[Dict[str, str]]:
        """生成模拟QA响应（用于测试）"""
        try:
            # 从prompt中提取三元组信息
            if "Triple: (" in prompt:
                triple_start = prompt.find("Triple: (") + 9
                triple_end = prompt.find(")", triple_start)
                triple_str = prompt[triple_start:triple_end]
                parts = [p.strip() for p in triple_str.split(",")]
                
                if len(parts) >= 3:
                    sub, rel, obj = parts[0], parts[1], parts[2]
                    
                    # 根据问题类型生成模拟QA
                    if "relationship between" in prompt:
                        return {
                            'question': f"What is the relationship between {sub} and {obj}?",
                            'answer': rel
                        }
                    elif "What is located" in prompt or "asking about what entity has" in prompt:
                        return {
                            'question': f"What has {rel} relationship with {obj}?",
                            'answer': sub
                        }
                    elif "Where is" in prompt or "asking about what the subject is related to" in prompt:
                        return {
                            'question': f"What is {sub} {rel} to?",
                            'answer': obj
                        }
                    elif "What is" in prompt and "type" in prompt:
                        # 从schema中提取类型
                        if "Schema: (" in prompt:
                            schema_start = prompt.find("Schema: (") + 9
                            schema_end = prompt.find(")", schema_start)
                            schema_str = prompt[schema_start:schema_end]
                            schema_parts = [p.strip() for p in schema_str.split(",")]
                            if schema_parts:
                                return {
                                    'question': f"What type of entity is {sub}?",
                                    'answer': schema_parts[0]
                                }
                        return {
                            'question': f"What is {sub}?",
                            'answer': "Entity"
                        }
            
            return {
                'question': "What is the main topic?",
                'answer': "Knowledge graph entity"
            }
            
        except Exception as e:
            print(f"⚠ 模拟QA生成失败: {e}")
            return None
    
    def _parse_qa_response(self, content: str) -> Optional[Dict[str, str]]:
        """解析LLM响应，提取问题和答案"""
        try:
            lines = content.strip().split('\n')
            question = None
            answer = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Question:'):
                    question = line.replace('Question:', '').strip()
                elif line.startswith('Answer:'):
                    answer = line.replace('Answer:', '').strip()
            
            if question and answer:
                return {'question': question, 'answer': answer}
            else:
                print(f"⚠ 无法解析QA响应: {content}")
                return None
                
        except Exception as e:
            print(f"⚠ 解析QA响应失败: {e}")
            return None
    
    def _enhanced_retrieve_for_qa(self, text: str) -> List[Dict]:
        """使用增强检索系统获取相关三元组，跳过重写步骤"""
        try:
            # 使用增强系统的多阶段检索功能
            retrieved_items = self.retrieval_engine.db_manager.multi_stage_retrieval(
                query=text, 
                n_results=5,  # 最终返回5个结果
                rerank_top_k=15  # 第一阶段检索15个，然后重排
            )
            
            # 转换为标准格式
            enhanced_results = []
            for item in retrieved_items:
                enhanced_results.append({
                    'triple': item['triple'],
                    'schema': item.get('schema', None),
                    'distance': item['distance'],
                    'metadata': item.get('metadata', {}),
                    'document': item.get('document', ''),
                    'rerank_score': item.get('rerank_score', 0),
                    'detailed_scores': item.get('detailed_scores', {})
                })
            
            return enhanced_results
            
        except Exception as e:
            print(f"⚠ 增强检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _generate_qa_from_text(self, text: str, entry_id: str) -> List[Dict]:
        """从文本生成QA对的主要方法"""
        qa_pairs = []
        
        try:
            # 1. 使用增强检索获取相关三元组（跳过重写）
            retrieved_results = self._enhanced_retrieve_for_qa(text)
            
            if not retrieved_results:
                print(f"⚠ 文本 {entry_id} 没有检索到相关三元组")
                return qa_pairs
            
            # 2. 为每个检索到的三元组生成不同类型的QA对
            for i, result in enumerate(retrieved_results[:3]):  # 限制前3个结果
                triple = result['triple']
                schema = result.get('schema')
                
                # 随机选择1-2个问题类型进行生成
                selected_types = random.sample(self.question_types, k=random.randint(1, 2))
                
                for question_type in selected_types:
                    try:
                        # 3. 构造增强prompt（包含One-shot示例）
                        prompt = self._construct_enhanced_prompt(triple, schema, question_type, text)
                        
                        # 4. 调用LLM生成QA对
                        qa_result = self._call_llm_for_qa_generation(prompt)
                        
                        if qa_result:
                            qa_pair = {
                                'question': qa_result['question'],
                                'answer': qa_result['answer'],
                                'question_type': question_type,
                                'source_text': text,
                                'triple': triple,
                                'schema': schema,
                                'entry_id': entry_id,
                                'generation_method': 'enhanced_retrieval_with_oneshot',
                                'retrieval_distance': result['distance'],
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            qa_pairs.append(qa_pair)
                            
                            # 记录到日志
                            self._log_qa_generation(entry_id, text, result, prompt, qa_pair, question_type)
                            
                    except Exception as e:
                        print(f"⚠ 生成QA对失败 (类型: {question_type}): {e}")
                        continue
            
            return qa_pairs
            
        except Exception as e:
            print(f"⚠ 处理文本时出错 (ID: {entry_id}): {e}")
            return qa_pairs
    
    def _log_qa_generation(self, entry_id: str, text: str, retrieval_result: Dict, 
                          prompt: str, qa_pair: Dict, question_type: str):
        """记录QA生成过程到日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("🔸" + "=" * 78 + "🔸\n")
                f.write(f"📋 条目ID: {entry_id}\n")
                f.write(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"🏷 问题类型: {question_type}\n")
                f.write("-" * 80 + "\n")
                
                f.write("📝 输入文本:\n")
                f.write(f"{text[:300]}...\n")
                f.write("-" * 80 + "\n")
                
                f.write("🔍 检索结果:\n")
                f.write(f"三元组: {retrieval_result['triple']}\n")
                f.write(f"Schema: {retrieval_result.get('schema', 'N/A')}\n")
                f.write(f"距离: {retrieval_result['distance']:.4f}\n")
                f.write("-" * 80 + "\n")
                
                f.write("💬 构建的Prompt:\n")
                f.write(f"{prompt[:500]}...\n")
                f.write("-" * 80 + "\n")
                
                f.write("✅ 生成的QA对:\n")
                f.write(f"问题: {qa_pair['question']}\n")
                f.write(f"答案: {qa_pair['answer']}\n")
                f.write("🔸" + "=" * 78 + "🔸\n\n")
                
        except Exception as e:
            print(f"⚠ 日志记录失败: {e}")
    
    def generate_qa_dataset_from_texts(self, max_texts: int = None, output_filename: str = None) -> List[Dict]:
        """从train数据集文本生成QA数据集"""
        
        print(f"🚀 开始增强QA生成流程")
        print(f"📊 流程: Text → 增强检索 → 重排 → 跳过重写 → One-shot Prompt → LLM → QA对")
        
        # 获取所有XML文件
        xml_files = list(Path(self.train_dataset_path).glob("*.xml"))
        
        if not xml_files:
            print(f"❌ 在 {self.train_dataset_path} 中未找到XML文件")
            return []
        
        # 限制处理数量
        if max_texts:
            xml_files = xml_files[:max_texts]
        
        print(f"📁 找到 {len(xml_files)} 个XML文件")
        
        all_qa_pairs = []
        output_path = Path(self.output_dir) / (output_filename or "enhanced_qa_dataset.json")
        
        # 增量保存模式
        processed_count = 0
        
        for xml_file in tqdm(xml_files, desc="处理XML文件"):
            try:
                # 解析XML文件
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # 提取文本内容
                text_elements = root.findall('.//text')
                
                for text_elem in text_elements:
                    text_content = text_elem.text
                    if text_content and len(text_content.strip()) > 50:
                        
                        entry_id = f"{xml_file.stem}_{len(all_qa_pairs)}"
                        
                        # 生成QA对
                        qa_pairs = self._generate_qa_from_text(text_content.strip(), entry_id)
                        
                        if qa_pairs:
                            all_qa_pairs.extend(qa_pairs)
                            
                            # 每处理10个文本保存一次
                            if len(all_qa_pairs) % 10 == 0:
                                with open(output_path, 'w', encoding='utf-8') as f:
                                    json.dump(all_qa_pairs, f, ensure_ascii=False, indent=2)
                                print(f"💾 已保存 {len(all_qa_pairs)} 个QA对到 {output_path}")
                
                processed_count += 1
                
            except Exception as e:
                print(f"⚠ 处理文件 {xml_file} 时出错: {e}")
                continue
        
        # 最终保存
        if all_qa_pairs:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_qa_pairs, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 增强QA数据集生成完成！")
            print(f"📊 总计: {len(all_qa_pairs)} 个QA对")
            print(f"📁 保存位置: {output_path}")
            print(f"📝 日志文件: {self.log_file}")
        
        return all_qa_pairs