"""
Módulo de Integración de Datos
Realiza combinaciones complejas entre conjuntos de datos para crear tablas analíticas.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from config.config import (
    CLEANED_DATA_DIR, MERGED_DATA_DIR, setup_logging
)

logger = setup_logging("integration")


class DataIntegrator:
    """Gestiona combinaciones de datos complejas y transformaciones."""
    
    def __init__(self, cleaned_dir: Path = CLEANED_DATA_DIR):
        self.cleaned_dir = cleaned_dir
        self.datasets = self._load_cleaned_datasets()
    
    def _load_cleaned_datasets(self) -> dict:
        """Carga todos los conjuntos de datos limpios."""
        datasets = {}
        
        parquet_files = {
            'customers': 'customers_cleaned.parquet',
            'orders': 'orders_cleaned.parquet',
            'order_items': 'order_items_cleaned.parquet',
            'order_payments': 'order_payments_cleaned.parquet',
            'order_reviews': 'order_reviews_cleaned.parquet',
            'products': 'products_cleaned.parquet',
            'sellers': 'sellers_cleaned.parquet',
            'geolocation': 'geolocation_cleaned.parquet',
            'category_translation': 'category_translation_cleaned.parquet'
        }
        
        for name, filename in parquet_files.items():
            try:
                filepath = self.cleaned_dir / filename
                if filepath.exists():
                    datasets[name] = pd.read_parquet(filepath)
                    logger.info(f"Cargado {name}: {len(datasets[name])} filas")
            except Exception as e:
                logger.warning(f"No se pudo cargar {name}: {e}")
        
        return datasets
    
    def create_order_analysis_table(self) -> pd.DataFrame:
        """
        Crea una tabla de análisis de pedidos completa.
        Combina (merge): pedidos <- clientes, elementos de pedidos, pagos, reseñas, productos, vendedores
        """
        logger.info("Creando tabla de análisis de pedidos...")
        
        # Comienza con pedidos
        df = self.datasets['orders'].copy()
        logger.info(f"Iniciando con pedidos: {len(df)} filas")
        
        # 1. Información de clientes
        if 'customers' in self.datasets:
            df = df.merge(
                self.datasets['customers'][['customer_id', 'customer_unique_id', 
                                            'customer_zip_code_prefix', 'customer_city', 'customer_state']],
                on='customer_id',
                how='left',
                indicator=False
            )
            logger.info(f"Después del merge con clientes: {len(df)} filas")
        
        # 2. Elementos del pedido
        if 'order_items' in self.datasets:
            order_items_agg = self.datasets['order_items'].groupby('order_id').agg({
                'order_item_id': 'count',
                'product_id': 'count',
                'seller_id': 'nunique',
                'price': ['sum', 'mean', 'min', 'max'],
                'freight_value': ['sum', 'mean']
            }).reset_index()
            
            # Aplana los nombres de columnas
            order_items_agg.columns = ['order_id', 'total_items', 'product_count',
                                       'seller_count', 'total_price', 'avg_price',
                                       'min_price', 'max_price', 'total_freight', 'avg_freight']
            
            df = df.merge(order_items_agg, on='order_id', how='left')
            logger.info(f"After order items merge: {len(df)} rows")
        
        # 3. Pagos del pedido
        if 'order_payments' in self.datasets:
            order_payments_agg = self.datasets['order_payments'].groupby('order_id').agg({
                'payment_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown',
                'payment_installments': 'max',
                'payment_value': 'sum'
            }).reset_index()
            
            order_payments_agg.columns = ['order_id', 'primary_payment_type', 
                                          'max_installments', 'total_payment']
            
            df = df.merge(order_payments_agg, on='order_id', how='left')
            logger.info(f"After order payments merge: {len(df)} rows")
        
        # 4. Reseñas del pedido
        if 'order_reviews' in self.datasets:
            order_reviews_agg = self.datasets['order_reviews'].groupby('order_id').agg({
                'review_id': 'count',
                'review_score': 'mean',
                'review_creation_date': 'max'
            }).reset_index()
            
            order_reviews_agg.columns = ['order_id', 'review_count', 'avg_review_score', 'last_review_date']
            
            df = df.merge(order_reviews_agg, on='order_id', how='left')
            logger.info(f"After order reviews merge: {len(df)} rows")
        
        # Calcula métricas de entrega
        if 'order_delivered_customer_date' in df.columns and 'order_purchase_timestamp' in df.columns:
            df['delivery_time_days'] = (
                pd.to_datetime(df['order_delivered_customer_date']) - 
                pd.to_datetime(df['order_purchase_timestamp'])
            ).dt.days
        
        if 'order_estimated_delivery_date' in df.columns and 'order_delivered_customer_date' in df.columns:
            df['delivery_delay_days'] = (
                pd.to_datetime(df['order_delivered_customer_date']) - 
                pd.to_datetime(df['order_estimated_delivery_date'])
            ).dt.days
        
        logger.info(f"Order analysis table created: {len(df)} rows x {len(df.columns)} columns")
        return df
    
    def create_product_seller_table(self) -> pd.DataFrame:
        """
        Crea una tabla de análisis de productos-vendedores.
        Combina: productos <- traducción de categoría, elementos de pedidos -> vendedores
        """
        logger.info("Creating product-seller analysis table...")
        
        # Comienza con productos
        df = self.datasets['products'].copy()
        
        # Añade traducción de categoría
        if 'category_translation' in self.datasets:
            df = df.merge(
                self.datasets['category_translation'],
                on='product_category_name',
                how='left'
            )
        
        # Agrega ventas por producto
        if 'order_items' in self.datasets:
            product_sales = self.datasets['order_items'].groupby('product_id').agg({
                'order_id': 'count',
                'seller_id': 'nunique',
                'price': ['sum', 'mean', 'count'],
                'freight_value': 'mean'
            }).reset_index()
            
            product_sales.columns = ['product_id', 'total_orders', 'seller_count',
                                    'revenue', 'avg_price', 'units_sold', 'avg_freight']
            
            df = df.merge(product_sales, on='product_id', how='left')
        
        logger.info(f"Product-seller table created: {len(df)} rows")
        return df
    
    def create_seller_performance_table(self) -> pd.DataFrame:
        """
        Crea la tabla de análisis del desempeño del vendedor.
        Combina: vendedores <- elementos de pedidos, pedidos
        """
        logger.info("Creating seller performance table...")
        
        # Comienza con vendedores
        df = self.datasets['sellers'].copy()
        
        # Agrega ventas por vendedor
        if 'order_items' in self.datasets:
            seller_sales = self.datasets['order_items'].groupby('seller_id').agg({
                'order_id': 'nunique',
                'price': ['sum', 'mean', 'count'],
                'freight_value': 'mean'
            }).reset_index()
            
            seller_sales.columns = ['seller_id', 'orders_count', 'revenue',
                                   'avg_price', 'units_sold', 'avg_freight']
            
            df = df.merge(seller_sales, on='seller_id', how='left')
        
        logger.info(f"Seller performance table created: {len(df)} rows")
        return df
    
    def create_master_dataset(self) -> pd.DataFrame:
        """Crea un conjunto de datos maestro completo."""
        logger.info("Creating master dataset...")
        
        # Comienza con tabla de análisis de pedidos
        df = self.create_order_analysis_table()
        
        logger.info(f"Master dataset created: {len(df)} rows x {len(df.columns)} columns")
        return df


def run_integration_phase(cleaned_dir: Path = CLEANED_DATA_DIR) -> dict:
    """Ejecuta la fase completa de integración."""
    logger.info("=" * 80)
    logger.info("PHASE 3: DATA INTEGRATION")
    logger.info("=" * 80)
    
    MERGED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    integrator = DataIntegrator(cleaned_dir)
    
    # Create integrated tables
    try:
        df_orders_analysis = integrator.create_order_analysis_table()
        df_orders_analysis.to_parquet(MERGED_DATA_DIR / "orders_with_details.parquet", index=False)
        logger.info(f"Saved: {MERGED_DATA_DIR / 'orders_with_details.parquet'}")
    except Exception as e:
        logger.error(f"Error creating order analysis table: {e}")
        df_orders_analysis = None
    
    try:
        df_product_seller = integrator.create_product_seller_table()
        df_product_seller.to_parquet(MERGED_DATA_DIR / "products_sellers_analysis.parquet", index=False)
        logger.info(f"Saved: {MERGED_DATA_DIR / 'products_sellers_analysis.parquet'}")
    except Exception as e:
        logger.error(f"Error creating product-seller table: {e}")
        df_product_seller = None
    
    try:
        df_seller_perf = integrator.create_seller_performance_table()
        df_seller_perf.to_parquet(MERGED_DATA_DIR / "sellers_performance.parquet", index=False)
        logger.info(f"Saved: {MERGED_DATA_DIR / 'sellers_performance.parquet'}")
    except Exception as e:
        logger.error(f"Error creating seller performance table: {e}")
        df_seller_perf = None
    
    try:
        df_master = integrator.create_master_dataset()
        df_master.to_parquet(MERGED_DATA_DIR / "master_dataset.parquet", index=False)
        logger.info(f"Saved: {MERGED_DATA_DIR / 'master_dataset.parquet'}")
    except Exception as e:
        logger.error(f"Error creating master dataset: {e}")
        df_master = None
    
    logger.info("\n" + "=" * 80)
    logger.info("INTEGRATION PHASE COMPLETED")
    logger.info("=" * 80 + "\n")
    
    return {
        'orders_analysis': df_orders_analysis,
        'product_seller': df_product_seller,
        'seller_performance': df_seller_perf,
        'master_dataset': df_master
    }


if __name__ == "__main__":
    run_integration_phase()
