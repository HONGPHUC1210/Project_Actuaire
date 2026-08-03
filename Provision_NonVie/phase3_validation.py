"""
phase3_validation.py
=====================
Validation croisée : résultats "maison" (chainladder_core.py) vs
package `chainladder-python` (implémentation industrielle de référence).

Critère de succès (PRD) : écart < 1% sur l'ultimate.
"""

import pandas as pd
import chainladder as cl

from chainladder_core import chain_ladder_ultimate

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def load_triangle():
    tri_obj = cl.load_sample("genins")
    df = tri_obj.to_frame()
    df.columns = [str(c) for c in df.columns]
    df.index = [d.year for d in df.index]
    return tri_obj, df


def validate_chain_ladder():
    tri_obj, triangle = load_triangle()

    # --- Résultats maison ---
    result_home, factors_home, _ = chain_ladder_ultimate(triangle)

    # --- Résultats package chainladder-python ---
    model_pkg = cl.Chainladder().fit(tri_obj)
    ultimate_pkg = model_pkg.ultimate_.to_frame().iloc[:, 0]
    ultimate_pkg.index = [d.year for d in ultimate_pkg.index]

    ldf_pkg = model_pkg.ldf_.to_frame().iloc[0]
    ldf_pkg.index = [str(c).split("-")[0] for c in ldf_pkg.index]

    # --- Comparaison ---
    comparison = pd.DataFrame({
        "ultimate_maison": result_home["ultimate_cl"],
        "ultimate_package": ultimate_pkg,
    })
    comparison["ecart_%"] = (
        (comparison["ultimate_maison"] - comparison["ultimate_package"])
        / comparison["ultimate_package"] * 100
    )

    ldf_comparison = pd.DataFrame({
        "ldf_maison": factors_home,
        "ldf_package": ldf_pkg,
    })
    ldf_comparison["ecart_%"] = (
        (ldf_comparison["ldf_maison"] - ldf_comparison["ldf_package"])
        / ldf_comparison["ldf_package"] * 100
    )

    return comparison, ldf_comparison


if __name__ == "__main__":
    comparison, ldf_comparison = validate_chain_ladder()

    print("=== Comparaison des Link Ratios (Development Factors) ===")
    print(ldf_comparison)

    print("\n=== Comparaison des Ultimates : maison vs chainladder-python ===")
    print(comparison)

    max_gap = comparison["ecart_%"].abs().max()
    print(f"\nEcart maximum observe : {max_gap:.4f}%")
    if max_gap < 1.0:
        print("VALIDATION REUSSIE : ecart < 1% (critere de succes PRD)")
    else:
        print("ATTENTION : ecart >= 1%, a investiguer")
