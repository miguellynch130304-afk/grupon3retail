"""
Módulo de Exploración y Perfilado de Datos
Genera perfiles estadísticos y detecta problemas de calidad de datos.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from config.config import (
    CSV_DIR, setup_logging, DATE_COLUMNS, MONETARY_COLUMNS
)

logger = setup_logging("exploration")


class DataProfiler:
    """Genera perfiles de datos detallados."""
    
    def __init__(self, csv_dir: Path = CSV_DIR):
        self.csv_dir = csv_dir
        self.profiles = {}
    
    def profile_dataframe(self, df: pd.DataFrame, dataset_name: str) -> dict:
        """Genera un perfil detallado para un conjunto de datos."""
        profile = {
            'conjunto_datos': dataset_name,
            'forma': df.shape,
            'columnas': list(df.columns),
            'tipos_datos': df.dtypes.to_dict(),
            'memoria_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'duplicados': df.duplicated().sum(),
            'conteo_nulos': df.isnull().sum().to_dict(),
            'porcentaje_nulos': (df.isnull().sum() / len(df) * 100).to_dict(),
            'resumen_numerico': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
            'conteos_unicos': df.nunique().to_dict(),
        }
        return profile
    
    def profile_all_datasets(self) -> dict:
        """Perfila todos los archivos CSV."""
        csv_files = sorted(self.csv_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                logger.info(f"Perfilando {csv_file.name}...")
                df = pd.read_csv(csv_file)
                self.profiles[csv_file.stem] = self.profile_dataframe(df, csv_file.name)
                logger.info(f"  -> {df.shape[0]:,} filas x {df.shape[1]} columnas")
            except Exception as e:
                logger.error(f"Error perfilando {csv_file.name}: {e}")
        
        return self.profiles
    
    def save_profile_report(self, output_path: Path) -> None:
        """Guarda el informe de perfilado como archivo de texto."""
        with open(output_path, 'w') as f:
            f.write("=" * 100 + "\n")
            f.write("INFORME DE PERFILADO DE DATOS - Pipeline Olist Brasil\n")
            f.write("=" * 100 + "\n\n")
            
            for dataset_name, profile in self.profiles.items():
                f.write(f"\nCONJUNTO DE DATOS: {profile['conjunto_datos']}\n")
                f.write("-" * 100 + "\n")
                f.write(f"Forma: {profile['forma'][0]:,} filas x {profile['forma'][1]} columnas\n")
                f.write(f"Memoria: {profile['memoria_mb']:.2f} MB\n")
                f.write(f"Duplicados: {profile['duplicados']}\n\n")
                
                f.write("COLUMNAS:\n")
                for col in profile['columnas']:
                    null_pct = profile['porcentaje_nulos'].get(col, 0)
                    unique = profile['conteos_unicos'].get(col, 0)
                    dtype = profile['tipos_datos'].get(col, 'desconocido')
                    f.write(f"  - {col}: {dtype} ({unique} únicos, {null_pct:.2f}% nulos)\n")
                
                f.write("\n")


class DataValidator:
    """Valida y detecta problemas de calidad de datos."""
    
    @staticmethod
    def detect_issues(df: pd.DataFrame, dataset_name: str) -> dict:
        """Detecta problemas de calidad de datos."""
        issues = {
            'conjunto_datos': dataset_name,
            'filas_totales': len(df),
            'duplicados': {
                'conteo': df.duplicated().sum(),
                'porcentaje': df.duplicated().sum() / len(df) * 100
            },
            'valores_nulos': {
                'columnas_con_nulos': df.columns[df.isnull().any()].tolist(),
                'resumen_nulos': df.isnull().sum()[df.isnull().sum() > 0].to_dict()
            },
            'problemas_tipo_dato': [],
            'valores_extremos': {}
        }
        
        # Verifica las columnas de fecha para consistencia
        for col in df.columns:
            if 'date' in col.lower() or 'timestamp' in col.lower():
                try:
                    pd.to_datetime(df[col], errors='raise')
                except:
                    issues['problemas_tipo_dato'].append(f"{col}: No es un datetime válido")
        
        # Verifica columnas numéricas para valores extremos
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > 0:
                issues['valores_extremos'][col] = {
                    'conteo': int(outliers),
                    'porcentaje': float(outliers / len(df) * 100)
                }
        
        return issues


def run_exploration_phase(csv_dir: Path = CSV_DIR) -> dict:
    """Ejecuta la fase completa de exploración."""
    logger.info("=" * 80)
    logger.info("FASE 1: EXPLORACIÓN DE DATOS")
    logger.info("=" * 80)
    
    profiler = DataProfiler(csv_dir)
    profiles = profiler.profile_all_datasets()
    
    # Generar reporte de validación
    logger.info("\nREPORTE DE VALIDACIÓN:")
    logger.info("-" * 80)
    
    validator = DataValidator()
    all_issues = {}
    
    for csv_file in sorted(csv_dir.glob("*.csv")):
        try:
            df = pd.read_csv(csv_file)
            issues = validator.detect_issues(df, csv_file.stem)
            all_issues[csv_file.stem] = issues
            
            logger.info(f"\n{csv_file.name}")
            logger.info(f"  Duplicados: {issues['duplicados']['conteo']} ({issues['duplicados']['porcentaje']:.2f}%)")
            if issues['valores_nulos']['columnas_con_nulos']:
                logger.info(f"  Columnas con nulos: {', '.join(issues['valores_nulos']['columnas_con_nulos'])}")
            if issues['valores_extremos']:
                logger.info(f"  Valores extremos detectados en: {', '.join(issues['valores_extremos'].keys())}")
        except Exception as e:
            logger.error(f"Error validando {csv_file.name}: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("FASE DE EXPLORACIÓN COMPLETADA")
    logger.info("=" * 80 + "\n")
    
    return {
        'profiles': profiles,
        'issues': all_issues
    }


if __name__ == "__main__":
    from config.config import OUTPUTS_DIR, create_project_directories
    
    create_project_directories()
    result = run_exploration_phase()
    
    profiler = DataProfiler()
    profiler.profiles = result['profiles']
    profiler.save_profile_report(OUTPUTS_DIR / "data_profile_report.txt")
    logger.info(f"Informe de perfilado guardado en {OUTPUTS_DIR / 'data_profile_report.txt'}")
