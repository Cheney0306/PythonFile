# cotkr_rewriter.py - CoTKR知识重写器

from typing import List, Dict, Tuple
import re
import config
from openai import OpenAI

class CoTKRRewriter:
    """CoTKR知识重写器 - 基于思维链的知识重写"""
    
    def __init__(self):
        # 新的四种问题类型模式
        self.question_patterns = {
            'subject': [
                'who wrote', 'who is the', 'who founded', 'who directed', 
                'who created', 'who leads', 'what wrote', 'what is the',
                'what founded', 'what created'
            ],
            'object': [
                'what did', 'where is', 'what does', 'what is the',
                'what country', 'what organization', 'what book',
                'what movie', 'what company'
            ],
            'relationship': [
                'what is the relationship', 'how is', 'how are',
                'what connects', 'what links', 'relationship between'
            ],
            'type': [
                'what type of entity', 'what kind of', 'what category',
                'what type is', 'what sort of', 'entity type'
            ]
        }
    
    def detect_question_type(self, question: str) -> str:
        """检测问题类型 - 支持四种特定类型"""
        question_lower = question.lower()
        
        # 优先检查relationship类型（因为它的模式比较特殊）
        if 'relationship' in question_lower or 'between' in question_lower:
            return 'relationship'
        
        # 检查type类型
        if 'type' in question_lower or 'kind' in question_lower or 'category' in question_lower:
            return 'type'
        
        # 按优先级检测其他问题类型
        for q_type, patterns in self.question_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                return q_type
        
        # 如果没有匹配到特定模式，使用启发式规则
        if question_lower.startswith('who '):
            return 'subject'
        elif question_lower.startswith('what did') or question_lower.startswith('where is'):
            return 'object'
        
        # 默认返回subject类型
        return 'subject'
    
    def rewrite_knowledge(self, retrieved_items: List[Dict], question: str, prompt_type: str = None) -> str:
        """
        使用CoTKR方法重写知识
        根据四种问题类型生成相应的思维链推理
        
        Args:
            retrieved_items: 检索到的项目列表
            question: 查询问题或文本
            prompt_type: 问题类型 ('sub', 'obj', 'rel', 'type')，如果提供则直接使用，不进行检测
        """
        if not retrieved_items:
            return "No relevant information found."
        
        # 确定问题类型
        if prompt_type:
            # 如果提供了prompt_type，直接使用并转换为内部格式
            type_mapping = {
                'sub': 'subject',
                'obj': 'object', 
                'rel': 'relationship',
                'type': 'type'
            }
            question_type = type_mapping.get(prompt_type, 'subject')
        else:
            # 否则检测问题类型
            question_type = self.detect_question_type(question)
        
        # 根据问题类型选择重写策略
        if question_type == 'subject':
            return self._rewrite_subject_question(retrieved_items, question)
        elif question_type == 'object':
            return self._rewrite_object_question(retrieved_items, question)
        elif question_type == 'relationship':
            return self._rewrite_relationship_question(retrieved_items, question)
        elif question_type == 'type':
            return self._rewrite_type_question(retrieved_items, question)
        else:
            # 默认使用subject处理
            return self._rewrite_subject_question(retrieved_items, question)
    
    def _rewrite_subject_question(self, items: List[Dict], question: str) -> str:
        """重写Subject类型问题 - 询问三元组的主语"""
        reasoning_steps = []
        
        reasoning_steps.append("Reason 1: This question is asking about the subject (who/what) that performs an action or has a relationship.")
        
        # 将三元组重写成自然语言句子
        natural_sentences = []
        subject_types = set()
        
        for item in items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            sub_type, rel_type, obj_type = schema
            
            # 清理名称
            sub_clean = sub.replace('_', ' ')
            obj_clean = obj.replace('_', ' ')
            rel_clean = rel.replace('_', ' ')
            
            # 将三元组重写成自然语言句子
            sentence = self._triple_to_sentence(sub_clean, rel_clean, obj_clean, sub_type, obj_type)
            natural_sentences.append(sentence)
            subject_types.add(sub_type)
        
        if natural_sentences:
            reasoning_steps.append(f"Knowledge 1: From the knowledge base: {' '.join(natural_sentences[:3])}")
        
        # 添加类型信息
        if subject_types:
            reasoning_steps.append("Reason 2: I should identify the type of entity that could be the subject.")
            reasoning_steps.append(f"Knowledge 2: The subject entities are of types: {', '.join(subject_types)}.")
        
        reasoning_steps.append("Reason 3: Based on the question pattern and retrieved knowledge, I can identify the subject entity.")
        
        return '\n'.join(reasoning_steps)
    
    def _rewrite_object_question(self, items: List[Dict], question: str) -> str:
        """重写Object类型问题 - 询问三元组的宾语"""
        reasoning_steps = []
        
        reasoning_steps.append("Reason 1: This question is asking about the object (what/who) that receives an action or is in a relationship.")
        
        # 将三元组重写成自然语言句子
        natural_sentences = []
        object_types = set()
        
        for item in items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            sub_type, rel_type, obj_type = schema
            
            # 清理名称
            sub_clean = sub.replace('_', ' ')
            obj_clean = obj.replace('_', ' ')
            rel_clean = rel.replace('_', ' ')
            
            # 将三元组重写成自然语言句子
            sentence = self._triple_to_sentence(sub_clean, rel_clean, obj_clean, sub_type, obj_type)
            natural_sentences.append(sentence)
            object_types.add(obj_type)
        
        if natural_sentences:
            reasoning_steps.append(f"Knowledge 1: From the knowledge base: {' '.join(natural_sentences[:3])}")
        
        # 添加类型信息
        if object_types:
            reasoning_steps.append("Reason 2: I should identify the type of entity that could be the object.")
            reasoning_steps.append(f"Knowledge 2: The object entities are of types: {', '.join(object_types)}.")
        
        reasoning_steps.append("Reason 3: Based on the question pattern and retrieved knowledge, I can identify the object entity.")
        
        return '\n'.join(reasoning_steps)
    
    def _rewrite_relationship_question(self, items: List[Dict], question: str) -> str:
        """重写Relationship类型问题 - 询问三元组的关系"""
        reasoning_steps = []
        
        reasoning_steps.append("Reason 1: This question is asking about the relationship or connection between two entities.")
        
        # 将三元组重写成自然语言句子，重点关注关系
        natural_sentences = []
        relationship_types = set()
        
        for item in items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            sub_type, rel_type, obj_type = schema
            
            # 清理名称
            sub_clean = sub.replace('_', ' ')
            obj_clean = obj.replace('_', ' ')
            rel_clean = rel.replace('_', ' ')
            
            # 将三元组重写成自然语言句子
            sentence = self._triple_to_sentence(sub_clean, rel_clean, obj_clean, sub_type, obj_type)
            natural_sentences.append(sentence)
            relationship_types.add(rel_type)
        
        if natural_sentences:
            reasoning_steps.append(f"Knowledge 1: From the knowledge base: {' '.join(natural_sentences[:3])}")
        
        # 添加关系类型信息
        if relationship_types:
            reasoning_steps.append("Reason 2: I should consider the types of relationships involved.")
            reasoning_steps.append(f"Knowledge 2: The relationship types include: {', '.join(relationship_types)}.")
        
        reasoning_steps.append("Reason 3: Based on the question and retrieved knowledge, I can identify the specific relationship.")
        
        return '\n'.join(reasoning_steps)
    
    def _rewrite_type_question(self, items: List[Dict], question: str) -> str:
        """重写Type类型问题 - 询问实体的类型"""
        reasoning_steps = []
        
        reasoning_steps.append("Reason 1: This question is asking about the type or category of an entity.")
        
        # 将三元组重写成自然语言句子，并提取类型信息
        natural_sentences = []
        entity_type_info = []
        all_types = set()
        
        for item in items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            sub_type, rel_type, obj_type = schema
            
            # 清理名称
            sub_clean = sub.replace('_', ' ')
            obj_clean = obj.replace('_', ' ')
            rel_clean = rel.replace('_', ' ')
            
            # 将三元组重写成自然语言句子
            sentence = self._triple_to_sentence(sub_clean, rel_clean, obj_clean, sub_type, obj_type)
            natural_sentences.append(sentence)
            
            # 构建类型相关的知识
            entity_type_info.append(f"{sub_clean} is of type {sub_type}")
            entity_type_info.append(f"{obj_clean} is of type {obj_type}")
            all_types.add(sub_type)
            all_types.add(obj_type)
        
        if natural_sentences:
            reasoning_steps.append(f"Knowledge 1: From the knowledge base: {' '.join(natural_sentences[:2])}")
        
        if entity_type_info:
            # 只显示前几个，避免重复
            unique_type_info = list(set(entity_type_info))[:4]
            reasoning_steps.append(f"Knowledge 2: Entity types: {'. '.join(unique_type_info)}.")
        
        # 添加类型总结
        if all_types:
            reasoning_steps.append("Reason 2: I should identify the specific entity type being asked about.")
            reasoning_steps.append(f"Knowledge 3: The available entity types are: {', '.join(all_types)}.")
        
        reasoning_steps.append("Reason 3: Based on the question context, I can determine which entity type is being requested.")
        
        return '\n'.join(reasoning_steps)
    
    def _triple_to_sentence(self, subject: str, relation: str, object_val: str, 
                           subject_type: str = "", object_type: str = "") -> str:
        """将三元组转换为自然语言句子"""
        
        # 关系词映射到自然语言
        relation_mappings = {
            'runwayLength': 'has a runway length of',
            'runwayName': 'has a runway named',
            'location': 'is located in',
            'leader': 'is led by',
            'capital': 'has the capital',
            'population': 'has a population of',
            'area': 'has an area of',
            'founded': 'was founded in',
            'wrote': 'wrote',
            'directed': 'directed',
            'created': 'created',
            'owns': 'owns',
            'memberOf': 'is a member of',
            'partOf': 'is part of',
            'hasType': 'is of type',
            'jurisdiction': 'has jurisdiction over'
        }
        
        # 获取自然语言关系描述
        natural_relation = relation_mappings.get(relation, f"has the relation '{relation}' with")
        
        # 根据对象类型调整句子结构
        if object_type.lower() in ['number', 'integer', 'float']:
            # 数值类型，可能需要单位
            if 'length' in relation.lower() or 'distance' in relation.lower():
                sentence = f"{subject} {natural_relation} {object_val} meters."
            elif 'population' in relation.lower():
                sentence = f"{subject} {natural_relation} {object_val} people."
            elif 'area' in relation.lower():
                sentence = f"{subject} {natural_relation} {object_val} square kilometers."
            else:
                sentence = f"{subject} {natural_relation} {object_val}."
        else:
            # 实体类型
            sentence = f"{subject} {natural_relation} {object_val}."
        
        return sentence
    
    def extract_answer_from_knowledge(self, question: str, cotkr_knowledge: str, retrieved_items: List[Dict], prompt_type: str = None) -> str:
        """
        从CoTKR知识中提取答案 - 【新方法】使用LLM进行最终答案的生成
        
        Args:
            question: 查询问题或文本
            cotkr_knowledge: CoTKR重写的知识
            retrieved_items: 检索到的项目列表
            prompt_type: 问题类型 ('sub', 'obj', 'rel', 'type')，如果提供则直接使用，不进行检测
        """
        if not retrieved_items:
            return "Information not available in the knowledge base."
        
        # 1. 构建一个新的、清晰的Prompt，要求LLM根据生成的"思维链"来回答问题
        prompt = f"""You are an intelligent assistant. Your task is to provide a direct and concise answer to the user's question based *only* on the provided "Reasoning Steps".

User's Question:
"{question}"

Reasoning Steps:
---
{cotkr_knowledge}
---

Based on the reasoning steps above, what is the final answer to the question?
Provide only the answer itself, without any extra explanation.

Final Answer:"""

        # 2. 调用LLM来生成答案
        try:
            if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your-openai-api-key-here":
                print("⚠️ OpenAI API key not set. Falling back to simple extraction.")
                # 如果没有API密钥，回退到简单的规则式提取
                return self._fallback_extraction(question, retrieved_items, prompt_type)
            
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that provides a final, concise answer based on the reasoning context provided."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.0,  # 使用0温度，让答案更具确定性
                max_tokens=60     # 答案通常很短，不需要太多token
            )
            
            final_answer = response.choices[0].message.content.strip()
            return final_answer
            
        except Exception as e:
            print(f"❌ LLM-based answer extraction failed: {e}")
            # 如果API调用失败，回退到简单的规则式提取
            return self._fallback_extraction(question, retrieved_items, prompt_type)
    
    def _fallback_extraction(self, question: str, retrieved_items: List[Dict], prompt_type: str = None) -> str:
        """回退方案：简单的规则式答案提取"""
        # 确定问题类型
        if prompt_type:
            type_mapping = {
                'sub': 'subject',
                'obj': 'object', 
                'rel': 'relationship',
                'type': 'type'
            }
            question_type = type_mapping.get(prompt_type, 'subject')
        else:
            question_type = self.detect_question_type(question)
        
        question_lower = question.lower()
        
        # 简化的答案提取逻辑
        if question_type == 'subject':
            return self._extract_subject_answer(question_lower, retrieved_items)
        elif question_type == 'object':
            return self._extract_object_answer(question_lower, retrieved_items)
        elif question_type == 'relationship':
            return self._extract_relationship_answer(question_lower, retrieved_items)
        elif question_type == 'type':
            return self._extract_type_answer(question_lower, retrieved_items)
        
        return "Information not available in the knowledge base."
    
    def _extract_subject_answer(self, question_lower: str, retrieved_items: List[Dict]) -> str:
        """提取Subject类型问题的答案"""
        # 寻找包含leader/president/king等关系的三元组
        leadership_relations = ['leader', 'president', 'king', 'queen', 'prime_minister', 'head_of_state', 'ruler']
        
        for item in retrieved_items:
            triple = item['triple']
            sub, rel, obj = triple
            
            # 如果关系是领导类型，返回宾语（领导者）
            if any(leadership in rel.lower() for leadership in leadership_relations):
                return obj.replace('_', ' ')
        
        # 如果没找到领导关系，寻找问题中提到的实体作为主语的三元组
        for item in retrieved_items:
            triple = item['triple']
            sub, rel, obj = triple
            
            # 检查问题中是否提到了主语实体
            if any(entity in question_lower for entity in [sub.lower(), sub.replace('_', ' ').lower()]):
                # 根据关系类型决定返回什么
                if 'leader' in rel.lower() or 'president' in rel.lower() or 'king' in rel.lower():
                    return obj.replace('_', ' ')
        
        # 默认返回第一个三元组的主语
        if retrieved_items:
            return retrieved_items[0]['triple'][0].replace('_', ' ')
        
        return "Information not available."
    
    def _extract_object_answer(self, question_lower: str, retrieved_items: List[Dict]) -> str:
        """提取Object类型问题的答案"""
        # 位置相关的关系
        location_relations = ['location', 'located_in', 'country', 'city', 'region', 'place']
        
        # 如果问题询问位置
        if any(word in question_lower for word in ['where', 'location', 'located', 'place']):
            for item in retrieved_items:
                triple = item['triple']
                sub, rel, obj = triple
                
                # 寻找位置相关的关系
                if any(loc_rel in rel.lower() for loc_rel in location_relations):
                    return obj.replace('_', ' ')
        
        # 如果问题询问其他属性
        for item in retrieved_items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            sub_type, rel_type, obj_type = schema
            
            # 检查问题中是否提到了主语实体
            if any(entity in question_lower for entity in [sub.lower(), sub.replace('_', ' ').lower()]):
                # 根据问题内容和关系类型返回合适的宾语
                if 'where' in question_lower and any(loc_rel in rel.lower() for loc_rel in location_relations):
                    return obj.replace('_', ' ')
                elif 'what' in question_lower and obj_type.lower() not in ['runway', 'runwaysurfacetype']:
                    return obj.replace('_', ' ')
        
        # 默认返回第一个非跑道相关的宾语
        for item in retrieved_items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            obj_type = schema[2]
            
            if obj_type.lower() not in ['runway', 'runwaysurfacetype', 'runwayname']:
                return obj.replace('_', ' ')
        
        # 最后默认返回第一个宾语
        if retrieved_items:
            return retrieved_items[0]['triple'][2].replace('_', ' ')
        
        return "Information not available."
    
    def _extract_relationship_answer(self, question_lower: str, retrieved_items: List[Dict]) -> str:
        """提取Relationship类型问题的答案"""
        # 直接返回关系，但优先选择最相关的
        for item in retrieved_items:
            triple = item['triple']
            sub, rel, obj = triple
            
            # 检查问题中是否同时提到了主语和宾语
            sub_mentioned = any(entity in question_lower for entity in [sub.lower(), sub.replace('_', ' ').lower()])
            obj_mentioned = any(entity in question_lower for entity in [obj.lower(), obj.replace('_', ' ').lower()])
            
            if sub_mentioned and obj_mentioned:
                return rel.replace('_', ' ')
        
        # 默认返回第一个关系
        if retrieved_items:
            return retrieved_items[0]['triple'][1].replace('_', ' ')
        
        return "Information not available."
    
    def _extract_type_answer(self, question_lower: str, retrieved_items: List[Dict]) -> str:
        """提取Type类型问题的答案"""
        for item in retrieved_items:
            triple = item['triple']
            schema = item['schema']
            sub, rel, obj = triple
            sub_type, rel_type, obj_type = schema
            
            # 检查问题中提到的实体
            if any(entity in question_lower for entity in [sub.lower(), sub.replace('_', ' ').lower()]):
                return sub_type
            elif any(entity in question_lower for entity in [obj.lower(), obj.replace('_', ' ').lower()]):
                return obj_type
        
        # 默认返回主语类型
        if retrieved_items:
            return retrieved_items[0]['schema'][0]
        
        return "Information not available."

# 测试函数
def test_cotkr_rewriter():
    """测试CoTKR重写器 - 四种问题类型"""
    rewriter = CoTKRRewriter()
    
    # 模拟检索结果
    mock_items = [
        {
            'triple': ('John_Doe', 'wrote', 'A_Fistful_of_Dollars'),
            'schema': ('Person', 'wrote', 'Movie'),
            'distance': 0.25
        },
        {
            'triple': ('Belgium', 'leader', 'Philippe_of_Belgium'),
            'schema': ('Country', 'leader', 'Royalty'),
            'distance': 0.31
        }
    ]
    
    # 四种类型的测试问题
    test_questions = [
        ("Who wrote A Fistful of Dollars?", "subject"),
        ("What did John Doe write?", "object"),
        ("What is the relationship between John Doe and A Fistful of Dollars?", "relationship"),
        ("What type of entity is John Doe?", "type")
    ]
    
    print("🧠 测试CoTKR重写器 - 四种问题类型")
    print("=" * 60)
    
    for question, expected_type in test_questions:
        print(f"\n问题: {question}")
        detected_type = rewriter.detect_question_type(question)
        print(f"检测类型: {detected_type} (预期: {expected_type})")
        
        rewritten = rewriter.rewrite_knowledge(mock_items, question)
        print(f"CoTKR重写:")
        for line in rewritten.split('\n')[:3]:  # 只显示前3行
            if line.strip():
                print(f"  {line}")
        
        answer = rewriter.extract_answer_from_knowledge(question, rewritten, mock_items)
        print(f"提取答案: {answer}")
        print("-" * 40)

if __name__ == '__main__':
    test_cotkr_rewriter()