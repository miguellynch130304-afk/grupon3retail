"""
Módulo de Visualización
Genera visualizaciones académicas profesionales para resultados del análisis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config.config import (
    MERGED_DATA_DIR, ANALYTICS_DATA_DIR, OUTPUTS_DIR, setup_logging
)

logger = setup_logging("visualization")

# Establecer estilo para publicaciones académicas
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10


class VisualizationEngine:
    """Genera visualizaciones académicas profesionales."""
    
    def __init__(self, merged_dir: Path = MERGED_DATA_DIR, analytics_dir: Path = ANALYTICS_DATA_DIR):
        self.merged_dir = merged_dir
        self.analytics_dir = analytics_dir
        self.viz_dir = OUTPUTS_DIR / "visualizations"
        self.viz_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_delivery_performance(self):
        """Grafica el análisis de tiempo de entrega y retrasos."""
        logger.info("Creando visualización de desempeño de entrega...")
        
        try:
            df = pd.read_parquet(self.merged_dir / "orders_with_details.parquet")
        except:
            logger.warning("Could not load orders data")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Métricas de Desempeño Logístico', fontsize=16, fontweight='bold')
        
        # 1. Distribución del tiempo de entrega
        if 'delivery_time_days' in df.columns:
            ax = axes[0, 0]
            df['delivery_time_days'].hist(bins=50, ax=ax, color='steelblue', edgecolor='black', alpha=0.7)
            ax.set_xlabel('Delivery Time (days)')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Delivery Times')
            ax.axvline(df['delivery_time_days'].mean(), color='red', linestyle='--', label=f"Mean: {df['delivery_time_days'].mean():.1f}")
            ax.legend()
        
        # 2. Entrega a tiempo vs tardía
        if 'delivery_delay_days' in df.columns:
            ax = axes[0, 1]
            on_time = (df['delivery_delay_days'] <= 0).sum()
            late = (df['delivery_delay_days'] > 0).sum()
            colors = ['#2ecc71', '#e74c3c']
            wedges, texts, autotexts = ax.pie([on_time, late], labels=['On-Time', 'Late'],
                                               autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('On-Time vs Late Deliveries')
        
        # 3. Distribución de retrasos (para pedidos tardíos)
        if 'delivery_delay_days' in df.columns:
            ax = axes[1, 0]
            late_delays = df[df['delivery_delay_days'] > 0]['delivery_delay_days']
            if len(late_delays) > 0:
                ax.hist(late_delays, bins=30, color='orangered', edgecolor='black', alpha=0.7)
                ax.set_xlabel('Delay (days)')
                ax.set_ylabel('Frequency')
                ax.set_title('Late Delivery Delays Distribution')
        
        # 4. Distribución del estado del pedido
        if 'order_status' in df.columns:
            ax = axes[1, 1]
            status_counts = df['order_status'].value_counts()
            status_counts.plot(kind='barh', ax=ax, color='teal', edgecolor='black')
            ax.set_xlabel('Number of Orders')
            ax.set_title('Order Status Distribution')
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / "01_delivery_performance.png", dpi=300, bbox_inches='tight')
        logger.info(f"Guardado: {self.viz_dir / '01_delivery_performance.png'}")
        plt.close()
    
    def plot_commercial_analysis(self):
        """Grafica las métricas de desempeño comercial."""
        logger.info("Creando visualización de análisis comercial...")
        
        try:
            df = pd.read_parquet(self.merged_dir / "orders_with_details.parquet")
        except:
            logger.warning("No se pudieron cargar los datos de pedidos")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Análisis de Desempeño Comercial', fontsize=16, fontweight='bold')
        
        # 1. Tendencia de ingresos
        if 'order_purchase_timestamp' in df.columns and 'total_payment' in df.columns:
            ax = axes[0, 0]
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['order_purchase_timestamp']).dt.to_period('M')
            monthly_revenue = df_copy.groupby('date')['total_payment'].sum()
            ax.plot(monthly_revenue.index.astype(str), monthly_revenue.values, marker='o', color='green', linewidth=2)
            ax.set_xlabel('Month')
            ax.set_ylabel('Revenue (BRL)')
            ax.set_title('Monthly Revenue Trend')
            ax.tick_params(axis='x', rotation=45)
        
        # 2. Distribución de puntuación de reseñas
        if 'avg_review_score' in df.columns:
            ax = axes[0, 1]
            scores = df['avg_review_score'].dropna()
            ax.hist(scores, bins=5, color='mediumpurple', edgecolor='black', alpha=0.7)
            ax.set_xlabel('Review Score')
            ax.set_ylabel('Frequency')
            ax.set_title('Customer Review Score Distribution')
            ax.set_xticks([1, 2, 3, 4, 5])
        
        # 3. Distribución del método de pago
        if 'primary_payment_type' in df.columns:
            ax = axes[1, 0]
            payment_counts = df['primary_payment_type'].value_counts()
            payment_counts.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
            ax.set_xlabel('Payment Type')
            ax.set_ylabel('Count')
            ax.set_title('Payment Method Distribution')
            ax.tick_params(axis='x', rotation=45)
        
        # 4. Distribución del valor del pedido
        if 'total_payment' in df.columns:
            ax = axes[1, 1]
            ax.hist(df['total_payment'], bins=50, color='coral', edgecolor='black', alpha=0.7)
            ax.set_xlabel('Order Value (BRL)')
            ax.set_ylabel('Frequency')
            ax.set_title('Order Value Distribution')
            ax.axvline(df['total_payment'].mean(), color='darkred', linestyle='--', label=f"Mean: {df['total_payment'].mean():.2f}")
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / "02_commercial_analysis.png", dpi=300, bbox_inches='tight')
        logger.info(f"Guardado: {self.viz_dir / '02_commercial_analysis.png'}")
        plt.close()
    
    def plot_regional_analysis(self):
        """Grafica las métricas de desempeño regional."""
        logger.info("Creando visualización de análisis regional...")
        
        try:
            regional_df = pd.read_csv(self.analytics_dir / "analysis_regional.csv")
        except:
            logger.warning("No se pudieron cargar datos regionales")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Análisis de Desempeño Regional', fontsize=16, fontweight='bold')
        
        # Ordena por total de pedidos
        regional_df = regional_df.sort_values('Total_Orders', ascending=False)
        
        # 1. Pedidos por estado
        ax = axes[0, 0]
        top_states = regional_df.head(10)
        ax.barh(top_states['State'], top_states['Total_Orders'], color='lightcoral', edgecolor='black')
        ax.set_xlabel('Total Orders')
        ax.set_title('Top 10 States by Order Volume')
        
        # 2. Ingresos por estado
        ax = axes[0, 1]
        top_revenue = regional_df.nlargest(10, 'Total_Revenue')
        ax.barh(top_revenue['State'], top_revenue['Total_Revenue'], color='lightgreen', edgecolor='black')
        ax.set_xlabel('Total Revenue (BRL)')
        ax.set_title('Top 10 States by Revenue')
        
        # 3. Clientes únicos por estado
        ax = axes[1, 0]
        top_customers = regional_df.nlargest(10, 'Unique_Customers')
        ax.barh(top_customers['State'], top_customers['Unique_Customers'], color='lightyellow', edgecolor='black')
        ax.set_xlabel('Unique Customers')
        ax.set_title('Top 10 States by Customer Count')
        
        # 4. Valor de pedido promedio por estado
        ax = axes[1, 1]
        ax.scatter(regional_df['Total_Orders'], regional_df['Avg_Order_Value'], alpha=0.6, s=100, color='lightblue', edgecolors='black')
        for idx, row in regional_df.iterrows():
            if idx < 5:  # Etiqueta los 5 principales
                ax.annotate(row['State'], (row['Total_Orders'], row['Avg_Order_Value']),
                           fontsize=8, alpha=0.7)
        ax.set_xlabel('Total Orders')
        ax.set_ylabel('Average Order Value (BRL)')
        ax.set_title('Order Volume vs Average Order Value by State')
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / "03_regional_analysis.png", dpi=300, bbox_inches='tight')
        logger.info(f"Guardado: {self.viz_dir / '03_regional_analysis.png'}")
        plt.close()
    
    def plot_kpi_summary(self):
        """Grafica el panel de resumen de KPI."""
        logger.info("Creando visualización de resumen de KPI...")
        
        try:
            logistic_kpis = pd.read_csv(self.analytics_dir / "kpi_logistic.csv")
            commercial_kpis = pd.read_csv(self.analytics_dir / "kpi_commercial.csv")
        except:
            logger.warning("No se pudieron cargar datos de KPI")
            return
        
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)
        fig.suptitle('Panel Resumen de KPI', fontsize=16, fontweight='bold')
        
        # Mostrar métricas clave como texto
        ax = fig.add_subplot(gs[0, :])
        ax.axis('off')
        
        # Crear texto de resumen
        summary_text = "KEY PERFORMANCE INDICATORS\n" + "="*50 + "\n\n"
        
        # Añadir KPIs de logística
        summary_text += "LOGISTICS METRICS:\n"
        for _, row in logistic_kpis.head(5).iterrows():
            summary_text += f"  {row['KPI']}: {row['Value']} {row['Unit']}\n"
        
        summary_text += "\nCOMMERCIAL METRICS:\n"
        for _, row in commercial_kpis.head(5).iterrows():
            summary_text += f"  {row['KPI']}: {row['Value']} {row['Unit']}\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        # Plot some key metrics
        ax1 = fig.add_subplot(gs[1, 0])
        kpi_names = ['Average Delivery Time', 'On-Time Delivery Rate', 'Average Order Value']
        for name in kpi_names:
            if name in logistic_kpis['KPI'].values:
                val = logistic_kpis[logistic_kpis['KPI'] == name]['Value'].values
                if len(val) > 0:
                    ax1.text(0.5, 0.7, f"{name}: {val[0]}", ha='center', fontsize=11, fontweight='bold')
        ax1.axis('off')
        
        ax2 = fig.add_subplot(gs[1, 1])
        if 'Total Revenue' in commercial_kpis['KPI'].values:
            val = commercial_kpis[commercial_kpis['KPI'] == 'Total Revenue']['Value'].values
            if len(val) > 0:
                ax2.text(0.5, 0.5, f"Total Revenue:\n{val[0]:.2f} BRL", ha='center', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        plt.savefig(self.viz_dir / "04_kpi_summary.png", dpi=300, bbox_inches='tight')
        logger.info(f"Guardado: {self.viz_dir / '04_kpi_summary.png'}")
        plt.close()


def run_visualization_phase(merged_dir: Path = MERGED_DATA_DIR, 
                            analytics_dir: Path = ANALYTICS_DATA_DIR) -> None:
    """Ejecuta la fase completa de visualización."""
    logger.info("=" * 80)
    logger.info("FASE 5: VISUALIZACIÓN")
    logger.info("=" * 80)
    
    engine = VisualizationEngine(merged_dir, analytics_dir)
    
    try:
        engine.plot_delivery_performance()
    except Exception as e:
        logger.error(f"Error creating delivery performance visualization: {e}")
    
    try:
        engine.plot_commercial_analysis()
    except Exception as e:
        logger.error(f"Error creating commercial analysis visualization: {e}")
    
    try:
        engine.plot_regional_analysis()
    except Exception as e:
        logger.error(f"Error creating regional analysis visualization: {e}")
    
    try:
        engine.plot_kpi_summary()
    except Exception as e:
        logger.error(f"Error creating KPI summary visualization: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("VISUALIZATION PHASE COMPLETED")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    run_visualization_phase()
