# TalentLab: HR Talent Segmentation & Retention System

An end-to-end machine learning project that segments a 1,000-employee workforce into
actionable talent personas, scores each employee's retention priority, and delivers the
results through an interactive dashboard.

**Live dashboard:** [enfield-protocol.streamlit.app](https://enfield-protocol.streamlit.app)

---

## Problem

Most HR teams apply one uniform policy to a diverse workforce. Without a record of who has
left before, they cannot predict attrition. And with no single metric able to describe an
employee, profiling stays manual and subjective. This project lets the data reveal its own
patterns instead.

## Approach

1. **Data cleaning.** Converted anomalies (impossible ages, extreme values, 550 missing
   entries) to NaN, then imputed with department-level medians.
2. **Clustering.** Compared K-Means, Agglomerative, GMM, and DBSCAN; selected **K-Means
   (k=5)** on Silhouette (0.1982), Davies-Bouldin (1.3702), and Calinski-Harabasz (216.9).
3. **Explainability.** A Random Forest surrogate with SHAP reveals which feature drives
   membership in each segment.
4. **Priority scoring.** A transparent, literature-grounded layer
   (`Priority = Turnover Risk × Impact`) ranks every employee into Critical, Watchlist, and
   Stable tiers.
5. **Deployment.** An interactive Streamlit dashboard, updated by replacing a single Excel
   file, with no model artifacts to manage.

## The Five Personas

| Persona | Size | Profile |
|---|---|---|
| At-Risk Employee | 182 | Disengaged, needs early support |
| Loyal Performer | 224 | High contribution, paid a third of peers |
| Established Performer | 225 | Top and engaged, worth retaining |
| Declining Performer | 159 | Productivity dropping; coach rather than replace |
| Rising Star | 210 | Engaged early-tenure talent |

## Dashboard Features

- **Talent Classifier.** Enter a profile, get segment, priority tier, and HR action instantly
- **Summary.** Workforce stats, cluster profiles, department breakdown
- **3D t-SNE.** Interactive validation that the five segments are truly separated
- **Employee Card.** Percentile bars, radar vs segment average, similar employees
- **Comparison.** Side-by-side view of two or three employees

## Tech Stack

Python · Scikit-learn · SHAP · Plotly · Streamlit · Pandas · NumPy

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Note

Segment assignment for new employees uses a nearest-centroid rule mathematically equivalent
to the trained K-Means model (verified 100% against all 1,000 training labels). The priority
score is a decision-support tool, not a resignation prediction. Because the dataset has no
attrition label, the score is a literature-grounded proxy rather than a trained predictive
model.

---

*Rakamin Academy, Data Science Final Project · Team Endfield Protocol*
