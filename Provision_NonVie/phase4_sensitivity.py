"""
phase4_sensitivity.py
=======================
Phase 4 -- Analyse de sensibilite :
  (A) Variation du loss ratio a priori (60/65/70/75%) -> impact sur Ultimate BF
  (B) Inflation non capturee dans le triangle historique -> impact sur Ultimate CL

Genere 2 graphiques + un tableau de synthese.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import chainladder as cl

from chainladder_core import (
    chain_ladder_ultimate,
    bornhuetter_ferguson_ultimate,
    development_factors,
)

pd.set_option("display.float_format", lambda x: f"{x:,.0f}")


def load_triangle():
    tri_obj = cl.load_sample("genins")
    df = tri_obj.to_frame()
    df.columns = [str(c) for c in df.columns]
    df.index = [d.year for d in df.index]
    return df


# ---------------------------------------------------------------------------
# (A) Sensibilite au Loss Ratio a priori (BF)
# ---------------------------------------------------------------------------

def sensitivity_loss_ratio(triangle, premium, loss_ratios=(0.60, 0.65, 0.70, 0.75)):
    factors = development_factors(triangle)
    results = {}
    for lr in loss_ratios:
        bf = bornhuetter_ferguson_ultimate(triangle, factors, premium, lr)
        results[f"LR_{int(lr*100)}%"] = bf["ultimate_bf"]
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# (B) Sensibilite a l'inflation non anticipee (Chain-Ladder)
# ---------------------------------------------------------------------------

def apply_inflation_trend(triangle, annual_inflation):
    """
    Simule une inflation des sinistres NON capturee dans les link ratios
    historiques : on gonfle chaque cellule observee d'un facteur cumule
    d'inflation croissant avec l'anciennete du development year, PUIS on
    recalcule le Chain-Ladder sur le triangle "inflate" pour observer
    l'effet sur l'ultimate par rapport au triangle de base.

    Approche simplifiee : facteur d'inflation applique uniquement à la
    portion projetee (developpement futur), pour representer une inflation
    qui accelere APRES la derniere observation et n'est donc pas capturee
    par les link ratios historiques (calcules sur donnees passees, stables).
    """
    cols = list(triangle.columns)
    factors = development_factors(triangle)
    # Ultimate SANS inflation additionnelle (baseline)
    result_base, _, projected_base = chain_ladder_ultimate(triangle)

    # On applique l'inflation uniquement aux increments projetes (futurs),
    # proportionnellement au nombre de periodes de developpement restantes.
    projected_inflated = triangle.copy().astype(float)
    n_cols = len(cols)
    for i in projected_inflated.index:
        row_raw = triangle.loc[i]
        last_obs_idx = row_raw.notna().values.nonzero()[0].max()
        prev_val = row_raw.iloc[last_obs_idx]
        for j in range(last_obs_idx, n_cols - 1):
            periods_ahead = j - last_obs_idx + 1
            base_increment = projected_base.loc[i].iloc[j + 1] - projected_base.loc[i].iloc[j]
            inflated_increment = base_increment * ((1 + annual_inflation) ** periods_ahead)
            new_val = prev_val + inflated_increment
            projected_inflated.loc[i, cols[j + 1]] = new_val
            prev_val = new_val

    ultimate_inflated = projected_inflated.iloc[:, -1]
    return ultimate_inflated


def sensitivity_inflation(triangle, inflation_scenarios=(0.0, 0.02, 0.05, 0.08)):
    results = {}
    for infl in inflation_scenarios:
        label = f"Inflation_{int(infl*100)}%"
        results[label] = apply_inflation_trend(triangle, infl)
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    triangle = load_triangle()
    premium = pd.Series(
        {ay: 5_000_000 + i * 150_000 for i, ay in enumerate(triangle.index)}
    )

    # --- (A) Loss ratio sensitivity ---
    lr_sensitivity = sensitivity_loss_ratio(triangle, premium)
    lr_total = lr_sensitivity.sum()
    print("=== (A) Sensibilite Loss Ratio a priori -- Ultimate total BF ===")
    print(lr_total)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    lr_sensitivity.plot(marker="o", ax=ax)
    ax.set_title("Sensibilite du Ultimate BF par accident year au Loss Ratio a priori")
    ax.set_xlabel("Accident Year")
    ax.set_ylabel("Ultimate BF ($)")
    ax.legend(title="Loss Ratio a priori")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("sensitivity_loss_ratio.png", dpi=150)
    plt.close()

    # --- (B) Inflation sensitivity ---
    infl_sensitivity = sensitivity_inflation(triangle)
    infl_total = infl_sensitivity.sum()
    print("\n=== (B) Sensibilite Inflation non anticipee -- Ultimate total CL ===")
    print(infl_total)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    infl_sensitivity.plot(marker="o", ax=ax)
    ax.set_title("Sensibilite du Ultimate CL par accident year a l'inflation non anticipee")
    ax.set_xlabel("Accident Year")
    ax.set_ylabel("Ultimate CL ($)")
    ax.legend(title="Inflation annuelle non captee")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("sensitivity_inflation.png", dpi=150)
    plt.close()

    # --- Tableau de synthese ---
    summary = pd.DataFrame({
        "Scenario": ["LR 60%", "LR 65%", "LR 70%", "LR 75%",
                     "Inflation 0%", "Inflation 2%", "Inflation 5%", "Inflation 8%"],
        "Ultimate_total": list(lr_total.values) + list(infl_total.values),
    })
    summary["Ecart_vs_base_%"] = (
        (summary["Ultimate_total"] - summary["Ultimate_total"].iloc[1])
        / summary["Ultimate_total"].iloc[1] * 100
    )
    summary.to_csv("sensitivity_summary.csv", index=False)
    print("\n=== Tableau de synthese (sauvegarde dans sensitivity_summary.csv) ===")
    print(summary)

    print("\nGraphiques sauvegardes : sensitivity_loss_ratio.png, sensitivity_inflation.png")
