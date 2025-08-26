# visualize_qa_flowchart.py - 问答系统流程图可视化

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def create_qa_system_flowchart():
    """创建问答系统主流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 定义颜色
    colors = {
        'input': '#E3F2FD',      # 浅蓝色 - 输入
        'process': '#FFF3E0',    # 浅橙色 - 处理
        'decision': '#F3E5F5',   # 浅紫色 - 决策
        'output': '#C8E6C9',     # 浅绿色 - 输出
        'storage': '#FFEBEE'     # 浅红色 - 存储
    }
    
    # 流程步骤
    steps = [
        # (x, y, width, height, text, color_key)
        (1, 10.5, 2, 0.8, '用户输入问题', 'input'),
        (1, 9.2, 2, 0.8, '问题向量化\n(BAAI/bge-m3)', 'process'),
        (1, 7.9, 2, 0.8, '向量数据库检索\n(ChromaDB)', 'process'),
        (1, 6.6, 2, 0.8, '获取Top-K\n相关文档', 'storage'),
        
        (4.5, 8.5, 2, 0.8, '问题类型检测', 'decision'),
        
        (4.5, 6.8, 1.8, 0.6, 'Subject\n重写', 'process'),
        (6.5, 6.8, 1.8, 0.6, 'Object\n重写', 'process'),
        (4.5, 5.8, 1.8, 0.6, 'Relation\n重写', 'process'),
        (6.5, 5.8, 1.8, 0.6, 'Type\n重写', 'process'),
        
        (7.5, 4.2, 2, 0.8, 'CoTKR\n思维链推理', 'decision'),
        (7.5, 2.9, 2, 0.8, '答案提取', 'process'),
        (7.5, 1.6, 2, 0.8, '返回最终答案', 'output'),
    ]
    
    # 绘制流程框
    boxes = []
    for x, y, w, h, text, color_key in steps:
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=colors[color_key],
            edgecolor='black',
            linewidth=1
        )
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                fontsize=9, weight='bold')
        boxes.append((x + w/2, y + h/2))
    
    # 绘制连接线
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # 主流程
        (4, 5), (4, 6), (4, 7), (4, 8),  # 分支到四种类型
        (5, 9), (6, 9), (7, 9), (8, 9),  # 汇聚到CoTKR
        (9, 10), (10, 11)  # 最终输出
    ]
    
    for start, end in connections:
        x1, y1 = boxes[start]
        x2, y2 = boxes[end]
        
        if start == 4:  # 从问题类型检测分支
            # 绘制分支箭头
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
        elif end == 9:  # 汇聚到CoTKR
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='green'))
        else:
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # 添加标题
    ax.text(5, 11.5, 'KG-RAG 问答系统完整流程', ha='center', va='center', 
            fontsize=16, weight='bold')
    
    # 添加图例
    legend_elements = [
        patches.Patch(color=colors['input'], label='输入层'),
        patches.Patch(color=colors['process'], label='处理层'),
        patches.Patch(color=colors['decision'], label='决策层'),
        patches.Patch(color=colors['storage'], label='存储层'),
        patches.Patch(color=colors['output'], label='输出层')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.tight_layout()
    plt.savefig('qa_system_main_flow.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_cotkr_detail_flowchart():
    """创建CoTKR重写详细流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定义颜色
    colors = {
        'subject': '#E3F2FD',    # 浅蓝色
        'object': '#FFF3E0',     # 浅橙色
        'relation': '#F3E5F5',   # 浅紫色
        'type': '#E0F2F1',       # 浅青色
        'common': '#FFEBEE'      # 浅红色
    }
    
    # CoTKR重写步骤
    ax.text(8, 9.5, 'CoTKR 四种问题类型重写策略', ha='center', va='center', 
            fontsize=16, weight='bold')
    
    # Subject类型重写
    subject_steps = [
        (1, 8, 2.5, 0.6, 'Subject问题\n"Who is the leader?"'),
        (1, 7, 2.5, 0.6, 'Reason 1:\n询问执行动作的主语'),
        (1, 6, 2.5, 0.6, 'Knowledge 1:\n三元组自然语言化'),
        (1, 5, 2.5, 0.6, 'Reason 2:\n识别主语实体类型'),
        (1, 4, 2.5, 0.6, 'Knowledge 2:\n主语类型信息'),
        (1, 3, 2.5, 0.6, 'Reason 3:\n基于模式识别主语'),
    ]
    
    # Object类型重写
    object_steps = [
        (4.5, 8, 2.5, 0.6, 'Object问题\n"Where is located?"'),
        (4.5, 7, 2.5, 0.6, 'Reason 1:\n询问接受动作的宾语'),
        (4.5, 6, 2.5, 0.6, 'Knowledge 1:\n三元组自然语言化'),
        (4.5, 5, 2.5, 0.6, 'Reason 2:\n识别宾语实体类型'),
        (4.5, 4, 2.5, 0.6, 'Knowledge 2:\n宾语类型信息'),
        (4.5, 3, 2.5, 0.6, 'Reason 3:\n基于模式识别宾语'),
    ]
    
    # Relation类型重写
    relation_steps = [
        (8, 8, 2.5, 0.6, 'Relation问题\n"What relationship?"'),
        (8, 7, 2.5, 0.6, 'Reason 1:\n询问实体间关系'),
        (8, 6, 2.5, 0.6, 'Knowledge 1:\n三元组自然语言化'),
        (8, 5, 2.5, 0.6, 'Reason 2:\n考虑关系类型'),
        (8, 4, 2.5, 0.6, 'Knowledge 2:\n关系类型信息'),
        (8, 3, 2.5, 0.6, 'Reason 3:\n识别具体关系'),
    ]
    
    # Type类型重写
    type_steps = [
        (11.5, 8, 2.5, 0.6, 'Type问题\n"What type of entity?"'),
        (11.5, 7, 2.5, 0.6, 'Reason 1:\n询问实体类型'),
        (11.5, 6, 2.5, 0.6, 'Knowledge 1:\n三元组自然语言化'),
        (11.5, 5, 2.5, 0.6, 'Knowledge 2:\n实体类型映射'),
        (11.5, 4, 2.5, 0.6, 'Reason 2:\n识别被询问实体'),
        (11.5, 3, 2.5, 0.6, 'Reason 3:\n确定实体类型'),
    ]
    
    # 绘制所有步骤
    all_steps = [
        (subject_steps, 'subject'),
        (object_steps, 'object'),
        (relation_steps, 'relation'),
        (type_steps, 'type')
    ]
    
    for steps, color_key in all_steps:
        for i, (x, y, w, h, text) in enumerate(steps):
            box = FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.05",
                facecolor=colors[color_key],
                edgecolor='black',
                linewidth=1
            )
            ax.add_patch(box)
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                    fontsize=8, weight='bold')
            
            # 绘制连接线
            if i < len(steps) - 1:
                next_x, next_y, _, _, _ = steps[i + 1]
                ax.annotate('', xy=(x + w/2, next_y + h), xytext=(x + w/2, y),
                           arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    # 汇聚到最终输出
    final_box = FancyBboxPatch(
        (6.5, 1.5), 3, 0.8,
        boxstyle="round,pad=0.1",
        facecolor=colors['common'],
        edgecolor='black',
        linewidth=2
    )
    ax.add_patch(final_box)
    ax.text(8, 1.9, '生成思维链推理文本', ha='center', va='center', 
            fontsize=12, weight='bold')
    
    # 从四个类型汇聚到最终输出
    for x_pos in [2.25, 5.75, 9.25, 12.75]:
        ax.annotate('', xy=(8, 2.3), xytext=(x_pos, 3),
                   arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # 添加图例
    legend_elements = [
        patches.Patch(color=colors['subject'], label='Subject类型'),
        patches.Patch(color=colors['object'], label='Object类型'),
        patches.Patch(color=colors['relation'], label='Relation类型'),
        patches.Patch(color=colors['type'], label='Type类型'),
        patches.Patch(color=colors['common'], label='汇聚输出')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.tight_layout()
    plt.savefig('cotkr_detail_flow.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_system_architecture():
    """创建系统架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定义层级
    layers = [
        # 用户接口层
        {
            'name': '用户接口层',
            'y': 8.5,
            'components': [
                (1, 8, 3, 0.8, 'simple_qa.py\n简单问答接口'),
                (5, 8, 3, 0.8, 'qa_system_demo.py\n演示系统'),
                (9, 8, 3, 0.8, 'interactive_qa\n交互式问答')
            ],
            'color': '#E3F2FD'
        },
        # 核心引擎层
        {
            'name': '核心引擎层',
            'y': 6.5,
            'components': [
                (3, 6, 3, 0.8, 'retrieval_engine.py\n检索引擎'),
                (7, 6, 3, 0.8, 'cotkr_rewriter.py\nCoTKR重写器')
            ],
            'color': '#FFF3E0'
        },
        # 数据管理层
        {
            'name': '数据管理层',
            'y': 4.5,
            'components': [
                (1, 4, 2.5, 0.8, 'vector_database.py\n向量数据库管理'),
                (4.5, 4, 2.5, 0.8, 'embedding_client.py\n嵌入客户端'),
                (8, 4, 2.5, 0.8, 'data_loader.py\n数据加载器')
            ],
            'color': '#E0F2F1'
        },
        # 外部服务层
        {
            'name': '外部服务层',
            'y': 2.5,
            'components': [
                (1, 2, 2.5, 0.8, 'SiliconFlow API\n嵌入服务'),
                (4.5, 2, 2.5, 0.8, 'ChromaDB\n向量数据库'),
                (8, 2, 2.5, 0.8, 'XML Dataset\n数据集')
            ],
            'color': '#FFEBEE'
        }
    ]
    
    # 绘制层级和组件
    for layer in layers:
        # 绘制层级背景
        layer_bg = FancyBboxPatch(
            (0.5, layer['y'] - 0.3), 13, 1.4,
            boxstyle="round,pad=0.1",
            facecolor=layer['color'],
            alpha=0.3,
            edgecolor='gray',
            linewidth=1
        )
        ax.add_patch(layer_bg)
        
        # 层级标题
        ax.text(0.2, layer['y'] + 0.4, layer['name'], ha='left', va='center', 
                fontsize=12, weight='bold', rotation=90)
        
        # 绘制组件
        for x, y, w, h, text in layer['components']:
            box = FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.05",
                facecolor=layer['color'],
                edgecolor='black',
                linewidth=1
            )
            ax.add_patch(box)
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                    fontsize=9, weight='bold')
    
    # 绘制连接线
    connections = [
        # 用户接口层到核心引擎层
        ((2.5, 8), (4.5, 6.8)),
        ((6.5, 8), (4.5, 6.8)),
        ((10.5, 8), (4.5, 6.8)),
        
        # 核心引擎层内部连接
        ((6, 6.4), (7, 6.4)),
        
        # 核心引擎层到数据管理层
        ((4.5, 6), (2.25, 4.8)),
        ((4.5, 6), (5.75, 4.8)),
        
        # 数据管理层到外部服务层
        ((2.25, 4), (2.25, 2.8)),
        ((5.75, 4), (2.25, 2.8)),
        ((5.75, 4), (5.75, 2.8)),
        ((9.25, 4), (9.25, 2.8)),
    ]
    
    for (x1, y1), (x2, y2) in connections:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # 添加标题
    ax.text(7, 9.5, 'KG-RAG 问答系统架构图', ha='center', va='center', 
            fontsize=16, weight='bold')
    
    plt.tight_layout()
    plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """生成所有流程图"""
    print("🎨 生成问答系统流程图...")
    
    try:
        print("1️⃣ 生成主流程图...")
        create_qa_system_flowchart()
        
        print("2️⃣ 生成CoTKR详细流程图...")
        create_cotkr_detail_flowchart()
        
        print("3️⃣ 生成系统架构图...")
        create_system_architecture()
        
        print("✅ 所有流程图生成完成！")
        print("📁 生成的文件:")
        print("   - qa_system_main_flow.png")
        print("   - cotkr_detail_flow.png") 
        print("   - system_architecture.png")
        
    except Exception as e:
        print(f"❌ 生成流程图时出错: {e}")
        print("💡 请确保已安装matplotlib: pip install matplotlib")

if __name__ == '__main__':
    main()