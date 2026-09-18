import numpy as np
import pandas as pd

# 50.000 müşterilik sentetik kredi risk portföyü simülasyonu
np.random.seed(42)
n_customers = 50000

customer_id = np.arange(100001, 100001 + n_customers)
income_total = np.random.lognormal(mean=9.8, sigma=0.5, size=n_customers)
credit_amount = income_total * np.random.uniform(1.2, 4.5, size=n_customers)
annuity_amount = credit_amount / np.random.choice([12, 24, 36, 48], size=n_customers)

max_dpd_last_6m = np.random.exponential(scale=5, size=n_customers).astype(int)
count_dpd_30plus_last_6m = (max_dpd_last_6m >= 30).astype(int) * np.random.poisson(lam=1, size=n_customers)

# TFRS 9 (IFRS 9) Faz Atamaları
def assign_tfrs9_stage(dpd):
    if dpd < 30:
        return "Stage 1 (Düşük Risk)"
    elif dpd < 90:
        return "Stage 2 (Önemli Risk Artışı)"
    else:
        return "Stage 3 (Temerrüt/Batık)"

tfrs9_stages = [assign_tfrs9_stage(d) for d in max_dpd_last_6m]

# PD (Probability of Default) Skoru Modellemesi
debt_to_income = annuity_amount / (income_total / 12)
raw_pd = 1 / (1 + np.exp(-(0.05 * max_dpd_last_6m + 1.2 * debt_to_income - 3.5)))
pd_score = np.clip(np.round(raw_pd, 2), 0.00, 1.00)

# Underwriting Karar Motoru
kredi_karari = np.where((pd_score >= 0.30) | (max_dpd_last_6m >= 60), "RET (Yüksek Risk)", "ONAY (Düşük Risk)")

df_portfolio = pd.DataFrame({
    'customer_id': customer_id,
    'income_total': np.round(income_total, 2),
    'credit_amount': np.round(credit_amount, 2),
    'annuity_amount': np.round(annuity_amount, 2),
    'max_dpd_last_6m': max_dpd_last_6m,
    'count_dpd_30plus_last_6m': count_dpd_30plus_last_6m,
    'TFRS9_Stage': tfrs9_stages,
    'PD_Score': pd_score,
    'Kredi_Karari': kredi_karari
})

# df_portfolio.to_csv("credit_risk_dataset.csv", index=False)
