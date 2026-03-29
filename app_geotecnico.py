import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import io
import re

matplotlib.rcParams["font.family"] = "DejaVu Sans"

st.set_page_config(
    page_title="GeoLab Viewer",
    page_icon="\U0001faa8",
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

# ---------- helpers ----------
def to_float(x):
    if pd.isna(x): return np.nan
    try: return float(str(x).replace(",",".").strip())
    except: return np.nan

def clean_col(s):
    return s.apply(to_float)

def prospect_from_sample(name):
    if pd.isna(name): return "Desconocido"
    name = str(name).strip()
    m = re.match(r"([A-Za-z]+[-_]?\d+)", name)
    if m: return m.group(1)
    return name.split()[0] if name.split() else name

def prospect_colors(label_series):
    prospects = label_series.apply(prospect_from_sample).unique()
    palette = plt.cm.get_cmap("tab20", max(len(prospects),1))
    return {p: matplotlib.colors.to_hex(palette(i)) for i,p in enumerate(sorted(prospects))}

def stats_metrics(s):
    s2 = pd.to_numeric(s, errors="coerce").dropna()
    if len(s2) == 0: return {}
    q1,q3 = s2.quantile(0.25), s2.quantile(0.75)
    iqr = q3 - q1
    outliers = int(((s2 < q1-1.5*iqr) | (s2 > q3+1.5*iqr)).sum())
    cv = round(s2.std()/s2.mean()*100, 1) if s2.mean() != 0 else np.nan
    return {
        "N": int(len(s2)),
        "Media": round(s2.mean(),3),
        "Mediana": round(s2.median(),3),
        "Desv.Tip": round(s2.std(),3),
        "Min": round(s2.min(),3),
        "Max": round(s2.max(),3),
        "CV(%)": cv,
        "Atipicos": outliers
    }

# ---------- load ----------
def load_and_clean(file):
    df = pd.read_excel(file, header=1)
    df.columns = [str(c).strip() for c in df.columns]
    return df


# ---------- data getters ----------
COLS_SPT  = ["Unidad geotécnica","Descripción Muestra","Ensayo geotecnia","Profundidad inicial",
             "ISPT_INC1","ISPT_INC2","ISPT_INC3","ISPT_INC4",
             "SPT (valores centrales)","MI (valores centrales)"]

COLS_GRAN = ["Descripción Muestra","Ensayo geotecnia","Profundidad inicial",
             "20","5","2","0.4","0.08",
             "Tamiz Grava","Tamiz Arena","Tamiz Finos",
             "LL","LP","IP","Clasificación USCS"]

COLS_ATTER = ["Descripción Muestra","Profundidad inicial","LL","LP","IP","Clasificación USCS"]

COLS_QUIM = ["Descripción Muestra","Profundidad inicial",
             "MO","SU","Sulfatos (mg/kg de suelo) Media.",
             "Grado acidez (ml/kg de suelo seco) Medio","YE","SS","% CO3CA"]

COLS_MEC  = ["Descripción Muestra.1","Ensayo geotecnia.1","Profundidad inicial.1",
             "Peso específico","Densidad Seca Kn/m3","Densidad Húmeda KN/m3","Humedad",
             "RCS (kpa)","Tipo Ensayo con drenaje","Ángulo de Rozamiento con denaje",
             "Cohesión KPa con drenaje","Tipo Ensayo sin drenaje",
             "Ángulo de Rozamiento sin denaje","Cohesión KPa sin drenaje"]

COLS_CON  = ["Descripción Muestra.2","Ensayo geotecnia.2","Profundidad inicial.2",
             "Indice de Poros","Presión de Preconsolidación (kPa)","Presión Hinchamiento",
             "HL","Calificación","COL","Tipo Proctor","ρ KN","W","CBR","CBR 95%"]

def _sub(df, cols):
    available = [c for c in cols if c in df.columns]
    if not available: return pd.DataFrame()
    sub = df[available].copy()
    num_cols = [c for c in available if c not in
                ["Unidad geotécnica","Descripción Muestra","Descripción Muestra.1",
                 "Descripción Muestra.2","Ensayo geotecnia","Ensayo geotecnia.1",
                 "Ensayo geotecnia.2","Clasificación USCS","Tipo Ensayo con drenaje",
                 "Tipo Ensayo sin drenaje","Tipo Proctor","Calificación","COL"]]
    for c in num_cols:
        sub[c] = clean_col(sub[c])
    return sub

def get_spt(df):   return _sub(df, COLS_SPT)
def get_gran(df):  return _sub(df, COLS_GRAN)
def get_atter(df): return _sub(df, COLS_ATTER)
def get_mec(df):   return _sub(df, COLS_MEC)
def get_consol(df):return _sub(df, COLS_CON)
def get_quim(df):  return _sub(df, COLS_QUIM)


# ---------- plotting helpers ----------
def boxplot_panel(data_dict, title, units_dict=None, ncols=3):
    valid = {k: pd.to_numeric(v, errors="coerce").dropna() for k,v in data_dict.items()}
    valid = {k:v for k,v in valid.items() if len(v)>0}
    if not valid: return None
    n = len(valid)
    ncols = min(ncols, n)
    nrows = int(np.ceil(n/ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5*ncols, 3.8*nrows))
    fig.suptitle(title, fontsize=13, fontweight="bold", color="#1a252f", y=1.01)
    axes = np.array(axes).flatten()
    for i,(lbl,s) in enumerate(valid.items()):
        ax = axes[i]
        ax.boxplot(s.values, patch_artist=True, widths=0.45,
                   medianprops=dict(color="#e74c3c",linewidth=2.5),
                   boxprops=dict(facecolor="#d6e4f0",color="#2471a3"),
                   whiskerprops=dict(color="#2471a3",linewidth=1.5),
                   capprops=dict(color="#2471a3",linewidth=1.5),
                   flierprops=dict(marker="o",color="#e74c3c",markerfacecolor="#e74c3c",markersize=6,alpha=0.8))
        q1,q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3-q1
        unit = (units_dict or {}).get(lbl,"")
        ax.set_title(lbl + (" ("+unit+")" if unit else ""), fontsize=9.5, fontweight="bold", color="#1a252f")
        ax.set_xticks([])
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        stats = stats_metrics(s)
        info = ("N="+str(stats["N"])+"  Med="+str(stats["Mediana"])+
                "\nMedia="+str(stats["Media"])+"  DS="+str(stats["Desv.Tip"])+
                "\nCV="+str(stats["CV(%)"])+"%  Atip="+str(stats["Atipicos"]))
        ax.set_xlabel(info, fontsize=7.5, color="#5d6d7e")
    for j in range(i+1, len(axes)): axes[j].set_visible(False)
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
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(fontsize=7.5, title="Prospección", title_fontsize=8, loc="best", framealpha=0.7)
    plt.tight_layout()
    return fig

def show_stats_table(series_dict, units_dict=None):
    rows = []
    for lbl, s in series_dict.items():
        m = stats_metrics(s)
        if m:
            m["Parámetro"] = lbl + (" ("+units_dict.get(lbl,"")+")" if units_dict and units_dict.get(lbl,"") else "")
            rows.append(m)
    if rows:
        tdf = pd.DataFrame(rows).set_index("Parámetro")
        non_int = [c for c in tdf.columns if c not in ["N","Atipicos"]]
        st.dataframe(
            tdf.style
               .format("{:.3f}", subset=non_int)
               .background_gradient(subset=["CV(%)"], cmap="YlOrRd")
               .background_gradient(subset=["Atipicos"], cmap="Oranges"),
            use_container_width=True)


# ---------- sidebar ----------
def sidebar_upload():
    st.sidebar.markdown("<div class=\"main-title\">\U0001faa8 GeoLab</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class=\"sub-title\">Visor de Ensayos Geotecnicos</div>", unsafe_allow_html=True)
    uploaded = st.sidebar.file_uploader("Cargar archivo Excel", type=["xlsx","xls"])
    return uploaded

# ---------- overview page ----------
def page_overview(df):
    st.markdown("<div class=\"main-title\">\U0001f4ca Resumen General</div>", unsafe_allow_html=True)
    spt  = get_spt(df)
    gran = get_gran(df)
    att  = get_atter(df)
    mec  = get_mec(df)
    con  = get_consol(df)
    quim = get_quim(df)

    def _n(sub, cols):
        available = [c for c in cols if c in sub.columns]
        if not available: return 0
        return int(sub[available].dropna(how="all").shape[0])

    kpis = [
        ("Registros totales", len(df)),
        ("SPT / MI", _n(spt, ["SPT (valores centrales)","MI (valores centrales)"])),
        ("Granulometrías", _n(gran, ["Tamiz Grava","Tamiz Arena","Tamiz Finos"])),
        ("Atterberg", _n(att, ["LL","LP","IP"])),
        ("Mecánicos", _n(mec, ["Densidad Seca Kn/m3","RCS (kpa)"])),
        ("Consol/CBR", _n(con, ["Indice de Poros","CBR"])),
        ("Químicos", _n(quim, ["MO","SU"])),
    ]
    cols = st.columns(len(kpis))
    for c, (lbl,val) in zip(cols, kpis):
        c.markdown("<div class=\"kpi-box\"><div class=\"kpi-val\">" + str(val) + "</div><div class=\"kpi-lbl\">" + lbl + "</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    def _prof_row(title, sub, params, desc_col, prof_col):
        visible = [(p,xl) for p,xl in params if p in sub.columns and not sub[[p]].dropna().empty]
        if not visible:
            st.info("Sin datos para: " + title)
            return
        st.markdown("<div class=\"section-header\">" + title + "</div>", unsafe_allow_html=True)
        n = min(3, len(visible))
        pcols = st.columns(n)
        for i,(param,xl) in enumerate(visible):
            s2 = sub[[desc_col, prof_col, param]].dropna()
            fig = depth_profile(s2, param, desc_col, prof_col, param+" vs Prof.", xl)
            if fig:
                pcols[i % n].pyplot(fig)
                plt.close(fig)

    _prof_row("SPT / MI vs Profundidad", spt,
        [("SPT (valores centrales)","N SPT"),("MI (valores centrales)","qd (MPa)")],
        "Descripción Muestra", "Profundidad inicial")

    _prof_row("Granulometría - Fracciones", gran,
        [("Tamiz Grava","% Grava"),("Tamiz Arena","% Arena"),("Tamiz Finos","% Finos")],
        "Descripción Muestra", "Profundidad inicial")

    _prof_row("Límites de Atterberg", att,
        [("LL","LL (%)"),("LP","LP (%)"),("IP","IP (%)")],
        "Descripción Muestra", "Profundidad inicial")

    _prof_row("Propiedades Mecánicas", mec,
        [("Densidad Seca Kn/m3","Den.Seca kN/m3"),("Humedad","Humedad %"),("RCS (kpa)","RCS kPa"),
         ("Ángulo de Rozamiento con denaje","Phi CD"),("Cohesión KPa con drenaje","c CD kPa")],
        "Descripción Muestra.1", "Profundidad inicial.1")

    _prof_row("Consolidación / Proctor / CBR", con,
        [("Indice de Poros","e"),("CBR","CBR %"),("ρ KN","rho Proctor kN")],
        "Descripción Muestra.2", "Profundidad inicial.2")

    _prof_row("Química del Suelo", quim,
        [("MO","MO %"),("SU","Sulfatos SO4"),("% CO3CA","CO3Ca %")],
        "Descripción Muestra", "Profundidad inicial")


# ---------- individual pages ----------
def _page_generic(df, title, icon, data_fn, filter_col, desc_col, prof_col,
                  params, box_title, page_key):
    st.markdown("<div class=\"main-title\">" + icon + " " + title + "</div>", unsafe_allow_html=True)
    sub = data_fn(df)
    if sub.empty:
        st.info("Sin datos para este ensayo.")
        return
    sub["_prospect"] = sub[filter_col].apply(prospect_from_sample)
    prospects = sorted(sub["_prospect"].dropna().unique())
    sel = st.multiselect("Filtrar por prospección:", prospects, default=prospects, key=page_key+"_sel")
    sub_f = sub[sub["_prospect"].isin(sel)].copy()

    num_cols = [c for c in sub_f.select_dtypes(include="number").columns]

    st.markdown("<div class=\"section-header\">Estadísticos por parámetro</div>", unsafe_allow_html=True)
    show_stats_table({c: sub_f[c] for c in num_cols})

    st.markdown("<div class=\"section-header\">Box-plots</div>", unsafe_allow_html=True)
    fig = boxplot_panel({c: sub_f[c] for c in num_cols}, box_title, ncols=3)
    if fig:
        st.pyplot(fig)
        plt.close(fig)

    visible = [(p,xl) for p,xl in params if p in sub_f.columns]
    if visible:
        st.markdown("<div class=\"section-header\">Perfiles por profundidad</div>", unsafe_allow_html=True)
        n = min(3, len(visible))
        pcols = st.columns(n)
        for i,(param,xl) in enumerate(visible):
            s2 = sub_f[[desc_col, prof_col, param]].dropna()
            fig = depth_profile(s2, param, desc_col, prof_col, param+" vs Prof.", xl)
            if fig:
                pcols[i % n].pyplot(fig)
                plt.close(fig)

    st.markdown("<div class=\"section-header\">Tabla de datos</div>", unsafe_allow_html=True)
    st.dataframe(sub_f.drop(columns=["_prospect"], errors="ignore").reset_index(drop=True),
                 use_container_width=True)


def page_spt(df):
    _page_generic(df, "SPT / MI - Penetración", "\U0001f4cd",
        get_spt, "Descripción Muestra", "Descripción Muestra", "Profundidad inicial",
        [("SPT (valores centrales)","N SPT"),("MI (valores centrales)","qd MPa"),
         ("ISPT_INC1","Inc1"),("ISPT_INC2","Inc2"),("ISPT_INC3","Inc3"),("ISPT_INC4","Inc4")],
        "SPT / MI - Box-plots", "spt")

def page_gran(df):
    _page_generic(df, "Granulometría y Plasticidad", "\U0001f9ea",
        get_gran, "Descripción Muestra", "Descripción Muestra", "Profundidad inicial",
        [("Tamiz Grava","% Grava"),("Tamiz Arena","% Arena"),("Tamiz Finos","% Finos"),
         ("LL","LL %"),("LP","LP %"),("IP","IP %"),
         ("20","P20"),("5","P5"),("2","P2"),("0.4","P0.4"),("0.08","P0.08")],
        "Granulometría - Box-plots", "gran")

def page_atter(df):
    _page_generic(df, "Límites de Atterberg", "\U0001f4d0",
        get_atter, "Descripción Muestra", "Descripción Muestra", "Profundidad inicial",
        [("LL","LL %"),("LP","LP %"),("IP","IP %")],
        "Atterberg - Box-plots", "atter")

def page_mec(df):
    _page_generic(df, "Propiedades Mecánicas", "\u2699\ufe0f",
        get_mec, "Descripción Muestra.1", "Descripción Muestra.1", "Profundidad inicial.1",
        [("Peso específico","Peso Esp."),("Densidad Seca Kn/m3","Den.Seca kN/m3"),
         ("Densidad Húmeda KN/m3","Den.Hum kN/m3"),("Humedad","Humedad %"),
         ("RCS (kpa)","RCS kPa"),("Ángulo de Rozamiento con denaje","Phi CD deg"),
         ("Cohesión KPa con drenaje","c CD kPa"),
         ("Ángulo de Rozamiento sin denaje","Phi CU deg"),
         ("Cohesión KPa sin drenaje","c CU kPa")],
        "Propiedades Mecánicas - Box-plots", "mec")

def page_consol(df):
    _page_generic(df, "Consolidación / Proctor / CBR", "\U0001f4c8",
        get_consol, "Descripción Muestra.2", "Descripción Muestra.2", "Profundidad inicial.2",
        [("Indice de Poros","e"),("Presión de Preconsolidación (kPa)","Pc kPa"),
         ("Presión Hinchamiento","Ph kPa"),("ρ KN","rho Proctor kN"),
         ("W","W opt %"),("CBR","CBR %"),("CBR 95%","CBR 95%")],
        "Consolidación / CBR - Box-plots", "consol")

def page_quim(df):
    _page_generic(df, "Química del Suelo", "\U0001f9ea",
        get_quim, "Descripción Muestra", "Descripción Muestra", "Profundidad inicial",
        [("MO","MO %"),("SU","Sulfatos SO4"),("Sulfatos (mg/kg de suelo) Media.","Sulfatos mg/kg"),
         ("Grado acidez (ml/kg de suelo seco) Medio","Acidez ml/kg"),
         ("YE","Yesos YE"),("SS","Sales SS"),("% CO3CA","CO3Ca %")],
        "Química - Box-plots", "quim")


# ---------- main ----------
def main():
    uploaded = sidebar_upload()

    if uploaded is None:
        st.markdown("<div class=\"main-title\">\U0001faa8 GeoLab Viewer</div>", unsafe_allow_html=True)
        st.markdown("<div class=\"sub-title\">Visor profesional de ensayos geotécnicos de laboratorio</div>", unsafe_allow_html=True)
        st.info("\U0001f4c2 Carga tu archivo Excel en la barra lateral para comenzar.")
        st.markdown("""
---
**Secciones disponibles:**
- 📊 Resumen General — KPIs + perfiles por profundidad de todos los ensayos
- 📍 SPT / MI — Incrementos y valores centrales
- 🧪 Granulometría y Plasticidad — Curvas y límites
- 📐 Límites de Atterberg — LL, LP, IP
- ⚙️ Propiedades Mecánicas — Densidad, RCS, corte
- 📈 Consolidación / Proctor / CBR
- 🧬 Química del Suelo — MO, Sulfatos, Yesos, etc.
""")
        return

    df = load_and_clean(uploaded)

    pages = {
        "📊 Resumen General":         page_overview,
        "📍 SPT / MI":                page_spt,
        "🧪 Granulometría":           page_gran,
        "📐 Atterberg":               page_atter,
        "⚙️ Mecánicas":               page_mec,
        "📈 Consolidación/CBR":       page_consol,
        "🧬 Química":                 page_quim,
    }

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Navegación**")
    choice = st.sidebar.radio("Sección:", list(pages.keys()))
    st.sidebar.markdown("---")
    st.sidebar.markdown("Filas cargadas: **" + str(len(df)) + "**")
    st.sidebar.markdown("Columnas: **" + str(len(df.columns)) + "**")

    pages[choice](df)


if __name__ == "__main__":
    main()

