"""
Tests de contrato de la base de datos de parámetros del terreno.

Comprueban integridad de los YAML, corrección de unidades, plausibilidad
física de los valores y el formateo de presentación.
"""
import math
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import soil_params_engine as eng  # noqa: E402

FUENTES = [m["fuente_id"] for m in eng.lista_fuentes()]

# Límites físicos plausibles por campo (para cazar errores de miles/decimales)
LIMITES = {
    "gamma_ap": (8, 24), "gamma_sat": (8, 24), "gamma_sum": (0, 15),
    "peso_sat": (8, 24), "peso_seco": (8, 24),
    "phi": (0, 50), "phi_r": (0, 45), "poisson": (0.0, 0.5),
    "k": (1e-13, 1.0),
}


# --------------------------------------------------------------------------- #
#  Estructura / integridad                                                     #
# --------------------------------------------------------------------------- #
def test_hay_siete_fuentes():
    assert len(FUENTES) == 7


def test_ids_unicos_y_ordenados():
    ids = [m["id"] for m in eng.lista_fuentes()]
    assert ids == sorted(ids)
    assert len(set(ids)) == len(ids)


@pytest.mark.parametrize("fid", FUENTES)
def test_toda_fuente_tiene_cita(fid):
    meta = eng.get_fuente(fid)["meta"]
    assert meta.get("cita"), f"{fid} sin cita (ningún valor sin fuente)"
    assert meta.get("nombre")


@pytest.mark.parametrize("fid", FUENTES)
def test_filas_casan_con_columnas(fid):
    doc = eng.get_fuente(fid)
    campos = {c["campo"] for c in doc["columnas"]}
    for fila in doc["filas"]:
        assert set(fila) == campos, f"{fid}: fila descuadrada {fila}"


@pytest.mark.parametrize("fid", FUENTES)
def test_tabla_no_vacia(fid):
    assert len(eng.tabla(fid)) > 0


# --------------------------------------------------------------------------- #
#  Unidades corregidas                                                         #
# --------------------------------------------------------------------------- #
def _unidades(fid):
    return {c["campo"]: c["unidad"] for c in eng.get_fuente(fid)["columnas"]}


def test_navfac_cohesion_en_t_por_m2():
    u = _unidades("navfac_1971")
    assert u["c_comp"] == "t/m²" and u["c_sat"] == "t/m²"


def test_densidades_cte_en_kN_por_m3():
    u = _unidades("cte_densidades")
    assert u["peso_sat"] == "kN/m³" and u["peso_seco"] == "kN/m³"


def test_permeabilidad_en_metros_por_segundo():
    for fid in ("grundbau_taschenbuch", "cte_permeabilidad"):
        assert any(c["unidad"] == "m/s" and c["tipo"] == "perm"
                   for c in eng.get_fuente(fid)["columnas"])


def test_no_queda_ninguna_unidad_erronea():
    prohibidas = {"m/sg", "t/m3", "kN/m2"}
    for fid in FUENTES:
        for c in eng.get_fuente(fid)["columnas"]:
            assert c["unidad"] not in prohibidas, f"{fid}/{c['campo']}"


# --------------------------------------------------------------------------- #
#  Plausibilidad física                                                        #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("fid", FUENTES)
def test_valores_dentro_de_rango_fisico(fid):
    doc = eng.get_fuente(fid)
    for fila in doc["filas"]:
        for campo, lim in LIMITES.items():
            v = fila.get(campo)
            if v is None:
                continue
            for x in (v if isinstance(v, list) else [v]):
                if isinstance(x, (int, float)):
                    assert lim[0] <= x <= lim[1], \
                        f"{fid}/{campo}={x} fuera de {lim} ({fila.get('tipo_suelo')})"


@pytest.mark.parametrize("fid", FUENTES)
def test_rangos_ordenados(fid):
    """En todo rango [a, b] con ambos extremos definidos, a <= b."""
    for fila in eng.get_fuente(fid)["filas"]:
        for v in fila.values():
            if isinstance(v, list) and len(v) == 2:
                a, b = v
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    assert a <= b


# --------------------------------------------------------------------------- #
#  Valores "golden" (transcripción correcta desde el Excel)                    #
# --------------------------------------------------------------------------- #
def _fila(fid, nombre):
    for f in eng.get_fuente(fid)["filas"]:
        if f["tipo_suelo"] == nombre:
            return f
    raise AssertionError(f"{nombre} no está en {fid}")


def test_golden_grundbau_grava():
    f = _fila("grundbau_taschenbuch", "Grava")
    assert f["gamma_ap"] == [16, 19]
    assert f["phi"] == [34, 42]
    assert f["k"] == [0.011, 0.21]


def test_golden_metrosur_ranges_parseados():
    f = _fila("metrosur_1999", "Arenas de miga")
    assert f["c"] == [5, 10]
    assert f["e_def"] == [5500, 7500]      # '5.500-7.500'
    assert f["poisson"] == 0.3             # '0,30'


def test_golden_cte_permeabilidad_arcilla():
    f = _fila("cte_permeabilidad", "Arcilla")
    assert f["k"][0] is None
    assert math.isclose(f["k"][1], 1e-9)


# --------------------------------------------------------------------------- #
#  Formateo de presentación                                                    #
# --------------------------------------------------------------------------- #
def test_formato_permeabilidad_superindices():
    assert eng.fmt_perm(1e-9) == "10⁻⁹"
    assert eng.fmt_perm(0.011) == "1,1·10⁻²"


def test_formato_rango_y_vacio():
    assert eng.fmt_valor([16, 19], "rango") == "16 – 19"
    assert eng.fmt_valor(None, "rango") == eng.NA
    assert eng.fmt_valor([None, 1e-9], "perm") == "< 10⁻⁹"


def test_tabla_formateada_sin_nulos_crudos():
    for fid in FUENTES:
        df = eng.tabla_formateada(fid)
        assert not df.isin(["None", "nan"]).any().any()
