# CV Bullets — Projet Provisionnement Non-Vie (Chain-Ladder & BF)

## Version FR

**Provisionnement Non-Vie — Chain-Ladder & Bornhuetter-Ferguson (projet personnel, 2026)**
- Implémenté en Python les méthodes Chain-Ladder et Bornhuetter-Ferguson *from scratch*
  (link ratios volume-weighted, projection de triangle, calcul d'IBNR) sur un triangle de
  sinistres payés (10×10), validé à l'identique (écart de 0.00 %) contre le package de
  référence `chainladder-python`
- Construit une analyse de sensibilité (loss ratio a priori, inflation non anticipée)
  mettant en évidence la plus grande stabilité du BF sur les accident years récentes et
  l'impact potentiel de +22 % sur l'ultimate en cas d'inflation non captée par les
  link ratios historiques

*(Variante courte, une ligne, si espace limité sur le CV)*
- Chain-Ladder & Bornhuetter-Ferguson *from scratch* en Python (validé contre
  `chainladder-python`, écart 0 %) avec analyse de sensibilité loss ratio / inflation

## Version EN

**Non-Life Reserving — Chain-Ladder & Bornhuetter-Ferguson (personal project, 2026)**
- Implemented Chain-Ladder and Bornhuetter-Ferguson methods from scratch in Python
  (volume-weighted link ratios, triangle projection, IBNR calculation) on a 10×10 paid
  claims triangle, validated to an exact match (0.00% deviation) against the industry
  reference package `chainladder-python`
- Built a sensitivity analysis (a priori loss ratio, unanticipated inflation) showing
  the greater stability of BF for recent accident years and a potential +22% impact on
  the ultimate under an inflation scenario not captured by historical link ratios

*(Short one-line variant, if CV space is limited)*
- Chain-Ladder & Bornhuetter-Ferguson from scratch in Python (validated against
  `chainladder-python`, 0% deviation) with loss ratio / inflation sensitivity analysis

---

## Notes d'honnêteté (pour toi, pas pour le CV)

- "Validé à l'identique / 0.00% deviation" est un fait vérifié dans ce projet — pas
  un arrondi optimiste, le résultat était réellement exact.
- Le +22% sur l'inflation est spécifique au scénario +8%/an choisi ici, pas une
  affirmation générale — si on te demande en entretien, sache l'expliquer comme un
  scénario de stress, pas une prévision.
- Pas de mention de Mack/Bootstrap/IFRS 17 dans le bullet : ce sont des extensions
  explicitement hors scope V1, ne pas laisser penser que c'est fait.
