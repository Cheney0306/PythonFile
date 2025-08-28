# 评估结果目录

这个目录用于存储检索系统的评估结果。

## 📁 文件结构

运行评估后，会生成以下类型的文件：

### 📊 主要结果文件
- `full_evaluation_results_YYYYMMDD_HHMMSS.json` - 完整评估结果
- `evaluation_summary_YYYYMMDD_HHMMSS.json` - 汇总指标
- `evaluation_report_YYYYMMDD_HHMMSS.md` - Markdown报告

### 📈 数据文件
- `metrics_comparison_YYYYMMDD_HHMMSS.csv` - CSV格式的指标对比
- `detailed_results_YYYYMMDD_HHMMSS.json` - 详细结果（可选）

### 📊 可视化图表
- `charts_YYYYMMDD_HHMMSS/` - 图表目录
  - `metrics_comparison.png` - 指标对比柱状图
  - `k_trend_analysis.png` - K值趋势图
  - `improvement_analysis.png` - 改进幅度图

## 🚀 如何生成评估结果

### 1. 完整评估
```bash
python retrieval_evaluation_system.py
```

### 2. 快速评估
```bash
python retrieval_evaluation_system.py --mode quick
```

### 3. 自定义评估
```bash
python retrieval_evaluation_system.py --mode custom --sample-size 50
```

## 📊 如何查看结果

### 1. 列出所有结果
```bash
python evaluation_viewer.py --action list
```

### 2. 查看特定结果
```bash
python evaluation_viewer.py --action view --index 1
```

### 3. 对比多个结果
```bash
python evaluation_viewer.py --action compare
```

### 4. 导出到Excel
```bash
python evaluation_viewer.py --action export
```

## 💡 注意事项

- 评估结果按时间戳命名，便于版本管理
- 建议定期清理旧的评估结果以节省空间
- 可以通过修改 `config.py` 中的配置来自定义输出格式

更多详细信息请参考 `EVALUATION_GUIDE.md`。