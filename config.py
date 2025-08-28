# config.py - 新系统配置文件
import os

# --- SiliconFlow API Configuration ---
SILICONFLOW_API_KEY = "sk-uxqvfhcmthztbcsizrkkclnxfqnjmnbxxtdoaajsxknnhmay" 
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/embeddings"
EMBEDDING_MODEL = "BAAI/bge-m3"

# --- OpenAI API Configuration (for QA generation) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Data and Database Paths ---
# 只使用train数据集进行向量数据库嵌入
DATASET_PATHS = [
    r"D:\dataset\train"
]

# dev数据集路径（用于文本QA生成）
DEV_DATASET_PATH = r"D:\dataset\train"

# --- Database Configuration ---
CHROMA_DB_PATH = r"D:\dataset\chroma_data\new_system_db" 
COLLECTION_NAME = f"new_kg_system_{EMBEDDING_MODEL.replace('/', '_')}"
ENHANCED_COLLECTION_NAME = f"enhanced_kg_system_{EMBEDDING_MODEL.replace('/', '_')}"

# --- Enhanced System Configuration ---
RERANKING_ENABLED = True
RERANK_TOP_K_MULTIPLIER = 2  # 第一阶段检索数量 = n_results * multiplier

# --- Processing Configuration ---
BATCH_SIZE = 32

# --- Logging Configuration ---
EMBEDDING_LOG_FILE = "new_system_embedding_log.txt"

# --- QA Generation Configuration ---
QA_OUTPUT_DIR = "qa_datasets"

# --- Evaluation Configuration ---
EVALUATION_OUTPUT_DIR = "evaluation"  # 评估结果输出目录
EVALUATION_SAMPLE_SIZE = 100
EVALUATION_K_VALUES = [1, 3, 5, 10]
SAVE_DETAILED_RESULTS = True  # 是否保存详细结果
SAVE_SUMMARY_CHARTS = True    # 是否保存图表

# --- CoTKR Configuration ---
COTKR_TEMPERATURE = 0.3
COTKR_MAX_TOKENS = 1024