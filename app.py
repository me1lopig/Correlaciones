import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import re

matplotlib.rcParams["font.family"] = "DejaVu Sans"

st.set_page_config(
    page_title="GeoLab Viewer",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
.main-title {font-size:2rem; font-weight:800; color:#1a252f; margin-bottom:0.2rem;}
.sub-title  {font-size:1rem; color:#5d6d7e; margin-bottom:1rem;}
.section-header {font-size:1.15rem; font-weight:700; color:#2471a3;
                 border-left:4px solid #2471a3; padding-left:8px; margin:1.2rem 0 0.6rem 0;}
.kpi-box {background:#d6e4f0; border-radius:10px; padding:14px 10px;
          text-align:center; margin:4px;}
.kpi-val {font-size:1.8rem; font-weight:800; color:#1a252f;}
.kpi-lbl {font-size:0.78rem; color:#5d6d7e; margin-top:2px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def to_float(x):
    if pd.isna(x): return np.nan
    try:
        return float(str(x).replace(",", ".").strip())
    except:
        return np.nan

def clean_col(s):
    return s.apply(to_float)

def prospect_from_sample(name):
    if pd.isna(name): return "Desconocido"
    name = str(name).strip()
    m = re.match(r"([A-Za-z]+[-_]?\d+)", name)
    if m: return m.group(1)
    return name.split()[0] if name.split() else name

def prospect_colors(label_series):
    prospects = sorted(label_series.apply(prospect_from_sample).unique())
    palette = plt.cm.get_cmap("tab20", max(len(prospects), 1))
    return {p: matplotlib.colors.to_hex(palette(i)) for i, p in enumerate(prospects)}

def stats_metrics(s):
    s2 = pd.to_numeric(s, errors="coerce").dropna()
    if len(s2) == 0: return {}
    q1, q3 = s2.quantile(0.25), s2.quantile(0.75)
    iqr = q3 - q1
    outliers = int(((s2 < q1 - 1.5*iqr) | (s2 > q3 + 1.5*iqr)).sum())
    cv = round(s2.std() / s2.mean() * 100, 1) if s2.mean() != 0 else np.nan
    return {"N": int(len(s2)), "Media": round(s2.mean(),3), "Mediana": round(s2.median(),3),
            "Desv.Tip": round(s2.std(),3), "Min": round(s2.min(),3), "Max": round(s2.max(),3),
            "CV(%)": cv, "Atipicos": outliers}



def load_and_clean(file):
    # KEY FIX: header=0 because row 0 IS the header (not row 1 or 2)
    df = pd.read_excel(file, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    text_cols = {
        "Unidad geotecnica","Descripcion Muestra","Descripcion Muestra.1",
        "Descripcion Muestra.2","Ensayo geotecnia","Ensayo geotecnia.1",
        "Ensayo geotecnia.2","Clasificacion USCS","Tipo Ensayo con drenaje",
        "Tipo Ensayo sin drenaje","Tipo Proctor","Calificacion","COL",
        # include accented versions too
        "Unidad geot\u00e9cnica",
        "Descripci\u00f3n Muestra","Descripci\u00f3n Muestra.1","Descripci\u00f3n Muestra.2",
        "Clasificaci\u00f3n USCS",
        "\u00c1ngulo de Rozamiento con denaje","\u00c1ngulo de Rozamiento sin denaje",
        "Calificaci\u00f3n",
    }
    for c in df.columns:
        if c not in text_cols:
            df[c] = clean_col(df[c])
    return df

COLS_SPT  = ["Unidad geot\u00e9cnica","Descripci\u00f3n Muestra","Ensayo geotecnia",
             "Profundidad inicial","ISPT_INC1","ISPT_INC2","ISPT_INC3","ISPT_INC4",
             "SPT (valores centrales)","MI (valores centrales)"]
COLS_GRAN = ["Descripci\u00f3n Muestra","Ensayo geotecnia","Profundidad inicial",
             "20","5","2","0.4","0.08",
             "Tamiz Grava","Tamiz Arena","Tamiz Finos","LL","LP","IP","Clasificaci\u00f3n USCS"]
COLS_ATTER= ["Descripci\u00f3n Muestra","Profundidad inicial","LL","LP","IP","Clasificaci\u00f3n USCS"]
COLS_QUIM = ["Descripci\u00f3n Muestra","Profundidad inicial","MO","SU",
             "Sulfatos (mg/kg de suelo) Media.",
             "Grado acidez (ml/kg de suelo seco) Medio","YE","SS","% CO3CA"]
COLS_MEC  = ["Descripci\u00f3n Muestra.1","Ensayo geotecnia.1","Profundidad inicial.1",
             "Peso espec\u00edfico","Densidad Seca Kn/m3","Densidad H\u00fameda KN/m3","Humedad",
             "RCS (kpa)","Tipo Ensayo con drenaje",
             "\u00c1ngulo de Rozamiento con denaje","Cohesi\u00f3n KPa con drenaje",
             "Tipo Ensayo sin drenaje",
             "\u00c1ngulo de Rozamiento sin denaje","Cohesi\u00f3n KPa sin drenaje"]
COLS_CON  = ["Descripci\u00f3n Muestra.2","Ensayo geotecnia.2","Profundidad inicial.2",
             "Indice de Poros","Presi\u00f3n de Preconsolidaci\u00f3n (kPa)","Presi\u00f3n Hinchamiento",
             "HL","Calificaci\u00f3n","COL","Tipo Proctor","\u03c1 KN","W","CBR","CBR 95%"]

def _sub(df, cols):
    available = [c for c in cols if c in df.columns]
    return df[available].copy() if available else pd.DataFrame()

def get_spt(df):    return _sub(df, COLS_SPT)
def get_gran(df):   return _sub(df, COLS_GRAN)
def get_atter(df):  return _sub(df, COLS_ATTER)
def get_mec(df):    return _sub(df, COLS_MEC)
def get_consol(df): return _sub(df, COLS_CON)
def get_quim(df):   return _sub(df, COLS_QUIM)



def boxplot_panel(data_dict, title, ncols=3):
    valid = {k: pd.to_numeric(v, errors="coerce").dropna()
             for k, v in data_dict.items()}
    valid = {k: v for k, v in valid.items() if len(v) > 0}
    if not valid: return None
    n = len(valid)
    ncols = min(ncols, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5*ncols, 3.8*nrows))
    fig.suptitle(title, fontsize=13, fontweight="bold", color="#1a252f", y=1.01)
    axes = np.array(axes).flatten()
    for i, (lbl, s) in enumerate(valid.items()):
        ax = axes[i]
        ax.boxplot(s.values, patch_artist=True, widths=0.45,
                   medianprops=dict(color="#e74c3c", linewidth=2.5),
                   boxprops=dict(facecolor="#d6e4f0", color="#2471a3"),
                   whiskerprops=dict(color="#2471a3", linewidth=1.5),
                   capprops=dict(color="#2471a3", linewidth=1.5),
                   flierprops=dict(marker="o", color="#e74c3c",
                                   markerfacecolor="#e74c3c", markersize=6, alpha=0.8))
        ax.set_title(lbl, fontsize=9.5, fontweight="bold", color="#1a252f")
        ax.set_xticks([])
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        m = stats_metrics(s)
        info = ("N=" + str(m["N"]) + "  Med=" + str(m["Mediana"]) +
                "\nMedia=" + str(m["Media"]) + "  DS=" + str(m["Desv.Tip"]) +
                "\nCV=" + str(m["CV(%)"]) + "%  Atip=" + str(m["Atipicos"]))
        ax.set_xlabel(info, fontsize=7.5, color="#5d6d7e")
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)
    plt.tight_layout()
    return fig

def depth_profile(df_sub, value_col, label_col, depth_col, title, xlabel, invert_y=True):
    sub = df_sub[[label_col, depth_col, value_col]].copy()
    sub[value_col] = pd.to_numeric(sub[value_col], errors="coerce")
    sub[depth_col] = pd.to_numeric(sub[depth_col], errors="coerce")
    sub = sub.dropna(subset=[value_col, depth_col])
    if sub.empty: return None
    sub["_prospect"] = sub[label_col].apply(prospect_from_sample)
    cmap = prospect_colors(sub[label_col])
    fig, ax = plt.subplots(figsize=(5, 7))
    for pname, grp in sub.groupby("_prospect"):
        col = cmap.get(pname, "#2471a3")
        ax.scatter(grp[value_col], grp[depth_col], color=col, s=55, label=pname,
                   zorder=4, edgecolors="white", linewidths=0.5)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel("Profundidad (m)", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold", color="#1a252f")
    if invert_y: ax.invert_yaxis()
    ax.grid(linestyle="--", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=7.5, title="Prospeccion", title_fontsize=8, loc="best", framealpha=0.7)
    plt.tight_layout()
    return fig

def show_stats_table(series_dict):
    rows = []
    for lbl, s in series_dict.items():
        m = stats_metrics(s)
        if m:
            m["Parametro"] = lbl
            rows.append(m)
    if rows:
        tdf = pd.DataFrame(rows).set_index("Parametro")
        float_cols = [c for c in tdf.columns if c not in ["N","Atipicos"]]
        st.dataframe(
            tdf.style
               .format("{:.3f}", subset=float_cols)
               .background_gradient(subset=["CV(%)"], cmap="YlOrRd"),
            use_container_width=True)



def kpi_box(val, label):
    st.markdown(
        '<div class="kpi-box"><div class="kpi-val">' + str(val) +
        '</div><div class="kpi-lbl">' + label + '</div></div>',
        unsafe_allow_html=True)

def sidebar_upload():
    st.sidebar.markdown("## 🪨 GeoLab Viewer")
    st.sidebar.markdown("---")
    f = st.sidebar.file_uploader(
        "Cargar archivo Excel", type=["xlsx","xls"],
        help="Sube el listado de ensayos de laboratorio")
    return f

def page_overview(df):
    st.markdown('<div class="main-title">🪨 GeoLab Viewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Resumen General del Proyecto</div>', unsafe_allow_html=True)

    spt_col   = "SPT (valores centrales)"
    mi_col    = "MI (valores centrales)"
    grava_col = "Tamiz Grava"
    ll_col    = "LL"
    dens_col  = "Densidad Seca Kn/m3"
    cbr_col   = "CBR"

    def _count(col):
        if col not in df.columns: return 0
        return int(df[col].notna().sum())

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi_box(len(df), "Registros totales")
    with c2: kpi_box(_count(spt_col) + _count(mi_col), "SPT / MI")
    with c3: kpi_box(_count(grava_col), "Granulometrías")
    with c4: kpi_box(_count(ll_col), "Atterberg")
    with c5: kpi_box(_count(dens_col), "Mecánicos")
    with c6: kpi_box(_count(cbr_col), "Consol/CBR")

    st.markdown('<div class="section-header">Perfiles por Profundidad</div>', unsafe_allow_html=True)
    cols_row = st.columns(3)

    profiles = [
        (spt_col, "Descripción Muestra", "Profundidad inicial",
         "SPT vs Profundidad", "N SPT"),
        (mi_col, "Descripción Muestra", "Profundidad inicial",
         "MI vs Profundidad", "N MI"),
        (grava_col, "Descripción Muestra", "Profundidad inicial",
         "Grava (%) vs Profundidad", "Grava (%)"),
        ("Tamiz Arena", "Descripción Muestra", "Profundidad inicial",
         "Arena (%) vs Profundidad", "Arena (%)"),
        (ll_col, "Descripción Muestra", "Profundidad inicial",
         "LL vs Profundidad", "LL (%)"),
        (dens_col, "Descripción Muestra.1", "Profundidad inicial.1",
         "Densidad Seca vs Profundidad", "Dens. Seca (kN/m\u00b3)"),
    ]

    for idx, (vcol, lcol, dcol, title, xlabel) in enumerate(profiles):
        if vcol not in df.columns or lcol not in df.columns or dcol not in df.columns:
            with cols_row[idx % 3]:
                st.warning("Sin columna: " + vcol)
            continue
        fig = depth_profile(df, vcol, lcol, dcol, title, xlabel)
        with cols_row[idx % 3]:
            if fig:
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Sin datos para: " + title)



def _generic_page(df, title, getter_fn, num_cols, depth_col_name,
                  sample_col_name, profile_pairs, units=None):
    st.markdown('<div class="main-title">' + title + '</div>', unsafe_allow_html=True)
    sub = getter_fn(df)
    if sub.empty or sub.shape[0] == 0:
        st.warning("No hay datos disponibles para este tipo de ensayo.")
        return

    # Filter by prospection
    sub["_prospect"] = sub[sample_col_name].apply(prospect_from_sample)
    prospects = sorted(sub["_prospect"].unique())
    sel = st.sidebar.multiselect("Filtrar prospección", prospects, default=prospects,
                                  key=title + "_filter")
    if sel:
        sub = sub[sub["_prospect"].isin(sel)]

    if sub.empty:
        st.warning("Sin datos tras el filtro seleccionado.")
        return

    # Stats table
    st.markdown('<div class="section-header">Estadísticos</div>', unsafe_allow_html=True)
    num_data = {c: sub[c] for c in num_cols if c in sub.columns}
    show_stats_table(num_data)

    # Box plots
    st.markdown('<div class="section-header">Diagramas de Caja</div>', unsafe_allow_html=True)
    fig = boxplot_panel(num_data, title)
    if fig:
        st.pyplot(fig); plt.close(fig)

    # Depth profiles
    st.markdown('<div class="section-header">Perfiles con Profundidad</div>', unsafe_allow_html=True)
    pcols = st.columns(min(len(profile_pairs), 3))
    for i, (vcol, lbl) in enumerate(profile_pairs):
        if vcol not in sub.columns or depth_col_name not in sub.columns:
            continue
        fig = depth_profile(sub, vcol, sample_col_name, depth_col_name, lbl, lbl)
        with pcols[i % 3]:
            if fig: st.pyplot(fig); plt.close(fig)
            else: st.info("Sin datos: " + lbl)

    # Raw data
    with st.expander("Ver datos completos"):
        disp = sub.drop(columns=["_prospect"], errors="ignore")
        st.dataframe(disp, use_container_width=True)

def page_spt(df):
    _generic_page(df, "SPT / MI",
        get_spt,
        ["ISPT_INC1","ISPT_INC2","ISPT_INC3","ISPT_INC4",
         "SPT (valores centrales)","MI (valores centrales)"],
        "Profundidad inicial", "Descripción Muestra",
        [("SPT (valores centrales)","SPT"),
         ("MI (valores centrales)","MI"),
         ("ISPT_INC3","Inc3")])

def page_gran(df):
    _generic_page(df, "Granulometría",
        get_gran,
        ["Tamiz Grava","Tamiz Arena","Tamiz Finos","LL","LP","IP"],
        "Profundidad inicial", "Descripción Muestra",
        [("Tamiz Grava","Grava (%)"),
         ("Tamiz Arena","Arena (%)"),
         ("Tamiz Finos","Finos (%)")])

def page_atter(df):
    _generic_page(df, "Límites de Atterberg",
        get_atter,
        ["LL","LP","IP"],
        "Profundidad inicial", "Descripción Muestra",
        [("LL","Límite Líquido"),
         ("LP","Límite Plástico"),
         ("IP","Índice de Plasticidad")])

def page_mec(df):
    _generic_page(df, "Parámetros Mecánicos",
        get_mec,
        ["Densidad Seca Kn/m3","Densidad Húmeda KN/m3","Humedad",
         "RCS (kpa)","Ángulo de Rozamiento con denaje","Cohesión KPa con drenaje",
         "Ángulo de Rozamiento sin denaje","Cohesión KPa sin drenaje"],
        "Profundidad inicial.1", "Descripción Muestra.1",
        [("Densidad Seca Kn/m3","Dens. Seca"),
         ("Ángulo de Rozamiento con denaje","Ang CD"),
         ("Cohesión KPa con drenaje","Coh CD")])

def page_consol(df):
    _generic_page(df, "Consolidación / CBR / Proctor",
        get_consol,
        ["Indice de Poros","Presión de Preconsolidación (kPa)",
         "Presión Hinchamiento","HL","CBR","CBR 95%","ρ KN","W"],
        "Profundidad inicial.2", "Descripción Muestra.2",
        [("CBR","CBR"),("CBR 95%","CBR 95%"),
         ("Indice de Poros","Indice de Poros")])

def page_quim(df):
    _generic_page(df, "Ensayos Químicos",
        get_quim,
        ["MO","SU","Sulfatos (mg/kg de suelo) Media.",
         "Grado acidez (ml/kg de suelo seco) Medio","YE","SS","% CO3CA"],
        "Profundidad inicial", "Descripción Muestra",
        [("Sulfatos (mg/kg de suelo) Media.","Sulfatos"),
         ("MO","MO"),("% CO3CA","CO3Ca")])



# ─────────────────────────── MAIN ────────────────────────────────
file = sidebar_upload()

if file is None:
    st.markdown('<div class="main-title">🪨 GeoLab Viewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Sube el archivo Excel para comenzar</div>',
                unsafe_allow_html=True)
    st.info("Usa el panel izquierdo para cargar el listado de ensayos de laboratorio.")
    st.stop()

df = load_and_clean(file)

pages = {
    "📊 Resumen General":   page_overview,
    "💥 SPT / MI":          page_spt,
    "🧪 Granulometría": page_gran,
    "📐 Atterberg":         page_atter,
    "🔧 Mecánicos":    page_mec,
    "📈 Consol / CBR":      page_consol,
    "⚗️ Químicos":   page_quim,
}

choice = st.sidebar.radio("Navegación", list(pages.keys()))
pages[choice](df)
