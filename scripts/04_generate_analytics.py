"""
Módulo de Analítica
Genera KPIs de logística y comerciales para análisis comercial.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from config.config import (
    MERGED_DATA_DIR, ANALYTICS_DATA_DIR, setup_logging
)

logger = setup_logging("analytics")


class AnalyticsEngine:
    """Genera KPIs y métricas comerciales."""
    
    def __init__(self, merged_dir: Path = MERGED_DATA_DIR):
        self.merged_dir = merged_dir
        self.load_datasets()
    
    def load_datasets(self):
        """Carga conjuntos de datos integrados."""
        try:
            self.orders_analysis = pd.read_parquet(
                self.merged_dir / "orders_with_details.parquet"
            )
            logger.info(f"Loaded orders analysis: {len(self.orders_analysis)} rows")
        except Exception as e:
            logger.error(f"Could not load orders analysis: {e}")
            self.orders_analysis = None
        
        try:
            self.sellers_performance = pd.read_parquet(
                self.merged_dir / "sellers_performance.parquet"
            )
            logger.info(f"Loaded sellers performance: {len(self.sellers_performance)} rows")
        except Exception as e:
            logger.error(f"Could not load sellers performance: {e}")
            self.sellers_performance = None
    
    def calculate_logistic_kpis(self) -> pd.DataFrame:
        """Calcula indicadores clave de desempeño en logística."""
        logger.info("Calculando KPIs logísticos...")
        
        if self.orders_analysis is None:
            logger.warning("No orders analysis data available")
            return pd.DataFrame()
        
        df = self.orders_analysis.copy()
        
        kpis = {
            'KPI': [],
            'Value': [],
            'Unit': [],
            'Date_Calculated': []
        }
        
        # 1. Tiempo promedio de entrega
        if 'delivery_time_days' in df.columns:
            avg_delivery = df['delivery_time_days'].mean()
            kpis['KPI'].append('Tiempo Promedio de Entrega')
            kpis['Value'].append(round(avg_delivery, 2))
            kpis['Unit'].append('días')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 2. Tasa de entrega a tiempo
        if 'delivery_delay_days' in df.columns:
            on_time = (df['delivery_delay_days'] <= 0).sum() / len(df) * 100
            kpis['KPI'].append('Tasa de Entrega a Tiempo')
            kpis['Value'].append(round(on_time, 2))
            kpis['Unit'].append('%')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 3. Porcentaje de entregas tardías
        if 'delivery_delay_days' in df.columns:
            late_rate = (df['delivery_delay_days'] > 0).sum() / len(df) * 100
            kpis['KPI'].append('Tasa de Entregas Tardías')
            kpis['Value'].append(round(late_rate, 2))
            kpis['Unit'].append('%')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 4. Promedio de días de retraso en entregas tardías
        if 'delivery_delay_days' in df.columns:
            late_delays = df[df['delivery_delay_days'] > 0]['delivery_delay_days']
            if len(late_delays) > 0:
                avg_late_delay = late_delays.mean()
                kpis['KPI'].append('Average Late Delivery Days')
                kpis['Value'].append(round(avg_late_delay, 2))
                kpis['Unit'].append('days')
                kpis['Date_Calculated'].append(datetime.now().date())
        
        # 5. Total de pedidos procesados
        kpis['KPI'].append('Total Orders Processed')
        kpis['Value'].append(len(df))
        kpis['Unit'].append('orders')
        kpis['Date_Calculated'].append(datetime.now().date())
        
        # 6. Pedidos cancelados
        if 'order_status' in df.columns:
            cancelled = (df['order_status'] == 'cancelled').sum()
            cancelled_rate = cancelled / len(df) * 100
            kpis['KPI'].append('Cancelled Orders Rate')
            kpis['Value'].append(round(cancelled_rate, 2))
            kpis['Unit'].append('%')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 7. Pedidos devueltos
        if 'order_status' in df.columns:
            returned = (df['order_status'].isin(['returned_to_sender', 'unavailable'])).sum()
            returned_rate = returned / len(df) * 100
            kpis['KPI'].append('Return/Unavailable Rate')
            kpis['Value'].append(round(returned_rate, 2))
            kpis['Unit'].append('%')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        return pd.DataFrame(kpis)
    
    def calculate_commercial_kpis(self) -> pd.DataFrame:
        """Calcula indicadores clave de desempeño comercial."""
        logger.info("Calculando KPIs comerciales...")
        
        if self.orders_analysis is None:
            logger.warning("No orders analysis data available")
            return pd.DataFrame()
        
        df = self.orders_analysis.copy()
        
        kpis = {
            'KPI': [],
            'Value': [],
            'Unit': [],
            'Date_Calculated': []
        }
        
        # 1. Ingreso total
        if 'total_payment' in df.columns:
            total_revenue = df['total_payment'].sum()
            kpis['KPI'].append('Total Revenue')
            kpis['Value'].append(round(total_revenue, 2))
            kpis['Unit'].append('BRL')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 2. Valor promedio del pedido
        if 'total_payment' in df.columns:
            avg_order_value = df['total_payment'].mean()
            kpis['KPI'].append('Average Order Value')
            kpis['Value'].append(round(avg_order_value, 2))
            kpis['Unit'].append('BRL')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 3. Puntuación promedio de reseñas
        if 'avg_review_score' in df.columns:
            avg_score = df['avg_review_score'].mean()
            kpis['KPI'].append('Average Review Score')
            kpis['Value'].append(round(avg_score, 2))
            kpis['Unit'].append('stars')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 4. Total de artículos vendidos
        if 'total_items' in df.columns:
            total_items = df['total_items'].sum()
            kpis['KPI'].append('Total Items Sold')
            kpis['Value'].append(int(total_items))
            kpis['Unit'].append('units')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 5. Promedio de artículos por pedido
        if 'total_items' in df.columns:
            avg_items = df['total_items'].mean()
            kpis['KPI'].append('Average Items Per Order')
            kpis['Value'].append(round(avg_items, 2))
            kpis['Unit'].append('units')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 6. Clientes únicos
        if 'customer_id' in df.columns:
            unique_customers = df['customer_id'].nunique()
            kpis['KPI'].append('Unique Customers')
            kpis['Value'].append(unique_customers)
            kpis['Unit'].append('customers')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        # 7. Análisis del método de pago (más común)
        if 'primary_payment_type' in df.columns:
            payment_type_counts = df['primary_payment_type'].value_counts()
            for method, count in payment_type_counts.head(3).items():
                percentage = (count / len(df)) * 100
                kpis['KPI'].append(f'Payment Method: {method}')
                kpis['Value'].append(round(percentage, 2))
                kpis['Unit'].append('%')
                kpis['Date_Calculated'].append(datetime.now().date())
        
        # 8. Costo promedio de envío
        if 'total_freight' in df.columns and 'total_items' in df.columns:
            avg_shipping = df['total_freight'].sum() / df['total_items'].sum()
            kpis['KPI'].append('Average Shipping Cost Per Item')
            kpis['Value'].append(round(avg_shipping, 2))
            kpis['Unit'].append('BRL')
            kpis['Date_Calculated'].append(datetime.now().date())
        
        return pd.DataFrame(kpis)
    
    def calculate_regional_analysis(self) -> pd.DataFrame:
        """Analiza el desempeño por región/estado."""
        logger.info("Calculating regional analysis...")
        
        if self.orders_analysis is None:
            logger.warning("No orders analysis data available")
            return pd.DataFrame()
        
        df = self.orders_analysis.copy()
        
        regional_kpis = []
        
        if 'customer_state' in df.columns and 'total_payment' in df.columns:
            regional_stats = df.groupby('customer_state').agg({
                'order_id': 'count',
                'total_payment': ['sum', 'mean'],
                'customer_id': 'nunique',
                'total_items': 'sum'
            }).reset_index()
            
            regional_stats.columns = ['State', 'Total_Orders', 'Total_Revenue', 
                                      'Avg_Order_Value', 'Unique_Customers', 'Total_Items']
            
            # Calculate metrics
            regional_stats['Orders_Per_Customer'] = regional_stats['Total_Orders'] / regional_stats['Unique_Customers']
            regional_stats['Avg_Items_Per_Order'] = regional_stats['Total_Items'] / regional_stats['Total_Orders']
            
            regional_kpis = regional_stats.copy()
        
        logger.info(f"Regional analysis: {len(regional_kpis)} states")
        return regional_kpis
    
    def calculate_temporal_analysis(self) -> pd.DataFrame:
        """Analiza el desempeño a lo largo del tiempo."""
        logger.info("Calculating temporal analysis...")
        
        if self.orders_analysis is None:
            logger.warning("No orders analysis data available")
            return pd.DataFrame()
        
        df = self.orders_analysis.copy()
        
        if 'order_purchase_timestamp' not in df.columns:
            return pd.DataFrame()
        
        df['order_date'] = pd.to_datetime(df['order_purchase_timestamp']).dt.date
        
        temporal_stats = df.groupby('order_date').agg({
            'order_id': 'count',
            'total_payment': ['sum', 'mean'],
            'customer_id': 'nunique',
            'total_items': 'sum'
        }).reset_index()
        
        temporal_stats.columns = ['Date', 'Orders_Count', 'Revenue', 'Avg_Order_Value',
                                  'Unique_Customers', 'Total_Items']
        
        logger.info(f"Temporal analysis: {len(temporal_stats)} days")
        return temporal_stats


def run_analytics_phase(merged_dir: Path = MERGED_DATA_DIR) -> dict:
    """Ejecuta la fase completa de analítica."""
    logger.info("=" * 80)
    logger.info("PHASE 4: ANALYTICS & KPI GENERATION")
    logger.info("=" * 80)
    
    ANALYTICS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    engine = AnalyticsEngine(merged_dir)
    
    results = {}
    
    # Calculate all KPIs
    try:
        logistic_kpis = engine.calculate_logistic_kpis()
        logistic_kpis.to_csv(ANALYTICS_DATA_DIR / "kpi_logistic.csv", index=False)
        results['logistic_kpis'] = logistic_kpis
        logger.info(f"Saved: {ANALYTICS_DATA_DIR / 'kpi_logistic.csv'}")
    except Exception as e:
        logger.error(f"Error calculating logistic KPIs: {e}")
    
    try:
        commercial_kpis = engine.calculate_commercial_kpis()
        commercial_kpis.to_csv(ANALYTICS_DATA_DIR / "kpi_commercial.csv", index=False)
        results['commercial_kpis'] = commercial_kpis
        logger.info(f"Saved: {ANALYTICS_DATA_DIR / 'kpi_commercial.csv'}")
    except Exception as e:
        logger.error(f"Error calculating commercial KPIs: {e}")
    
    try:
        regional_analysis = engine.calculate_regional_analysis()
        regional_analysis.to_csv(ANALYTICS_DATA_DIR / "analysis_regional.csv", index=False)
        results['regional_analysis'] = regional_analysis
        logger.info(f"Saved: {ANALYTICS_DATA_DIR / 'analysis_regional.csv'}")
    except Exception as e:
        logger.error(f"Error calculating regional analysis: {e}")
    
    try:
        temporal_analysis = engine.calculate_temporal_analysis()
        temporal_analysis.to_csv(ANALYTICS_DATA_DIR / "analysis_temporal.csv", index=False)
        results['temporal_analysis'] = temporal_analysis
        logger.info(f"Saved: {ANALYTICS_DATA_DIR / 'analysis_temporal.csv'}")
    except Exception as e:
        logger.error(f"Error calculating temporal analysis: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("ANALYTICS PHASE COMPLETED")
    logger.info("=" * 80 + "\n")
    
    return results


if __name__ == "__main__":
    run_analytics_phase()
