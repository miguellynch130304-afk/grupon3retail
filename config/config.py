"""
Módulo de Configuración para el Pipeline de Olist Brasil
Define rutas, constantes, registros y configuraciones del proyecto.
"""

import logging
from pathlib import Path
from datetime import datetime

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent

# Directorios de datos
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CLEANED_DATA_DIR = PROCESSED_DATA_DIR / "cleaned"
MERGED_DATA_DIR = PROCESSED_DATA_DIR / "merged"
ANALYTICS_DATA_DIR = PROCESSED_DATA_DIR / "analytics"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
EXPORTS_DIR = DATA_DIR / "exports"

# Rutas de datos crudos
CSV_DIR = RAW_DATA_DIR / "csv"
JSON_DIR = RAW_DATA_DIR / "json"

# Directorios de scripts y salida
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Archivos CSV
CUSTOMERS_CSV = CSV_DIR / "olist_customers_dataset.csv"
ORDERS_CSV = CSV_DIR / "olist_orders_dataset.csv"
ORDER_ITEMS_CSV = CSV_DIR / "olist_order_items_dataset.csv"
ORDER_PAYMENTS_CSV = CSV_DIR / "olist_order_payments_dataset.csv"
ORDER_REVIEWS_CSV = CSV_DIR / "olist_order_reviews_dataset.csv"
PRODUCTS_CSV = CSV_DIR / "olist_products_dataset.csv"
SELLERS_CSV = CSV_DIR / "olist_sellers_dataset.csv"
GEOLOCATION_CSV = CSV_DIR / "olist_geolocation_dataset.csv"
CATEGORY_TRANSLATION_CSV = CSV_DIR / "product_category_name_translation.csv"

# Archivos JSON
BRAZIL_GEO_JSON = JSON_DIR / "brazil_geo.json"

# Archivos de salida
CLEANED_ORDERS_PARQUET = CLEANED_DATA_DIR / "orders_cleaned.parquet"
CLEANED_PRODUCTS_PARQUET = CLEANED_DATA_DIR / "products_cleaned.parquet"
CLEANED_CUSTOMERS_PARQUET = CLEANED_DATA_DIR / "customers_cleaned.parquet"
CLEANED_SELLERS_PARQUET = CLEANED_DATA_DIR / "sellers_cleaned.parquet"

MERGED_MASTER_PARQUET = MERGED_DATA_DIR / "master_dataset.parquet"
MERGED_ORDER_ANALYSIS_PARQUET = MERGED_DATA_DIR / "orders_with_details.parquet"

ANALYTICS_KPI_CSV = ANALYTICS_DATA_DIR / "kpi_logistic_commercial.csv"
ANALYTICS_REGIONAL_CSV = ANALYTICS_DATA_DIR / "regional_analysis.csv"
ANALYTICS_TEMPORAL_CSV = ANALYTICS_DATA_DIR / "temporal_analysis.csv"

# Configuración de registro
def setup_logging(log_name: str = "pipeline") -> logging.Logger:
    """Configura la sistema de registro de eventos."""
    log_dir = OUTPUTS_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{log_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    
    # Gestor de archivo
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # Gestor de consola
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


# Constantes de datos
NULL_HANDLING_STRATEGY = {
    'drop': ['review_comment_title', 'review_comment_message', 'product_category_name'],
    'forward_fill': ['order_approved_at', 'order_delivered_carrier_date'],
    'zero': ['payment_installments']
}

# Columnas monetarias para estandarización de formato
MONETARY_COLUMNS = [
    'price', 'freight_value', 'payment_value',
    'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'
]

# Columnas geográficas
GEOGRAPHIC_COLUMNS = ['customer_zip_code_prefix', 'seller_zip_code_prefix', 'geolocation_zip_code_prefix']

# Columnas de fecha
DATE_COLUMNS = [
    'order_purchase_timestamp', 'order_approved_at', 
    'order_delivered_carrier_date', 'order_delivered_customer_date',
    'order_estimated_delivery_date', 'review_creation_date', 'review_answer_timestamp',
    'shipping_limit_date'
]

# Etapas del pipeline
PIPELINE_STAGES = [
    'EXPLORACIÓN',
    'LIMPIEZA',
    'INTEGRACIÓN',
    'ANALÍTICA',
    'VISUALIZACIÓN',
    'EXPORTACIÓN'
]

# Crear todos los directorios necesarios
def create_project_directories():
    """Crea todos los directorios del proyecto si no existen."""
    dirs = [
        CLEANED_DATA_DIR,
        MERGED_DATA_DIR,
        ANALYTICS_DATA_DIR,
        EXTERNAL_DATA_DIR,
        EXPORTS_DIR,
        OUTPUTS_DIR,
        NOTEBOOKS_DIR,
        OUTPUTS_DIR / "logs",
        OUTPUTS_DIR / "visualizations",
        OUTPUTS_DIR / "reports"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    create_project_directories()
    logger = setup_logging("config_test")
    logger.info("Módulo de configuración cargado exitosamente")
