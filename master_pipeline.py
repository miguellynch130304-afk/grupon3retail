"""
Orquestador Principal del Pipeline
Ejecuta el pipeline completo de datos desde datos crudos hasta analítica y visualizaciones.

ARQUITECTURA DEL PIPELINE:
- FASE 1: EXPLORACIÓN - Perfilado de datos y evaluación de calidad
- FASE 2: LIMPIEZA - Validación de datos, normalización y deduplicación
- FASE 3: INTEGRACIÓN - Combinaciones complejas y creación de conjuntos de datos
- FASE 4: ANALÍTICA - Cálculo de KPI y métricas comerciales
- FASE 5: VISUALIZACIÓN - Gráficos académicos profesionales (Python/matplotlib/seaborn)
- FASE 6: VISUALIZACIÓN AVANZADA - Gráficos estadísticos avanzados (R/ggplot2)
"""

import sys
import time
import importlib
import importlib.util
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Añade proyecto a la ruta
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    create_project_directories, setup_logging, OUTPUTS_DIR, 
    PIPELINE_STAGES, EXPORTS_DIR
)

logger = setup_logging("master_pipeline")


class MasterPipeline:
    """Orquesta el pipeline de datos completo."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.execution_log = {
            'start_time': self.start_time.isoformat(),
            'stages': {},
            'errors': []
        }
        
        logger.info("\n" + "=" * 100)
        logger.info("OLIST BRASIL - PIPELINE HÍBRIDO DE INGESTA Y ANÁLISIS DE DATOS")
        logger.info("=" * 100)
        logger.info(f"Hora de inicio: {self.start_time}")
        logger.info("=" * 100 + "\n")
    
    def run_phase(self, phase_name: str, module_name: str, function_name: str) -> bool:
        """Ejecuta una fase del pipeline."""
        logger.info(f"\n>>> EJECUTANDO FASE: {phase_name}")
        phase_start = time.time()
        
        try:
            # Importa el módulo dinámicamente
            module = importlib.import_module(module_name)
            phase_function = getattr(module, function_name)
            
            # Ejecuta la función de fase
            result = phase_function()
            
            phase_time = time.time() - phase_start
            self.execution_log['stages'][phase_name] = {
                'status': 'EXITOSA',
                'duration_seconds': phase_time,
                'result_type': type(result).__name__
            }
            
            logger.info(f"<<< FASE COMPLETADA: {phase_name} ({phase_time:.2f}s)")
            return True
            
        except Exception as e:
            logger.error(f"<<< FASE FALLIDA: {phase_name}")
            logger.error(f"Error: {str(e)}")
            self.execution_log['stages'][phase_name] = {
                'status': 'FALLIDA',
                'error': str(e)
            }
            self.execution_log['errors'].append({
                'phase': phase_name,
                'error': str(e)
            })
            return False
    
    def run_r_visualization_phase(self, phase_name: str = 'FASE 6: VISUALIZACION AVANZADA (R/ggplot2)') -> bool:
        """Ejecuta visualizaciones avanzadas con R/ggplot2."""
        logger.info(f"\n>>> EJECUTANDO FASE: {phase_name}")
        phase_start = time.time()
        
        try:
            # Detecta el directorio del script
            r_script_path = PROJECT_ROOT / 'scripts' / '06_generate_visualizations_r.R'
            
            if not r_script_path.exists():
                logger.warning(f"Script R no encontrado en {r_script_path}")
                self.execution_log['stages'][phase_name] = {
                    'status': 'SKIPPED',
                    'reason': 'Script R no encontrado'
                }
                return False
            
            # Detecta el sistema operativo y prepara el comando
            system = platform.system()
            rscript_path = None
            
            if system == 'Windows':
                # Busca Rscript en rutas estándar de Windows
                windows_r_paths = [
                    r'C:\Program Files\R\R-4.6.0\bin\Rscript.exe',
                    r'C:\Program Files\R\R-4.5.0\bin\Rscript.exe',
                    r'C:\Program Files\R\R-4.4.0\bin\Rscript.exe',
                    r'C:\Program Files (x86)\R\R-4.6.0\bin\Rscript.exe',
                ]
                
                # Intenta con rutas conocidas
                for path in windows_r_paths:
                    if Path(path).exists():
                        rscript_path = path
                        break
                
                # Si no encuentra en rutas estándar, intenta con Rscript.exe en PATH
                if not rscript_path:
                    rscript_path = 'Rscript.exe'
                    
            else:
                # Linux/Mac: usa Rscript desde PATH
                rscript_path = 'Rscript'
            
            # Ejecuta el script R
            logger.info(f"Ejecutando script R: {r_script_path}")
            logger.info(f"Usando Rscript: {rscript_path}")
            
            cmd = [str(rscript_path), str(r_script_path)]
            
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600  # 10 minutos timeout
            )
            
            # Procesa salida
            if result.stdout:
                logger.info(f"Salida R:\n{result.stdout}")
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Error desconocido en ejecución de R"
                logger.error(f"R exit code: {result.returncode}")
                logger.error(f"Stderr: {error_msg}")
                
                self.execution_log['stages'][phase_name] = {
                    'status': 'FAILED',
                    'error': error_msg,
                    'exit_code': result.returncode
                }
                return False
            
            phase_time = time.time() - phase_start
            self.execution_log['stages'][phase_name] = {
                'status': 'SUCCESS',
                'duration_seconds': phase_time,
                'script': str(r_script_path)
            }
            
            logger.info(f"<<< FASE COMPLETADA: {phase_name} ({phase_time:.2f}s)")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"<<< FASE FALLIDA: {phase_name} - Timeout (10 minutos)")
            self.execution_log['stages'][phase_name] = {
                'status': 'FAILED',
                'error': 'Timeout - proceso R ejecutándose demasiado tiempo'
            }
            return False
            
        except FileNotFoundError:
            logger.error("Rscript no encontrado en el PATH del sistema")
            logger.info("Para instalar R, visite: https://www.r-project.org/")
            self.execution_log['stages'][phase_name] = {
                'status': 'FAILED',
                'error': 'Rscript no encontrado en PATH'
            }
            return False
            
        except Exception as e:
            logger.error(f"<<< FASE FALLIDA: {phase_name}")
            logger.error(f"Error: {str(e)}")
            self.execution_log['stages'][phase_name] = {
                'status': 'FAILED',
                'error': str(e)
            }
            self.execution_log['errors'].append({
                'phase': phase_name,
                'error': str(e)
            })
            return False

    
    def execute_pipeline(self, skip_phases: list = None) -> bool:
        """Ejecuta el pipeline completo."""
        if skip_phases is None:
            skip_phases = []
        
        # Crea directorios del proyecto
        create_project_directories()
        logger.info("Directorios del proyecto creados/verificados\n")
        
        # Fase 1: Exploración
        if 'EXPLORATION' not in skip_phases:
            success = self.run_phase(
                'PHASE 1: EXPLORATION',
                'scripts.explore_data' if importlib.util.find_spec('scripts.explore_data') else 'scripts.01_explore_data',
                'run_exploration_phase'
            )
            if not success:
                logger.warning("Continuando a pesar de errores de exploración...")
        
        # Fase 2: Limpieza
        if 'CLEANING' not in skip_phases:
            success = self.run_phase(
                'PHASE 2: CLEANING',
                'scripts.clean_data' if importlib.util.find_spec('scripts.clean_data') else 'scripts.02_clean_data',
                'run_cleaning_phase'
            )
            if not success:
                logger.warning("Continuando a pesar de errores de limpieza...")
        
        # Fase 3: Integración
        if 'INTEGRATION' not in skip_phases:
            success = self.run_phase(
                'PHASE 3: INTEGRATION',
                'scripts.integrate_data' if importlib.util.find_spec('scripts.integrate_data') else 'scripts.03_integrate_data',
                'run_integration_phase'
            )
            if not success:
                logger.warning("Continuando a pesar de errores de integración...")
        
        # Fase 4: Analítica
        if 'ANALYTICS' not in skip_phases:
            success = self.run_phase(
                'PHASE 4: ANALYTICS',
                'scripts.generate_analytics' if importlib.util.find_spec('scripts.generate_analytics') else 'scripts.04_generate_analytics',
                'run_analytics_phase'
            )
            if not success:
                logger.warning("Continuando a pesar de errores de analítica...")
        
        # Fase 5: Visualización
        if 'VISUALIZATION' not in skip_phases:
            success = self.run_phase(
                'PHASE 5: VISUALIZATION',
                'scripts.generate_visualizations' if importlib.util.find_spec('scripts.generate_visualizations') else 'scripts.05_generate_visualizations',
                'run_visualization_phase'
            )
            if not success:
                logger.warning("Continuando a pesar de errores de visualización...")
        
        # Fase 6: Visualización Avanzada (R/ggplot2)
        if 'ADVANCED_VISUALIZATION' not in skip_phases:
            self.run_r_visualization_phase()
        
        return True
    
    def generate_summary_report(self) -> str:
        """Genera resumen de ejecución del pipeline."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        report = "\n" + "=" * 100 + "\n"
        report += "RESUMEN DE EJECUCIÓN DEL PIPELINE\n"
        report += "=" * 100 + "\n\n"
        
        report += f"Hora de inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Hora de finalización: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Duración total: {total_duration:.2f} segundos ({total_duration/60:.2f} minutos)\n\n"
        
        report += "ESTADO DE EJECUCIÓN POR FASE:\n"
        report += "-" * 100 + "\n"
        
        for phase, status in self.execution_log['stages'].items():
            status_str = status['status']
            if status_str in ['EXITOSA', 'SUCCESS']:
                duration = status.get('duration_seconds', 0)
                status_display = 'EXITOSA' if status_str == 'SUCCESS' else status_str
                report += f"  [{status_display:8}] {phase:40} ({duration:.2f}s)\n"
            else:
                error = status.get('error', 'Error desconocido')
                status_display = 'FALLIDA' if status_str == 'FAILED' else status_str
                report += f"  [{status_display:8}] {phase:40} - {error}\n"
        
        if self.execution_log['errors']:
            report += "\nERRORES ENCONTRADOS:\n"
            report += "-" * 100 + "\n"
            for error in self.execution_log['errors']:
                report += f"  Fase: {error['phase']}\n"
                report += f"  Error: {error['error']}\n\n"
        else:
            report += "\n¡SIN ERRORES - ¡PIPELINE EJECUTADO EXITOSAMENTEs!\n"
        
        report += "=" * 100 + "\n"
        
        return report
    
    def finalize(self) -> None:
        """Finaliza la ejecución del pipeline."""
        report = self.generate_summary_report()
        
        logger.info(report)
        
        # Guarda informe
        report_path = OUTPUTS_DIR / "pipeline_execution_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"\nInforme de ejecución guardado: {report_path}")
        
        # Guarda registro de ejecución como JSON
        import json
        self.execution_log['end_time'] = datetime.now().isoformat()
        log_path = OUTPUTS_DIR / "pipeline_execution_log.json"
        with open(log_path, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
        
        logger.info(f"Registro de ejecución guardado: {log_path}\n")


def main():
    """Punto de entrada principal para el pipeline."""
    pipeline = MasterPipeline()
    
    try:
        # Ejecuta pipeline completo
        pipeline.execute_pipeline()
        
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrumpido por el usuario")
        
    except Exception as e:
        logger.error(f"Error fatal en pipeline: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # Finaliza y genera informes
        pipeline.finalize()


if __name__ == "__main__":
    main()
