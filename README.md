**Proyecto**
- **Título:** Pipeline Híbrido de Ingesta y Data Wrangling para la Optimización de la Eficiencia Logística y Análisis Comercial en el Sector Retail

**Resumen Ejecutivo**
- **Descripción:** Orquestador end-to-end que consolida fuentes heterogéneas (CSV + JSON), realiza limpieza, deduplicación, imputación y cálculo de KPIs en Python y produce visualizaciones avanzadas en R.
- **Objetivo:** Integrar, limpiar y analizar datos transaccionales para evaluar desempeño logístico y comercial; garantizar reproducibilidad mediante automatización.

**Estructura del Repositorio**
- **Raíz:** [master_pipeline.py](master_pipeline.py) — orquestador principal.
- **Configuración:** [config/config.py](config/config.py)
- **Scripts por fase:** `scripts/` (fases 01–06):
  - [scripts/01_explore_data.py](scripts/01_explore_data.py)
  - [scripts/02_clean_data.py](scripts/02_clean_data.py)
  - [scripts/03_integrate_data.py](scripts/03_integrate_data.py)
  - [scripts/04_generate_analytics.py](scripts/04_generate_analytics.py)
  - [scripts/05_generate_visualizations.py](scripts/05_generate_visualizations.py)
  - [scripts/06_generate_visualizations_r.R](scripts/06_generate_visualizations_r.R)
- **Datos:** `data/raw/`, `data/processed/`, `data/exports/`.
- **Salidas:** `outputs/` (reportes, gráficos, logs) y `outputs/pipeline_execution_log.json`.

**Requisitos**
- **Python:** 3.14.4
- **R:** 4.6.0 (solo para la fase 06)
- **Bibliotecas Python (ejemplos):** pandas, numpy, geopandas, pyproj, matplotlib, seaborn
- **Paquetes R (ejemplos):** dplyr, ggplot2, corrplot, gridExtra

**Instalación (recomendado: entorno virtual)**
- **Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
- **Linux / macOS (bash):**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- **R (instalar paquetes si faltan):**
```r
install.packages(c("dplyr","ggplot2","corrplot","gridExtra"))
```

**Ejecución**
- Ejecución completa del pipeline (orquestador):
```bash
python master_pipeline.py
```
- Si necesita ejecutar fases individualmente, ejecutar el script correspondiente en `scripts/`.
- La fase de visualización avanzada en R se invoca automáticamente desde `master_pipeline.py`; requiere que `Rscript` esté en el PATH.

**Consideraciones sobre los datos**
- Los archivos originales en `data/raw/` pueden ser pesados (varios CSV > 50MB). Para mantener el repositorio ligero se recomienda usar `git lfs` para archivos grandes o excluir `data/raw/` y compartir datos por separado.
- Si prefiere un repositorio sin datos crudos, puede mover `data/raw/` fuera del repo y dejar solo scripts y ejemplos reducidos en `data/processed/`.

**Salidas y artefactos**
- **Logs de ejecución:** `outputs/pipeline_execution_log.json`.
- **Visualizaciones:** gráficos generados por Python y R guardados en `outputs/visualizations/`.

**Calidad y Validación**
- El pipeline registra tiempos y excepciones; en caso de fallo la fase queda registrada en el log para auditoría.
- Se aplican operaciones de deduplicación, IQR para outliers e imputación selectiva para preservar trazabilidad.

**Resultados clave (resumen)**
- **Registros procesados:** 1,550,922 registros consolidados en 9 fuentes.
- **Órdenes únicas finales:** 99,441
- **Tiempo total de ejecución (ejemplo):** ~151.25 segundos (ingesta → visualización)
- **KPIs destacados:** tiempo medio de entrega ≈ 13.8 días; satisfacción media ≈ 4.09/5; ingresos totales ≈ 9.3M BRL.

**Contribuyentes:** Miguel Ángel Caballero Lynch, Ruben Osamu Tsukazan Nakaima, Willy Laurence Torres Bojorquez, Hugo Junior Valverde Chumbe, Rosmery Isabel Luna Tito, Saúl Yonathan López Huamán

**Recomendaciones y siguientes pasos**
- **Monitoreo:** implementar alarmas para retrasos extremos y anomalías.
- **Enriquecimiento:** incorporar datos externos (económicos/logísticos).
- **Despliegue liviano:** usar `git lfs` o excluir `data/raw/` antes de publicar código público.
- **Interfaz:** desarrollar un tablero interactivo para usuarios ejecutivos.
