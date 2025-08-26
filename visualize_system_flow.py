# visualize_system_flow.py - 系统流程可视化

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_system_flow_diagram():
    """创建系统流程图"""
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 定义颜色
    colors = {
        'data': '#E3F2FD',      # 浅蓝色 - 数据层
        'storage': '#E8F5E8',   # 浅绿色 - 存储层
        'retrieval': '#F3E5F5', # 浅紫色 - 检索层
        'rewrite': '#FFF3E0',   # 浅橙色 - 重写层
        'eval': '#FCE4EC',      # 浅粉色 - 评估层
        'app': '#F1F8E9'        # 浅黄绿色 - 应用层
    }
    
    # 绘制组件框
    components = [
        # 数据层
        {'name': 'XML知识文件', 'pos': (1, 11), 'size': (1.5, 0.8), 'color': colors['data']},
        {'name': 'KnowledgeDataLoader', 'pos': (3, 11), 'size': (2, 0.8), 'color': colors['data']},
        {'name': '知识条目\n(Triple+Schema)', 'pos': (5.5, 11), 'size': (1.8, 0.8), 'color': colors['data']},
        
        # 存储层
        {'name': 'EmbeddingClient\n(SiliconFlow)', 'pos': (1, 9.5), 'size': (2, 0.8), 'color': colors['storage']},
        {'name': '向量嵌入', 'pos': (3.5, 9.5), 'size': (1.5, 0.8), 'color': colors['storage']},
        {'name': 'ChromaDB\n向量数据库', 'pos': (5.5, 9.5), 'size': (2, 0.8), 'color': colors['storage']},
        
        # 检索层
        {'name': '用户问题', 'pos': (1, 7.5), 'size': (1.5, 0.8), 'color': colors['retrieval']},
        {'name': 'RetrievalEngine', 'pos': (3, 7.5), 'size': (2, 0.8), 'color': colors['retrieval']},
        {'name': '向量相似度检索', 'pos': (5.5, 7.5), 'size': (2, 0.8), 'color': colors['retrieval']},
        {'name': 'Top-K三元组', 'pos': (8, 7.5), 'size': (1.5, 0.8), 'color': colors['retrieval']},
        
        # 重写层
        {'name': 'CoTKRRewriter', 'pos': (1, 5.5), 'size': (2, 0.8), 'color': colors['rewrite']},
        {'name': '问题类型检测', 'pos': (3.5, 5.5), 'size': (2, 0.8), 'color': colors['rewrite']},
        {'name': '思维链推理', 'pos': (6, 5.5), 'size': (1.8, 0.8), 'color': colors['rewrite']},
        {'name': '重写知识', 'pos': (8.2, 5.5), 'size': (1.5, 0.8), 'color': colors['rewrite']},
        {'name': '答案提取', 'pos': (4.5, 4), 'size': (1.5, 0.8), 'color': colors['rewrite']},
        
        # 评估层
        {'name': 'QAGenerator', 'pos': (1, 2.5), 'size': (1.8, 0.8), 'color': colors['eval']},
        {'name': 'QA数据集', 'pos': (3.2, 2.5), 'size': (1.5, 0.8), 'color': colors['eval']},
        {'name': 'EvaluationEngine', 'pos': (5, 2.5), 'size': (2, 0.8), 'color': colors['eval']},
        {'name': 'Precision@K\nRecall@K\nnDCG@K', 'pos': (7.5, 2.5), 'size': (2, 0.8), 'color': colors['eval']},
        
        # 应用层
        {'name': 'MainSystem', 'pos': (2, 0.8), 'size': (2, 0.8), 'color': colors['app']},
        {'name': '交互式查询', 'pos': (4.5, 0.8), 'size': (1.8, 0.8), 'color': colors['app']},
        {'name': '批量查询', 'pos': (6.5, 0.8), 'size': (1.5, 0.8), 'color': colors['app']},
        {'name': '性能评估', 'pos': (8.2, 0.8), 'size': (1.5, 0.8), 'color': colors['app']},
    ]
    
    # 绘制组件
    for comp in components:
        x, y = comp['pos']
        w, h = comp['size']
        
        # 创建圆角矩形
        box = FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.05",
            facecolor=comp['color'],
            edgecolor='black',
            linewidth=1
        )
        ax.add_patch(box)
        
        # 添加文本
        ax.text(x, y, comp['name'], ha='center', va='center', 
                fontsize=9, weight='bold', wrap=True)
    
    # 绘制连接线
    connections = [
        # 数据流
        ((1.75, 11), (3, 11)),      # XML -> DataLoader
        ((4, 11), (5.5, 11)),       # DataLoader -> 知识条目
        ((5.5, 10.6), (5.5, 10.3)), # 知识条目 -> 向量嵌入
        ((3, 9.5), (3.5, 9.5)),     # EmbeddingClient -> 向量嵌入
        ((4.25, 9.5), (5.5, 9.5)),  # 向量嵌入 -> ChromaDB
        
        # 检索流
        ((1.75, 7.5), (3, 7.5)),    # 用户问题 -> RetrievalEngine
        ((4, 7.5), (5.5, 7.5)),     # RetrievalEngine -> 向量检索
        ((6.5, 7.5), (8, 7.5)),     # 向量检索 -> Top-K
        ((6.5, 9.1), (6.5, 8.3)),   # ChromaDB -> 向量检索
        
        # 重写流
        ((8, 7.1), (8, 6.3)),       # Top-K -> 重写知识
        ((1, 6.3), (1, 5.9)),       # 用户问题 -> CoTKR
        ((2, 5.5), (3.5, 5.5)),     # CoTKR -> 问题类型检测
        ((4.5, 5.5), (6, 5.5)),     # 问题类型检测 -> 思维链推理
        ((6.9, 5.5), (8.2, 5.5)),   # 思维链推理 -> 重写知识
        ((8.2, 5.1), (5.2, 4.4)),   # 重写知识 -> 答案提取
        
        # 评估流
        ((1.9, 2.5), (3.2, 2.5)),   # QAGenerator -> QA数据集
        ((3.95, 2.5), (5, 2.5)),    # QA数据集 -> EvaluationEngine
        ((6, 2.5), (7.5, 2.5)),     # EvaluationEngine -> 指标
        
        # 应用层连接
        ((3, 0.8), (4.5, 0.8)),     # MainSystem -> 交互式查询
        ((3, 0.8), (6.5, 0.8)),     # MainSystem -> 批量查询
        ((3, 0.8), (8.2, 0.8)),     # MainSystem -> 性能评估
    ]
    
    for start, end in connections:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc="black", alpha=0.7)
        ax.add_patch(arrow)
    
    # 添加层标签
    layer_labels = [
        ('数据层', 0.2, 11, colors['data']),
        ('存储层', 0.2, 9.5, colors['storage']),
        ('检索层', 0.2, 7.5, colors['retrieval']),
        ('重写层', 0.2, 5.5, colors['rewrite']),
        ('评估层', 0.2, 2.5, colors['eval']),
        ('应用层', 0.2, 0.8, colors['app']),
    ]
    
    for label, x, y, color in layer_labels:
        ax.text(x, y, label, ha='center', va='center', 
                fontsize=12, weight='bold', rotation=90,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.8))
    
    # 添加标题
    ax.text(5, 11.8, '新KG-RAG系统架构流程图', ha='center', va='center', 
            fontsize=16, weight='bold')
    
    # 添加说明
    ax.text(8.5, 11, 'CoTKR特色:\n• 问题类型自动检测\n• 思维链推理\n• 后处理知识重写', 
            ha='left', va='top', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('newSystem/system_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ 系统流程图已保存为 'system_flow_diagram.png'")

def create_component_interaction_diagram():
    """创建组件交互图"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 核心组件位置
    components = {
        'main': {'pos': (5, 5), 'size': (2, 1), 'color': '#FFE0B2', 'name': 'MainSystem\n主系统'},
        'retrieval': {'pos': (2, 7), 'size': (1.8, 0.8), 'color': '#E1F5FE', 'name': 'RetrievalEngine\n检索引擎'},
        'cotkr': {'pos': (8, 7), 'size': (1.8, 0.8), 'color': '#F3E5F5', 'name': 'CoTKRRewriter\n知识重写器'},
        'database': {'pos': (2, 3), 'size': (1.8, 0.8), 'color': '#E8F5E8', 'name': 'VectorDatabase\n向量数据库'},
        'embedding': {'pos': (5, 8.5), 'size': (1.8, 0.8), 'color': '#FFF3E0', 'name': 'EmbeddingClient\n嵌入客户端'},
        'qa_gen': {'pos': (8, 3), 'size': (1.8, 0.8), 'color': '#FCE4EC', 'name': 'QAGenerator\nQA生成器'},
        'evaluator': {'pos': (5, 1.5), 'size': (1.8, 0.8), 'color': '#F1F8E9', 'name': 'EvaluationEngine\n评估引擎'},
        'data_loader': {'pos': (2, 1.5), 'size': (1.8, 0.8), 'color': '#E0F2F1', 'name': 'DataLoader\n数据加载器'},
    }
    
    # 绘制组件
    for comp_id, comp in components.items():
        x, y = comp['pos']
        w, h = comp['size']
        
        # 创建圆角矩形
        box = FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.1",
            facecolor=comp['color'],
            edgecolor='black',
            linewidth=2
        )
        ax.add_patch(box)
        
        # 添加文本
        ax.text(x, y, comp['name'], ha='center', va='center', 
                fontsize=10, weight='bold')
    
    # 绘制交互连接
    interactions = [
        ('main', 'retrieval', '查询请求'),
        ('main', 'qa_gen', 'QA生成'),
        ('main', 'evaluator', '性能评估'),
        ('main', 'database', '数据库管理'),
        ('retrieval', 'cotkr', '知识重写'),
        ('retrieval', 'database', '向量检索'),
        ('database', 'embedding', '向量化'),
        ('data_loader', 'database', '数据填充'),
        ('qa_gen', 'evaluator', 'QA数据'),
        ('evaluator', 'retrieval', '批量查询'),
    ]
    
    for start, end, label in interactions:
        start_pos = components[start]['pos']
        end_pos = components[end]['pos']
        
        # 计算连接点
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = np.sqrt(dx**2 + dy**2)
        
        # 调整起点和终点，避免与框重叠
        offset = 0.9
        start_adj = (start_pos[0] + dx * offset / length, start_pos[1] + dy * offset / length)
        end_adj = (end_pos[0] - dx * offset / length, end_pos[1] - dy * offset / length)
        
        # 绘制箭头
        arrow = ConnectionPatch(start_adj, end_adj, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc="blue", alpha=0.6,
                              linewidth=2)
        ax.add_patch(arrow)
        
        # 添加标签
        mid_x = (start_adj[0] + end_adj[0]) / 2
        mid_y = (start_adj[1] + end_adj[1]) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='center', 
                fontsize=8, bbox=dict(boxstyle="round,pad=0.2", 
                facecolor='white', alpha=0.8))
    
    # 添加标题
    ax.text(5, 9.5, '新KG-RAG系统组件交互图', ha='center', va='center', 
            fontsize=16, weight='bold')
    
    plt.tight_layout()
    plt.savefig('newSystem/component_interaction_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ 组件交互图已保存为 'component_interaction_diagram.png'")

def main():
    """主函数"""
    print("🎨 生成系统可视化图表")
    print("=" * 40)
    
    try:
        create_system_flow_diagram()
        create_component_interaction_diagram()
        
        print("\n🎉 所有图表生成完成！")
        print("📁 生成的文件:")
        print("   - system_flow_diagram.png")
        print("   - component_interaction_diagram.png")
        
    except Exception as e:
        print(f"❌ 图表生成失败: {e}")
        print("请确保已安装matplotlib: pip install matplotlib")

if __name__ == '__main__':
    main()