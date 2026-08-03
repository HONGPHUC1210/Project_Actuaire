# Provisionnement Non-Vie : Chain-Ladder & Bornhuetter-Ferguson

**Auteur :** Hong Phuc QUACH
**Date :** Août 2026
**Dataset :** GenIns (Taylor & Ashe, 1983) — triangle de sinistres payés cumulés,
General Liability, 10 années de survenance × 10 années de développement.
Source publique : package `chainladder-python` (`cl.load_sample('genins')`).

---

## 1. Objectif

Démontrer une maîtrise pratique des méthodes de provisionnement Non-Vie standards
(Chain-Ladder, Bornhuetter-Ferguson), depuis la compréhension manuelle (Excel) jusqu'à
l'industrialisation (Python), avec validation croisée contre un package de référence et
une analyse critique des limites des méthodes.

## 2. Contenu du repository

| Fichier | Phase | Description |
|---|---|---|
| `chainladder_manuel_phase0.xlsx` | 0 | Calcul manuel en Excel (formules, pas de valeurs codées en dur) : triangle brut, link ratios, triangle complété, ultimate/IBNR |
| `chainladder_core.py` | 1 & 2 | Implémentation Python from scratch : link ratios, projection du triangle, Chain-Ladder, Bornhuetter-Ferguson |
| `phase3_validation.py` | 3 | Validation croisée contre le package `chainladder-python` |
| `phase4_sensitivity.py` | 4 | Analyse de sensibilité (loss ratio a priori, inflation non anticipée) + graphiques |
| `sensitivity_loss_ratio.png` | 4 | Graphique — impact du loss ratio a priori sur l'Ultimate BF |
| `sensitivity_inflation.png` | 4 | Graphique — impact de l'inflation non anticipée sur l'Ultimate CL |
| `sensitivity_summary.csv` | 4 | Tableau de synthèse des scénarios |
| `triangle_genins_raw.csv` | — | Données sources |

## 3. Méthodologie

### Chain-Ladder
1. **Link ratios (volume-weighted)** : `f_j = Σ C[i,j+1] / Σ C[i,j]`, calculés sur la
   portion commune du triangle (accident years pour lesquels les deux colonnes sont observées).
2. **Projection en cascade** : `Ĉ[i,j+1] = C[i,j] × f_j` pour toute cellule non observée.
3. **Ultimate** = dernière colonne du triangle projeté. **IBNR** = Ultimate − Paid to date.

### Bornhuetter-Ferguson
`Ultimate_BF = Paid_to_date + (1 − β) × Ultimate_a_priori`, où :
- `Ultimate_a_priori = Prime × Loss Ratio a priori` (65 % retenu comme hypothèse centrale)
- `β` (% développé) = `1 / CDF` depuis la dernière colonne observée jusqu'à l'ultimate,
  `CDF` étant le produit cumulé des link ratios de Chain-Ladder restants.

> **Note sur les primes :** le dataset GenIns ne fournit pas de primes acquises réelles.
> Une prime proxy croissante par accident year est utilisée uniquement pour illustrer le
> mécanisme du BF — ce point est assumé et documenté explicitement, pas présenté comme
> une donnée réelle.

## 4. Résultats clés

### Validation croisée (Phase 3)
Écart maximum observé entre l'implémentation maison et `chainladder-python` :
**0.00 %** sur les 10 accident years (concordance exacte sur les link ratios et les ultimates).

### Sensibilité (Phase 4)

**Insight 1 — Bornhuetter-Ferguson est plus stable que Chain-Ladder sur les accident
years récentes.** Pour les années peu développées (2009, 2010 : β ≈ 24 % et 7 %), l'Ultimate
BF est dominé par l'a priori (poids `1−β` élevé), donc peu sensible au bruit des quelques
paiements observés. À l'inverse, le Chain-Ladder pur, 100 % piloté par la donnée observée,
est structurellement plus volatil sur ces mêmes années (link ratios précoces très élevés,
ex. `f_{12→24} ≈ 3.49`, appliqués à une base de données très faible).

**Insight 2 — Le Chain-Ladder sous-estime l'ultimate en cas d'inflation non anticipée.**
Les link ratios historiques capturent une tendance d'inflation passée stable ; si l'inflation
future accélère (chocs de coût des sinistres, changements réglementaires, etc.), cette
accélération n'est pas dans les link ratios calculés sur données historiques. Le scénario à
+8 % d'inflation non captée montre un ultimate total supérieur de **~22 %** au scénario
de base, avec l'écart le plus marqué sur les accident years les moins développées (2008-2010),
qui ont le plus de développement futur restant à projeter, donc le plus d'exposition au biais.

## 5. Limites & hypothèses (à discuter en entretien)

- Link ratios volume-weighted uniquement : pas de moyenne simple ni régression testée
  (extension possible : comparer les 3 approches).
- Pas de modélisation stochastique (Mack Chain-Ladder, Bootstrap ODP) dans cette V1 →
  pas d'intervalle de confiance sur l'IBNR, uniquement une estimation ponctuelle.
- Loss ratio a priori BF fixé arbitrairement à 65 % (hypothèse de marché standard, non
  calibrée sur des données spécifiques à ce portefeuille).
- Le dernier link ratio (108→120) est proche de 1 (tail factor implicite = 1), hypothèse
  simplificatrice : pas de queue de développement au-delà de 120 mois.

## 6. Extensions futures (hors scope V1)

- Lien avec IFRS 17 (Liability for Incurred Claims, discounting, Risk Adjustment)
- Méthode stochastique (Mack Chain-Ladder, Bootstrap ODP) pour intervalle de confiance
- Application à un triangle Vie/Prévoyance

## 7. Reproduire les résultats

```bash
pip install chainladder openpyxl pandas numpy matplotlib
python3 chainladder_core.py        # Phase 1 & 2
python3 phase3_validation.py       # Phase 3
python3 phase4_sensitivity.py      # Phase 4
python3 build_excel.py             # Phase 0 (Excel)
```
