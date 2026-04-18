# Méthodologie Technique de Simulation du Risque Sismique

Ce document récapitule les principes de calcul et la méthodologie extraits des outils de simulation internes (Excel et Moteur Monte Carlo) pour la plateforme AEC Seismic Risk.

## 1. Approche Déterministe (Modèle Excel)
L'approche déterministe se concentre sur l'estimation des pertes pour un événement unique de type "Pire Scénario" (Worst Case Scenario).

### Formule du Dommage Maximal (MAX_DAMAGE)
Le dommage maximal probable par commune est calculé comme suit :
**MAX_DAMAGE = Capital Assuré × Coefficient d’Accélération (A)**

*   **Coefficient A** : Issu du règlement RPA 99/2003 (Tableau 4.1), il représente l'accélération de zone.
*   **Zonage Type** : 
    *   Zone III (Alger, Boumerdès, Chlef) : Coefficient `A` ≈ 0.4.
    *   Zone II : Coefficient `A` ≈ 0.3.
    *   Zone I : Coefficient `A` ≈ 0.15.

### Rétention et Réassurance
Le modèle intègre une logique de rétention de **30% (Quota-Share)**.
*   **GAM Retention** : 30% du Capital, de la Prime et de l'exposition au dommage sont conservés.
*   **Cession** : 70% de l'exposition est cédée à la réassurance.

---

## 2. Approche Probabiliste (Simulation Monte Carlo)
Complémente l'approche déterministe en simulant 5 000 années d'activité aléatoire.

### Métriques Clés Générées
1.  **AAL (Average Annual Loss)** : Perte moyenne annuelle attendue, utilisée pour calibrer la prime pure (Burn Cost).
2.  **PML (Probable Maximum Loss)** : Perte maximale à une période de retour donnée (ex: 200 ans, 500 ans).
3.  **EP Curve (Exceedance Probability)** : Courbe montrant la probabilité que les pertes dépassent un certain seuil.

---

## 3. Comparaison Technique
| Paramètre | Modèle Déterministe (Excel) | Modèle Probabiliste (Simulation) |
| :--- | :--- | :--- |
| **Objectif** | Évaluer la solvabilité sur un séisme majeur | Estimer les pertes moyennes à long terme |
| **Input Principal** | Coefficients RPA statiques | Taux de hasard stochastique (Poisson) |
| **Sortie** | Capacité maximale requise | PML, AAL, EP Curve |
| **Usage** | Réassurance / Solvabilité | Tarification / Budgétisation |
