"""
chainladder_core.py
====================
Implémentation "from scratch" des méthodes de provisionnement Non-Vie :
- Chain-Ladder (link ratios volume-weighted)
- Bornhuetter-Ferguson

Auteur : Hong Phuc QUACH
Dataset : GenIns (Taylor & Ashe, 1983) — triangle de sinistres payés cumulés,
          10 années de survenance x 10 années de développement.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# PHASE 1 — Chain-Ladder from scratch
# ---------------------------------------------------------------------------

def development_factors(triangle: pd.DataFrame) -> pd.Series:
    """
    Calcule les link ratios (facteurs de développement) volume-weighted.

    f_j = somme_i C[i, j+1] / somme_i C[i, j]
    calculé uniquement sur la portion "commune" du triangle
    (les accident years i pour lesquels C[i,j] et C[i,j+1] sont tous deux observés).

    Parameters
    ----------
    triangle : DataFrame, index = accident year, columns = development year,
               NaN pour les cellules non observées.

    Returns
    -------
    Series indexée par development year de départ (ex: f['12'] = f_{12->24}).
    """
    cols = list(triangle.columns)
    factors = {}
    for j in range(len(cols) - 1):
        col_curr, col_next = cols[j], cols[j + 1]
        mask = triangle[col_next].notna()  # période commune
        num = triangle.loc[mask, col_next].sum()
        den = triangle.loc[mask, col_curr].sum()
        factors[col_curr] = num / den
    return pd.Series(factors, name="development_factor")


def project_triangle(triangle: pd.DataFrame, factors: pd.Series) -> pd.DataFrame:
    """
    Complète le triangle en appliquant les link ratios en cascade
    sur les cellules manquantes (partie inférieure droite du triangle).
    """
    projected = triangle.copy().astype(float)
    cols = list(triangle.columns)
    for i in projected.index:
        for j in range(len(cols) - 1):
            c_curr, c_next = cols[j], cols[j + 1]
            if pd.isna(projected.loc[i, c_next]):
                projected.loc[i, c_next] = projected.loc[i, c_curr] * factors[c_curr]
    return projected


def latest_diagonal(triangle: pd.DataFrame) -> pd.Series:
    """Dernière valeur observée (non-NaN) par accident year = cumul payé à date."""
    return triangle.apply(lambda row: row.dropna().iloc[-1], axis=1)


def chain_ladder_ultimate(triangle: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline complet Chain-Ladder : link ratios -> projection -> ultimate/IBNR.

    Returns
    -------
    DataFrame avec colonnes : paid_to_date, ultimate_cl, ibnr_cl
    """
    factors = development_factors(triangle)
    projected = project_triangle(triangle, factors)
    ultimate = projected.iloc[:, -1]
    paid = latest_diagonal(triangle)
    result = pd.DataFrame({
        "paid_to_date": paid,
        "ultimate_cl": ultimate,
        "ibnr_cl": ultimate - paid,
    })
    return result, factors, projected


# ---------------------------------------------------------------------------
# PHASE 2 — Bornhuetter-Ferguson
# ---------------------------------------------------------------------------

def cumulative_development_factor(factors: pd.Series, from_col) -> float:
    """
    Facteur de développement cumulé depuis `from_col` jusqu'à l'ultimate
    (produit des link ratios successifs à partir de cette position).
    """
    cols = list(factors.index)
    idx = cols.index(from_col)
    return float(np.prod(factors.iloc[idx:].values))


def pct_developed(triangle: pd.DataFrame, factors: pd.Series) -> pd.Series:
    """
    % développement (beta_i) pour chaque accident year, basé sur la
    dernière colonne observée de cette accident year.

    beta_i = 1 / CDF(depuis la dernière colonne observée)

    Pour la toute dernière colonne du triangle (développement complet),
    beta = 1 (100% développé, pas de CDF résiduel).
    """
    cols = list(triangle.columns)
    betas = {}
    for i in triangle.index:
        row = triangle.loc[i]
        last_observed_col = row.dropna().index[-1]
        if last_observed_col == cols[-1]:
            betas[i] = 1.0
        else:
            cdf = cumulative_development_factor(factors, last_observed_col)
            betas[i] = 1.0 / cdf
    return pd.Series(betas, name="pct_developed")


def bornhuetter_ferguson_ultimate(
    triangle: pd.DataFrame,
    factors: pd.Series,
    premium: pd.Series,
    apriori_loss_ratio: float,
) -> pd.DataFrame:
    """
    Ultimate_BF = Cumul payé + (1 - beta) x Ultimate_a_priori
    Ultimate_a_priori = premium x apriori_loss_ratio

    Parameters
    ----------
    triangle : triangle brut (pour paid_to_date et beta)
    factors  : link ratios (Phase 1)
    premium  : primes acquises par accident year (Series indexée comme triangle.index)
    apriori_loss_ratio : loss ratio a priori (ex: 0.65)

    Returns
    -------
    DataFrame avec colonnes : paid_to_date, pct_developed, ultimate_apriori,
                               ultimate_bf, ibnr_bf
    """
    paid = latest_diagonal(triangle)
    beta = pct_developed(triangle, factors)
    ultimate_apriori = premium * apriori_loss_ratio
    ultimate_bf = paid + (1 - beta) * ultimate_apriori
    return pd.DataFrame({
        "paid_to_date": paid,
        "pct_developed": beta,
        "ultimate_apriori": ultimate_apriori,
        "ultimate_bf": ultimate_bf,
        "ibnr_bf": ultimate_bf - paid,
    })


if __name__ == "__main__":
    import chainladder as cl

    tri_obj = cl.load_sample("genins")
    triangle = tri_obj.to_frame()
    triangle.columns = [str(c) for c in triangle.columns]
    triangle.index = [d.year for d in triangle.index]

    result_cl, factors, projected = chain_ladder_ultimate(triangle)
    print("=== Link ratios (development factors) ===")
    print(factors.round(4))
    print("\n=== Chain-Ladder result ===")
    print(result_cl.round(0))

    # Premium hypothétique (proxy réaliste : ~1.6x le paid_to_date moyen mature,
    # utilisé uniquement pour illustrer BF -- GenIns ne fournit pas de premium)
    premium = pd.Series(
        {ay: 5_000_000 + i * 150_000 for i, ay in enumerate(triangle.index)}
    )
    result_bf = bornhuetter_ferguson_ultimate(triangle, factors, premium, apriori_loss_ratio=0.65)
    print("\n=== Bornhuetter-Ferguson result (apriori LR = 65%) ===")
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    print(result_bf)
