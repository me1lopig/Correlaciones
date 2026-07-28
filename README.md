# Correlaciones Geotécnicas

Herramienta integral para el análisis y cálculo de correlaciones en geotecnia. Este repositorio contiene múltiples aplicaciones Streamlit diseñadas para facilitar el trabajo con parámetros del suelo, ensayos de laboratorio y correlaciones empíricas comúnmente utilizadas en ingeniería geotécnica.

## 📌 Aplicaciones Disponibles

### 🔍 GeoLab Viewer (`app.py`)
Aplicación principal para la visualización y análisis de ensayos de laboratorio. Permite:
- Cargar archivos Excel con datos de ensayos
- Visualizar resúmenes generales del proyecto
- Analizar datos por tipo de ensayo: SPT/MI, granulometría, límites de Atterberg, parámetros mecánicos, consolidación/CBR, y ensayos químicos
- Generar gráficos de perfiles por profundidad y diagramas de caja
- Filtrar datos por prospección

### 📊 Corrección de Ensayos SPT (`spt_corregido.py`)
Calcula el valor corregido **$(N_1)_{60}$** basado en las recomendaciones de:
- Skempton (1986)
- Youd et al. (2001)

Incluye configuración del equipo (tipo de martillo, eficiencia, diámetro del sondeo, longitud del varillaje) y correcciones automáticas.

### 🏗️ Ángulo de Rozamiento (`angulo_rozamiento_streamlit.py`)
Calcula el ángulo de rozamiento (φ) a partir de:
- Índice plástico (IP)
- Número de golpes SPT (N_spt)

Implementa múltiples correlaciones:
- Jiménez Salas y Justo Alpañes
- Peck
- Muromachi (1974)
- Terzaghi & Peck (1948)
- Kishida (1969)

Genera informes detallados en formato Word con los resultados.

### 📈 Módulo de Elasticidad
- **Arenas** (`modulo_elasticidad_arenas.py` y `modulo_elasticidad_arenas_2.py`): Cálculo del módulo de elasticidad para suelos arenosos
- **Arcillas** (`modulo_elasticidad_arcillas.py`): Cálculo del módulo de elasticidad para suelos arcillosos

### 📉 Índice de Compresión (`Cc_streamlit_*.py`)
Múltiples versiones para el cálculo del índice de compresión (Cc) en suelos cohesivos.

### 📚 Consulta de Propiedades de Suelos (`Tablas/`)
Aplicación independiente para consultar parámetros geotécnicos del terreno organizados por fuente:
- Grundbau-Taschenbuch
- EAU 1970
- NAVFAC 1971
- Metrosur 1999
- CTE (Código Técnico de la Edificación): densidades, propiedades básicas, permeabilidad

Cada documento tiene su propia pestaña y los valores de distintas fuentes no se mezclan.

## 🛠️ Requisitos

```bash
pip install -r requirements.txt
```

Dependencias principales:
- streamlit
- pandas
- numpy
- matplotlib
- python-docx

## 🚀 Ejecución

Para ejecutar cualquier aplicación Streamlit:

```bash
streamlit run <nombre_archivo>.py
```

Ejemplos:
```bash
streamlit run app.py                    # GeoLab Viewer
streamlit run spt_corregido.py          # Corrección SPT
streamlit run angulo_rozamiento_streamlit.py  # Ángulo de rozamiento
```

Para la aplicación de tablas:
```bash
cd Tablas
streamlit run app.py
```

## 📁 Estructura del Proyecto

```
Correlaciones/
├── app.py                          # GeoLab Viewer
├── spt_corregido.py                # Corrección SPT
├── angulo_rozamiento_streamlit.py  # Ángulo de rozamiento
├── modulo_elasticidad_arcillas.py   # Módulo elasticidad arcillas
├── modulo_elasticidad_arenas.py     # Módulo elasticidad arenas
├── modulo_elasticidad_arenas_2.py   # Versión alternativa
├── Cc_streamlit_*.py               # Índice de compresión
├── main.py                         # Interfaz Tkinter para tablas
├── listadoLab.py                   # Listado de laboratorio
├── requirements.txt
├── Tablas/                         # Aplicación de consulta de propiedades
│   ├── app.py                      # Interfaz Streamlit
│   ├── soil_params_engine.py       # Motor de datos
│   ├── build_data.py               # Generador de datos YAML
│   ├── data/                       # Datos en formato YAML
│   │   ├── grundbau_taschenbuch.yaml
│   │   ├── eau_1970.yaml
│   │   ├── navfac_1971.yaml
│   │   ├── metrosur_1999.yaml
│   │   ├── cte_densidades.yaml
│   │   ├── cte_prop_basicas.yaml
│   │   └── cte_permeabilidad.yaml
│   └── tests/                      # Pruebas unitarias
└── Resources/                      # Recursos (archivos Excel de referencia)
```

## 📝 Notas

- Todas las aplicaciones están desarrolladas en Python usando Streamlit como framework principal
- Los valores calculados son **orientativos** y no sustituyen la caracterización geotécnica específica de cada emplazamiento mediante ensayos
- El proyecto sigue una arquitectura modular: datos + motor + interfaz + tests

## 📄 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0** - ver el archivo [LICENSE](LICENSE) para más detalles.
