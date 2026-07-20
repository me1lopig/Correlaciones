# Consulta de propiedades de suelos

Aplicación Streamlit para consultar parámetros geotécnicos del terreno,
tabulados **por fuente**. Cada documento (norma, manual o proyecto) tiene su
propia pestaña; el usuario elige el documento aplicable. Los valores de
distintas fuentes **no se comparan ni se mezclan**.

## Estructura

```
soil_app/
├── app.py                    Interfaz Streamlit (una pestaña por fuente)
├── soil_params_engine.py     Motor: carga YAML, formatea, sirve DataFrames
├── build_data.py             Genera los YAML desde el Excel original
├── data/                     Una fuente por archivo (fuente de la verdad)
│   ├── grundbau_taschenbuch.yaml
│   ├── eau_1970.yaml
│   ├── navfac_1971.yaml
│   ├── metrosur_1999.yaml
│   ├── cte_densidades.yaml
│   ├── cte_prop_basicas.yaml
│   └── cte_permeabilidad.yaml
├── tests/test_engine.py      Tests de contrato (pytest)
└── requirements.txt
```

Arquitectura separada, como el resto de tus herramientas: **datos (YAML) +
motor sin UI + interfaz Streamlit + tests**. El motor no depende de Streamlit,
así que sirve también para notebooks u otras herramientas de cálculo.

## Puesta en marcha

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Modelo de datos (YAML)

Cada fuente es un documento con `meta`, `columnas` y `filas`:

```yaml
meta:
  id: 1
  fuente_id: grundbau_taschenbuch
  nombre: Grundbau-Taschenbuch
  cita: "…"          # ningún valor sin fuente
  nota: "…"
columnas:
  - {campo: gamma_ap, etiqueta: "γ aparente", unidad: "kN/m³", tipo: rango, grupo: "Peso específico"}
filas:
  - {tipo_suelo: Grava, gamma_ap: [16, 19], k: [0.011, 0.21], c: null}
```

Tipos de columna (`tipo`): `text`, `num`, `rango` (`[min, max]`) y `perm`
(permeabilidad en m/s; admite extremos abiertos `[null, 1e-9]` → «< 10⁻⁹»).
Los valores se guardan **nativos** (número, lista o null); el motor los
formatea para mostrar (decimales con coma, notación científica, «—» para vacío).

## Correcciones aplicadas al original

Los **valores numéricos no se alteran**; solo se corrigen unidades mal
rotuladas, se separan los rangos de texto y se sanean erratas.

| Tipo | Original | Corregido |
|------|----------|-----------|
| Unidad | Cohesión NAVFAC `t/m³` | `t/m²` (la cohesión es una tensión) |
| Unidad | Densidades CTE `kN/m²` | `kN/m³` (son pesos específicos) |
| Unidad | Permeabilidad `m/sg` | `m/s` |
| Formato | `800-1.000`, `10^-2 a 10^-5`, `>38`, `0,35` | `[min, max]` / número |
| Vacíos | `--` | `null` (sin dato) |
| Erratas | `Arana`, `especifioco`, `rozamento`, `biuen`, `Mexcla`, `gurpo`… | corregidas |

## Añadir una fuente nueva

1. Crea `data/<fuente_id>.yaml` con la misma estructura (`meta` con `cita`
   obligatoria, `columnas`, `filas`).
2. Asigna un `id` correlativo (define el orden de las pestañas).
3. `pytest -q` para validar integridad, unidades y plausibilidad física.

No hace falta tocar `app.py` ni el motor: ambos descubren las fuentes solas.

## Regenerar los datos desde el Excel

```bash
python build_data.py ruta/a/Tablas_Parametros.xlsx
```

## Tests

```bash
pytest -q
```

Comprueban: toda fuente tiene cita; filas y columnas cuadran; unidades
corregidas (y ninguna errónea residual); valores dentro de rangos físicos
plausibles (γ 8–24 kN/m³, φ 0–50°, k 1e-13–1 m/s…); rangos ordenados; y varios
valores «golden» de transcripción.

## Aviso

Todos los valores son **orientativos** y no sustituyen la caracterización
geotécnica específica de cada emplazamiento mediante ensayos.
