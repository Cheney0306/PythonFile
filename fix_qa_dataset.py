# fix_qa_dataset.py - 修复QA数据集JSON格式

import json
import re
from pathlib import Path

def fix_json_file(file_path: Path):
    """修复JSON文件格式"""
    print(f"🔧 修复文件: {file_path}")
    
    try:
        # 读取原始内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否是有效的JSON
        try:
            json.loads(content)
            print("✅ 文件格式正确，无需修复")
            return True
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON格式错误: {e}")
        
        # 尝试修复常见的JSON格式问题
        
        # 1. 处理缺少逗号的问题
        # 查找 } 后面直接跟 { 的情况，在中间添加逗号
        fixed_content = re.sub(r'}\s*\n\s*{', '},\n  {', content)
        
        # 2. 确保文件以数组格式包装
        if not fixed_content.strip().startswith('['):
            # 如果不是以数组开始，包装成数组
            fixed_content = '[\n' + fixed_content + '\n]'
        
        # 3. 处理末尾的逗号问题
        fixed_content = re.sub(r',\s*]', '\n]', fixed_content)
        
        # 4. 验证修复后的JSON
        try:
            parsed_data = json.loads(fixed_content)
            print(f"✅ 修复成功，包含 {len(parsed_data)} 个QA对")
            
            # 备份原文件
            backup_path = file_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📁 原文件已备份到: {backup_path}")
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ 自动修复失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 处理文件时出错: {e}")
        return False

def create_sample_qa_dataset():
    """创建示例QA数据集"""
    sample_qa_data = [
        {
            "question": "Who is the leader of Belgium?",
            "answer": "Philippe of Belgium",
            "question_type": "sub",
            "source_text": "Belgium's leader is King Philippe.",
            "triple": ["Belgium", "leader", "Philippe_of_Belgium"],
            "schema": ["Country", "leader", "King"],
            "entry_id": "sample_001",
            "generation_method": "manual_sample",
            "timestamp": "2025-08-27T00:00:00"
        },
        {
            "question": "Where is Amsterdam Airport Schiphol located?",
            "answer": "Netherlands",
            "question_type": "obj",
            "source_text": "Amsterdam Airport Schiphol is located in the Netherlands.",
            "triple": ["Amsterdam_Airport_Schiphol", "location", "Netherlands"],
            "schema": ["Airport", "location", "Country"],
            "entry_id": "sample_002",
            "generation_method": "manual_sample",
            "timestamp": "2025-08-27T00:00:01"
        },
        {
            "question": "What is the capital of Belgium?",
            "answer": "Brussels",
            "question_type": "obj",
            "source_text": "The capital of Belgium is Brussels.",
            "triple": ["Belgium", "capital", "Brussels"],
            "schema": ["Country", "capital", "CapitalCity"],
            "entry_id": "sample_003",
            "generation_method": "manual_sample",
            "timestamp": "2025-08-27T00:00:02"
        },
        {
            "question": "What type of entity is Belgium?",
            "answer": "Country",
            "question_type": "type",
            "source_text": "Belgium is a country in Europe.",
            "triple": ["Belgium", "type", "Country"],
            "schema": ["Country", "type", "EntityType"],
            "entry_id": "sample_004",
            "generation_method": "manual_sample",
            "timestamp": "2025-08-27T00:00:03"
        },
        {
            "question": "What is the relationship between Belgium and Brussels?",
            "answer": "capital",
            "question_type": "rel",
            "source_text": "Brussels is the capital of Belgium.",
            "triple": ["Belgium", "capital", "Brussels"],
            "schema": ["Country", "capital", "CapitalCity"],
            "entry_id": "sample_005",
            "generation_method": "manual_sample",
            "timestamp": "2025-08-27T00:00:04"
        }
    ]
    
    # 创建示例数据集文件
    qa_dir = Path("qa_datasets")
    qa_dir.mkdir(exist_ok=True)
    
    sample_file = qa_dir / "sample_qa_dataset.json"
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_qa_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建示例QA数据集: {sample_file}")
    print(f"📊 包含 {len(sample_qa_data)} 个QA对")
    
    return sample_file

def main():
    """主函数"""
    print("🔧 QA数据集修复工具")
    print("=" * 40)
    
    qa_dir = Path("qa_datasets")
    
    if not qa_dir.exists():
        print(f"📁 创建qa_datasets目录...")
        qa_dir.mkdir(exist_ok=True)
    
    # 查找所有JSON文件
    json_files = list(qa_dir.glob("*.json"))
    
    if not json_files:
        print("📂 未找到JSON文件，创建示例数据集...")
        create_sample_qa_dataset()
        return
    
    print(f"📁 找到 {len(json_files)} 个JSON文件:")
    
    fixed_count = 0
    
    for json_file in json_files:
        print(f"\n处理文件: {json_file.name}")
        
        if fix_json_file(json_file):
            fixed_count += 1
    
    print(f"\n📊 处理结果:")
    print(f"   - 总文件数: {len(json_files)}")
    print(f"   - 修复成功: {fixed_count}")
    print(f"   - 修复失败: {len(json_files) - fixed_count}")
    
    # 如果所有文件都修复失败，创建示例数据集
    if fixed_count == 0:
        print(f"\n🔄 所有文件修复失败，创建示例数据集...")
        create_sample_qa_dataset()
    
    print(f"\n✅ QA数据集修复完成！")
    print(f"💡 现在可以运行评估: python retrieval_evaluation_system.py --mode quick")

if __name__ == '__main__':
    main()