"""
Módulo de Limpieza de Datos
Gestiona valores nulos, duplicados, normalización y conversiones de tipos.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from config.config import (
    CUSTOMERS_CSV, ORDERS_CSV, ORDER_ITEMS_CSV, ORDER_PAYMENTS_CSV,
    ORDER_REVIEWS_CSV, PRODUCTS_CSV, SELLERS_CSV, GEOLOCATION_CSV,
    CATEGORY_TRANSLATION_CSV, CLEANED_DATA_DIR, DATE_COLUMNS,
    MONETARY_COLUMNS, setup_logging
)

logger = setup_logging("cleaning")


class DataCleaner:
    """Gestiona operaciones de limpieza de datos."""
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Elimina filas duplicadas."""
        initial_rows = len(df)
        df_cleaned = df.drop_duplicates()
        removed = initial_rows - len(df_cleaned)
        
        if removed > 0:
            logger.info(f"{dataset_name}: Se eliminaron {removed} filas duplicadas")
        
        return df_cleaned
    
    @staticmethod
    def handle_nulls(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Gestiona valores nulos de manera inteligente."""
        df_cleaned = df.copy()
        
        null_cols = df_cleaned.columns[df_cleaned.isnull().any()]
        
        for col in null_cols:
            null_count = df_cleaned[col].isnull().sum()
            null_pct = null_count / len(df_cleaned) * 100
            
            if null_pct > 50:
                # Elimina columna si más del 50% son nulos
                logger.warning(f"{dataset_name}.{col}: {null_pct:.2f}% nulos - eliminando columna")
                df_cleaned = df_cleaned.drop(columns=[col])
            elif col in ['payment_installments']:
                # Completa con 0 para cuotas
                df_cleaned[col].fillna(0, inplace=True)
                logger.info(f"{dataset_name}.{col}: Se rellenaron {null_count} nulos con 0")
            elif df_cleaned[col].dtype == 'object':
                # Completa columnas de texto con 'Desconocido'
                df_cleaned[col].fillna('Desconocido', inplace=True)
                logger.info(f"{dataset_name}.{col}: Se rellenaron {null_count} nulos con 'Desconocido'")
            else:
                # Rellena hacia adelante y hacia atrás para columnas numéricas
                df_cleaned[col] = df_cleaned[col].ffill()
                df_cleaned[col] = df_cleaned[col].bfill()
                logger.info(f"{dataset_name}.{col}: Se rellenaron {null_count} nulos con forward/backward fill")
        
        return df_cleaned
    
    @staticmethod
    def normalize_dates(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Convierte columnas de fecha a datetime."""
        df_cleaned = df.copy()
        
        for col in df_cleaned.columns:
            if 'date' in col.lower() or 'timestamp' in col.lower():
                try:
                    df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce')
                    logger.info(f"{dataset_name}.{col}: Convertido a datetime")
                except Exception as e:
                    logger.warning(f"{dataset_name}.{col}: No se pudo convertir a datetime - {e}")
        
        return df_cleaned
    
    @staticmethod
    def normalize_numeric_types(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Normaliza los tipos de datos numéricos."""
        df_cleaned = df.copy()
        
        # Convierte columnas float sin decimales a int
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if df_cleaned[col].dtype == np.float64:
                if df_cleaned[col].apply(lambda x: x == int(x) if pd.notna(x) else True).all():
                    try:
                        df_cleaned[col] = df_cleaned[col].astype('Int64', errors='ignore')
                        logger.debug(f"{dataset_name}.{col}: Convertido a Int64")
                    except:
                        pass
        
        return df_cleaned
    
    @staticmethod
    def clean_categorical_data(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Limpia columnas categóricas."""
        df_cleaned = df.copy()
        
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                # Elimina espacios en blanco al inicio y final
                df_cleaned[col] = df_cleaned[col].str.strip()
                
                # Convierte a minúsculas para consistencia
                if col not in ['order_id', 'customer_id', 'product_id', 'seller_id', 'review_id']:
                    df_cleaned[col] = df_cleaned[col].str.lower()
                
                logger.debug(f"{dataset_name}.{col}: Datos categóricos limpiados")
        
        return df_cleaned
    
    @staticmethod
    def remove_outliers(df: pd.DataFrame, dataset_name: str, method='iqr') -> pd.DataFrame:
        """Detecta y gestiona valores atípicos usando el método IQR."""
        df_cleaned = df.copy()
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = df_cleaned[col].quantile(0.25)
                Q3 = df_cleaned[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_before = len(df_cleaned)
                df_cleaned = df_cleaned[
                    (df_cleaned[col] >= lower_bound) &
                    (df_cleaned[col] <= upper_bound) |
                    (df_cleaned[col].isnull())
                ]
                outliers_after = len(df_cleaned)
                
                if outliers_before > outliers_after:
                    logger.info(f"{dataset_name}.{col}: Se eliminaron {outliers_before - outliers_after} valores extremos")
        
        return df_cleaned


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de clientes."""
    logger.info("Limpiando conjunto de datos de clientes...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'clientes')
    df = cleaner.handle_nulls(df, 'clientes')
    df = cleaner.normalize_numeric_types(df, 'clientes')
    df = cleaner.clean_categorical_data(df, 'clientes')
    
    # Elimina filas con customer_id inválido
    df = df[df['customer_id'].notna() & (df['customer_id'] != '')]
    
    logger.info(f"Clientes limpiados: {len(df)} filas")
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de pedidos."""
    logger.info("Limpiando conjunto de datos de pedidos...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'pedidos')
    df = cleaner.handle_nulls(df, 'pedidos')
    df = cleaner.normalize_dates(df, 'pedidos')
    df = cleaner.normalize_numeric_types(df, 'pedidos')
    df = cleaner.clean_categorical_data(df, 'pedidos')
    
    logger.info(f"Pedidos limpiados: {len(df)} filas")
    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de elementos de pedidos."""
    logger.info("Limpiando conjunto de datos de elementos de pedidos...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'elementos_pedidos')
    df = cleaner.handle_nulls(df, 'elementos_pedidos')
    df = cleaner.normalize_dates(df, 'elementos_pedidos')
    df = cleaner.remove_outliers(df, 'elementos_pedidos')
    df = cleaner.normalize_numeric_types(df, 'elementos_pedidos')
    
    logger.info(f"Elementos de pedidos limpiados: {len(df)} filas")
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de productos."""
    logger.info("Limpiando conjunto de datos de productos...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'productos')
    df = cleaner.handle_nulls(df, 'productos')
    df = cleaner.remove_outliers(df, 'productos')
    df = cleaner.normalize_numeric_types(df, 'productos')
    df = cleaner.clean_categorical_data(df, 'productos')
    
    logger.info(f"Productos limpiados: {len(df)} filas")
    return df


def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de vendedores."""
    logger.info("Limpiando conjunto de datos de vendedores...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'vendedores')
    df = cleaner.handle_nulls(df, 'vendedores')
    df = cleaner.normalize_numeric_types(df, 'vendedores')
    df = cleaner.clean_categorical_data(df, 'vendedores')
    
    logger.info(f"Vendedores limpiados: {len(df)} filas")
    return df


def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de geolocalización."""
    logger.info("Limpiando conjunto de datos de geolocalización...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'geolocalizacion')
    df = cleaner.handle_nulls(df, 'geolocalizacion')
    df = cleaner.remove_outliers(df, 'geolocalizacion')
    df = cleaner.normalize_numeric_types(df, 'geolocalizacion')
    df = cleaner.clean_categorical_data(df, 'geolocalizacion')
    
    logger.info(f"Geolocalización limpiada: {len(df)} filas")
    return df


def clean_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de pagos de pedidos."""
    logger.info("Limpiando conjunto de datos de pagos de pedidos...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'pagos_pedidos')
    df = cleaner.handle_nulls(df, 'pagos_pedidos')
    df = cleaner.remove_outliers(df, 'pagos_pedidos')
    df = cleaner.normalize_numeric_types(df, 'pagos_pedidos')
    df = cleaner.clean_categorical_data(df, 'pagos_pedidos')
    
    logger.info(f"Pagos de pedidos limpiados: {len(df)} filas")
    return df


def clean_order_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el conjunto de datos de reseñas de pedidos."""
    logger.info("Limpiando conjunto de datos de reseñas de pedidos...")
    cleaner = DataCleaner()
    
    df = cleaner.remove_duplicates(df, 'resenas_pedidos')
    df = cleaner.handle_nulls(df, 'resenas_pedidos')
    df = cleaner.normalize_dates(df, 'resenas_pedidos')
    df = cleaner.normalize_numeric_types(df, 'resenas_pedidos')
    df = cleaner.clean_categorical_data(df, 'resenas_pedidos')
    
    logger.info(f"Reseñas de pedidos limpiadas: {len(df)} filas")
    return df


def run_cleaning_phase() -> dict:
    """Ejecuta la fase completa de limpieza."""
    logger.info("=" * 80)
    logger.info("FASE 2: LIMPIEZA DE DATOS")
    logger.info("=" * 80)
    
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    cleaned_datasets = {}
    
    # Carga y limpia cada conjunto de datos
    try:
        df_customers = pd.read_csv(CUSTOMERS_CSV)
        df_customers = clean_customers(df_customers)
        df_customers.to_parquet(CLEANED_DATA_DIR / "clientes_limpiados.parquet", index=False)
        cleaned_datasets['clientes'] = df_customers
        logger.info(f"Guardado: {CLEANED_DATA_DIR / 'clientes_limpiados.parquet'}")
    except Exception as e:
        logger.error(f"Error limpiando clientes: {e}")
    
    try:
        df_orders = pd.read_csv(ORDERS_CSV)
        df_orders = clean_orders(df_orders)
        df_orders.to_parquet(CLEANED_DATA_DIR / "orders_cleaned.parquet", index=False)
        cleaned_datasets['orders'] = df_orders
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'orders_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning orders: {e}")
    
    try:
        df_order_items = pd.read_csv(ORDER_ITEMS_CSV)
        df_order_items = clean_order_items(df_order_items)
        df_order_items.to_parquet(CLEANED_DATA_DIR / "order_items_cleaned.parquet", index=False)
        cleaned_datasets['order_items'] = df_order_items
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'order_items_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning order items: {e}")
    
    try:
        df_order_payments = pd.read_csv(ORDER_PAYMENTS_CSV)
        df_order_payments = clean_order_payments(df_order_payments)
        df_order_payments.to_parquet(CLEANED_DATA_DIR / "order_payments_cleaned.parquet", index=False)
        cleaned_datasets['order_payments'] = df_order_payments
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'order_payments_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning order payments: {e}")
    
    try:
        df_products = pd.read_csv(PRODUCTS_CSV)
        df_products = clean_products(df_products)
        df_products.to_parquet(CLEANED_DATA_DIR / "products_cleaned.parquet", index=False)
        cleaned_datasets['products'] = df_products
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'products_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning products: {e}")
    
    try:
        df_sellers = pd.read_csv(SELLERS_CSV)
        df_sellers = clean_sellers(df_sellers)
        df_sellers.to_parquet(CLEANED_DATA_DIR / "sellers_cleaned.parquet", index=False)
        cleaned_datasets['sellers'] = df_sellers
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'sellers_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning sellers: {e}")
    
    try:
        df_geolocation = pd.read_csv(GEOLOCATION_CSV)
        df_geolocation = clean_geolocation(df_geolocation)
        df_geolocation.to_parquet(CLEANED_DATA_DIR / "geolocation_cleaned.parquet", index=False)
        cleaned_datasets['geolocation'] = df_geolocation
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'geolocation_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning geolocation: {e}")
    
    try:
        df_order_reviews = pd.read_csv(ORDER_REVIEWS_CSV)
        df_order_reviews = clean_order_reviews(df_order_reviews)
        df_order_reviews.to_parquet(CLEANED_DATA_DIR / "order_reviews_cleaned.parquet", index=False)
        cleaned_datasets['order_reviews'] = df_order_reviews
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'order_reviews_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning order reviews: {e}")
    
    try:
        df_category = pd.read_csv(CATEGORY_TRANSLATION_CSV)
        cleaner = DataCleaner()
        df_category = cleaner.remove_duplicates(df_category, 'category_translation')
        df_category.to_parquet(CLEANED_DATA_DIR / "category_translation_cleaned.parquet", index=False)
        cleaned_datasets['category_translation'] = df_category
        logger.info(f"Saved: {CLEANED_DATA_DIR / 'category_translation_cleaned.parquet'}")
    except Exception as e:
        logger.error(f"Error cleaning category translation: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("CLEANING PHASE COMPLETED")
    logger.info("=" * 80 + "\n")
    
    return cleaned_datasets


if __name__ == "__main__":
    cleaner = DataCleaner()
    run_cleaning_phase()
