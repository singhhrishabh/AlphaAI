"""
Regression & Correlation Analysis
Assignment Report - Statistical Analysis using Python
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.figsize': (10, 6),
    'figure.dpi': 150
})

OUTPUT_DIR = "/Users/rishabhsingh/New-Project/output"
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("TOPIC 1: REGRESSION ANALYSIS")
print("=" * 80)
print()
print("Research Question:")
print("Does the number of hours a student studies per week predict their exam score?")
print()

# ─────────────────────────────────────────────────────────────
# DATASET: Student Study Hours vs Exam Scores
# ─────────────────────────────────────────────────────────────
np.random.seed(42)

study_hours = np.array([1, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5,
                        7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 12,
                        2.5, 3, 4, 5, 6, 7, 8, 9, 10, 11])

exam_scores = np.array([30, 35, 42, 44, 48, 50, 55, 58, 62, 65,
                        68, 70, 74, 76, 80, 82, 85, 87, 90, 95,
                        38, 45, 52, 56, 60, 67, 72, 78, 84, 88])

df_reg = pd.DataFrame({
    'Study_Hours': study_hours,
    'Exam_Score': exam_scores
})

print("─" * 60)
print("DATASET: Student Study Hours vs Exam Scores (n = 30)")
print("─" * 60)
print(df_reg.to_string(index=False))
print()

# Descriptive Statistics
print("─" * 60)
print("DESCRIPTIVE STATISTICS")
print("─" * 60)
print(df_reg.describe().round(4).to_string())
print()

# ─────────────────────────────────────────────────────────────
# SIMPLE LINEAR REGRESSION using statsmodels (SPSS-like output)
# ─────────────────────────────────────────────────────────────
X = sm.add_constant(df_reg['Study_Hours'])
y = df_reg['Exam_Score']

model = sm.OLS(y, X).fit()

print("─" * 60)
print("REGRESSION OUTPUT (OLS - Ordinary Least Squares)")
print("─" * 60)
print(model.summary())
print()

# ANOVA Table (computed manually)
print("─" * 60)
print("ANOVA TABLE")
print("─" * 60)
ss_total = np.sum((y - y.mean())**2)
ss_reg = np.sum((model.fittedvalues - y.mean())**2)
ss_res = np.sum(model.resid**2)
df_reg_anova = 1
df_res_anova = n - 2 if 'n' in dir() else len(y) - 2
ms_reg = ss_reg / df_reg_anova
ms_res = ss_res / df_res_anova
f_val = ms_reg / ms_res
f_pval = 1 - stats.f.cdf(f_val, df_reg_anova, df_res_anova)

anova_data = {
    'Source': ['Regression', 'Residual', 'Total'],
    'Sum of Squares': [f'{ss_reg:.4f}', f'{ss_res:.4f}', f'{ss_total:.4f}'],
    'df': [df_reg_anova, df_res_anova, df_reg_anova + df_res_anova],
    'Mean Square': [f'{ms_reg:.4f}', f'{ms_res:.4f}', ''],
    'F': [f'{f_val:.4f}', '', ''],
    'Sig.': [f'{f_pval:.6e}', '', '']
}
anova_df = pd.DataFrame(anova_data)
print(anova_df.to_string(index=False))
print()

# Coefficients Table
print("─" * 60)
print("COEFFICIENTS TABLE")
print("─" * 60)
coef_df = pd.DataFrame({
    'Coefficient': model.params,
    'Std. Error': model.bse,
    't-value': model.tvalues,
    'p-value': model.pvalues,
    'CI Lower (95%)': model.conf_int()[0],
    'CI Upper (95%)': model.conf_int()[1]
})
print(coef_df.round(4).to_string())
print()

# Model Summary
print("─" * 60)
print("MODEL SUMMARY")
print("─" * 60)
print(f"R                    = {np.sqrt(model.rsquared):.4f}")
print(f"R-squared            = {model.rsquared:.4f}")
print(f"Adjusted R-squared   = {model.rsquared_adj:.4f}")
print(f"Std. Error of Est.   = {np.sqrt(model.mse_resid):.4f}")
print(f"F-statistic          = {model.fvalue:.4f}")
print(f"Prob (F-statistic)   = {model.f_pvalue:.6f}")
print(f"Durbin-Watson        = {sm.stats.stattools.durbin_watson(model.resid):.4f}")
print(f"AIC                  = {model.aic:.4f}")
print(f"BIC                  = {model.bic:.4f}")
print()

# Prediction
y_pred = model.predict(X)

# Residuals
print("─" * 60)
print("RESIDUAL STATISTICS")
print("─" * 60)
residuals = model.resid
print(f"Mean of Residuals         = {residuals.mean():.6f}")
print(f"Std. Dev. of Residuals    = {residuals.std():.4f}")
print(f"Min Residual              = {residuals.min():.4f}")
print(f"Max Residual              = {residuals.max():.4f}")
print()

# Shapiro-Wilk test for normality of residuals
shapiro_stat, shapiro_p = stats.shapiro(residuals)
print(f"Shapiro-Wilk Test (Normality of Residuals):")
print(f"  W-statistic = {shapiro_stat:.4f}, p-value = {shapiro_p:.4f}")
if shapiro_p > 0.05:
    print("  → Residuals are approximately normally distributed (p > 0.05)")
else:
    print("  → Residuals deviate from normality (p < 0.05)")
print()

# ─── Regression Equation ───
b0 = model.params['const']
b1 = model.params['Study_Hours']
print("─" * 60)
print("REGRESSION EQUATION")
print("─" * 60)
print(f"Exam_Score = {b0:.4f} + {b1:.4f} × Study_Hours")
print()
print(f"Interpretation:")
print(f"  • Intercept ({b0:.2f}): Predicted exam score when study hours = 0")
print(f"  • Slope ({b1:.2f}): For every additional hour of study,")
print(f"    the exam score increases by approximately {b1:.2f} points")
print()

# ─── Predictions for sample values ───
print("─" * 60)
print("SAMPLE PREDICTIONS")
print("─" * 60)
for hrs in [3, 6, 9, 12]:
    pred = b0 + b1 * hrs
    print(f"  If Study Hours = {hrs:2d}, Predicted Exam Score = {pred:.2f}")
print()

# ─────────────────────────────────────────────────────────────
# PLOTS for Regression
# ─────────────────────────────────────────────────────────────

# Plot 1: Scatter plot with regression line
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(study_hours, exam_scores, color='#2196F3', s=80, alpha=0.8,
           edgecolors='white', linewidth=1.5, zorder=5, label='Observed Data')
x_line = np.linspace(study_hours.min() - 0.5, study_hours.max() + 0.5, 100)
y_line = b0 + b1 * x_line
ax.plot(x_line, y_line, color='#E53935', linewidth=2.5, label=f'Regression Line\ny = {b0:.2f} + {b1:.2f}x', zorder=4)

# Confidence interval band
predictions = model.get_prediction(sm.add_constant(x_line))
pred_summary = predictions.summary_frame(alpha=0.05)
ax.fill_between(x_line, pred_summary['mean_ci_lower'], pred_summary['mean_ci_upper'],
                color='#E53935', alpha=0.15, label='95% Confidence Interval')

ax.set_xlabel('Study Hours per Week', fontsize=13, fontweight='bold')
ax.set_ylabel('Exam Score', fontsize=13, fontweight='bold')
ax.set_title('Simple Linear Regression: Study Hours vs Exam Score', fontsize=15, fontweight='bold', pad=15)
ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
ax.text(0.95, 0.05, f'R² = {model.rsquared:.4f}\nF = {model.fvalue:.2f}\np < 0.001',
        transform=ax.transAxes, fontsize=11, verticalalignment='bottom',
        horizontalalignment='right', bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_regression_scatter.png', bbox_inches='tight')
plt.close()
print("[Saved] 01_regression_scatter.png")

# Plot 2: Residual plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].scatter(y_pred, residuals, color='#FF7043', s=70, alpha=0.8, edgecolors='white', linewidth=1.2)
axes[0].axhline(y=0, color='#333', linestyle='--', linewidth=1.5)
axes[0].set_xlabel('Fitted Values', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Residuals', fontsize=12, fontweight='bold')
axes[0].set_title('Residuals vs Fitted Values', fontsize=13, fontweight='bold')

sm.qqplot(residuals, line='45', ax=axes[1], markerfacecolor='#7E57C2', markeredgecolor='white',
          markersize=7, alpha=0.8)
axes[1].set_title('Normal Q-Q Plot of Residuals', fontsize=13, fontweight='bold')
axes[1].get_lines()[0].set_color('#E53935')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_regression_residuals.png', bbox_inches='tight')
plt.close()
print("[Saved] 02_regression_residuals.png")


print()
print("=" * 80)
print("TOPIC 2: CORRELATION ANALYSIS")
print("=" * 80)
print()
print("Research Question:")
print("Is there a significant relationship between monthly advertising")
print("expenditure (in $1000s) and monthly sales revenue (in $1000s)?")
print()

# ─────────────────────────────────────────────────────────────
# DATASET: Advertising Expenditure vs Sales Revenue
# ─────────────────────────────────────────────────────────────

advertising = np.array([2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0,
                        7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0,
                        3.5, 5.0, 6.5, 8.0, 9.5, 11.0, 4.0, 7.0, 10.0, 12.5])

sales = np.array([22, 28, 31, 35, 38, 42, 45, 50, 53, 58,
                  60, 64, 67, 72, 75, 80, 83, 88, 91, 96,
                  33, 44, 55, 66, 76, 86, 37, 57, 79, 99])

df_corr = pd.DataFrame({
    'Advertising_Expenditure ($1000s)': advertising,
    'Sales_Revenue ($1000s)': sales
})

print("─" * 60)
print("DATASET: Advertising Expenditure vs Sales Revenue (n = 30)")
print("─" * 60)
print(df_corr.to_string(index=False))
print()

# Descriptive Statistics
print("─" * 60)
print("DESCRIPTIVE STATISTICS")
print("─" * 60)
print(df_corr.describe().round(4).to_string())
print()

# ─────────────────────────────────────────────────────────────
# CORRELATION ANALYSIS
# ─────────────────────────────────────────────────────────────

# Pearson Correlation
pearson_r, pearson_p = stats.pearsonr(advertising, sales)
print("─" * 60)
print("PEARSON CORRELATION COEFFICIENT")
print("─" * 60)
print(f"  Pearson r           = {pearson_r:.4f}")
print(f"  p-value             = {pearson_p:.6e}")
print(f"  R² (Coeff. of Det.) = {pearson_r**2:.4f}")
print(f"  N                   = {len(advertising)}")
print()

# Spearman Rank Correlation
spearman_r, spearman_p = stats.spearmanr(advertising, sales)
print("─" * 60)
print("SPEARMAN RANK CORRELATION COEFFICIENT")
print("─" * 60)
print(f"  Spearman ρ (rho)    = {spearman_r:.4f}")
print(f"  p-value             = {spearman_p:.6e}")
print(f"  N                   = {len(advertising)}")
print()

# Kendall Tau Correlation
kendall_tau, kendall_p = stats.kendalltau(advertising, sales)
print("─" * 60)
print("KENDALL TAU CORRELATION COEFFICIENT")
print("─" * 60)
print(f"  Kendall τ (tau)     = {kendall_tau:.4f}")
print(f"  p-value             = {kendall_p:.6e}")
print(f"  N                   = {len(advertising)}")
print()

# Correlation Matrix
print("─" * 60)
print("CORRELATION MATRIX (Pearson)")
print("─" * 60)
corr_matrix = df_corr.corr()
print(corr_matrix.round(4).to_string())
print()

# Hypothesis Testing
print("─" * 60)
print("HYPOTHESIS TEST FOR PEARSON CORRELATION")
print("─" * 60)
n = len(advertising)
t_stat = pearson_r * np.sqrt((n - 2) / (1 - pearson_r**2))
df_t = n - 2
p_val_two_tail = 2 * (1 - stats.t.cdf(abs(t_stat), df_t))
print(f"  H₀: ρ = 0 (No linear correlation)")
print(f"  H₁: ρ ≠ 0 (Significant linear correlation)")
print(f"  Significance level α = 0.05")
print(f"")
print(f"  t-statistic         = {t_stat:.4f}")
print(f"  Degrees of freedom  = {df_t}")
print(f"  p-value (two-tail)  = {p_val_two_tail:.6e}")
print(f"  Critical t (α=0.05) = ±{stats.t.ppf(0.975, df_t):.4f}")
print()
if p_val_two_tail < 0.05:
    print(f"  DECISION: Reject H₀ (p = {p_val_two_tail:.2e} < 0.05)")
    print(f"  CONCLUSION: There is a statistically significant linear")
    print(f"  correlation between Advertising Expenditure and Sales Revenue.")
else:
    print(f"  DECISION: Fail to Reject H₀ (p = {p_val_two_tail:.4f} > 0.05)")
print()

# Strength Interpretation
print("─" * 60)
print("INTERPRETATION OF CORRELATION STRENGTH")
print("─" * 60)
abs_r = abs(pearson_r)
if abs_r >= 0.9:
    strength = "Very Strong"
elif abs_r >= 0.7:
    strength = "Strong"
elif abs_r >= 0.5:
    strength = "Moderate"
elif abs_r >= 0.3:
    strength = "Weak"
else:
    strength = "Very Weak / Negligible"
direction = "Positive" if pearson_r > 0 else "Negative"
print(f"  |r| = {abs_r:.4f} → {strength} {direction} Correlation")
print(f"  R²  = {pearson_r**2:.4f} → {pearson_r**2*100:.2f}% of variance in Sales")
print(f"         is explained by Advertising Expenditure.")
print()

# ─────────────────────────────────────────────────────────────
# PLOTS for Correlation
# ─────────────────────────────────────────────────────────────

# Plot 3: Scatter plot for correlation
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(advertising, sales, color='#43A047', s=90, alpha=0.85,
           edgecolors='white', linewidth=1.5, zorder=5, label='Observed Data')

# Add trend line
z = np.polyfit(advertising, sales, 1)
p_line = np.poly1d(z)
x_trend = np.linspace(advertising.min() - 0.5, advertising.max() + 0.5, 100)
ax.plot(x_trend, p_line(x_trend), color='#FF6F00', linewidth=2.5, linestyle='--',
        label=f'Trend Line', zorder=4)

ax.set_xlabel('Advertising Expenditure ($1000s)', fontsize=13, fontweight='bold')
ax.set_ylabel('Sales Revenue ($1000s)', fontsize=13, fontweight='bold')
ax.set_title('Correlation: Advertising Expenditure vs Sales Revenue', fontsize=15, fontweight='bold', pad=15)
ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
ax.text(0.95, 0.05,
        f'Pearson r = {pearson_r:.4f}\nSpearman ρ = {spearman_r:.4f}\np < 0.001',
        transform=ax.transAxes, fontsize=11, verticalalignment='bottom',
        horizontalalignment='right', bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', alpha=0.9))
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_correlation_scatter.png', bbox_inches='tight')
plt.close()
print("[Saved] 03_correlation_scatter.png")

# Plot 4: Correlation Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr_matrix.values, cmap='RdYlGn', vmin=-1, vmax=1)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Correlation Coefficient', fontsize=12)
labels = ['Advertising\nExpenditure', 'Sales\nRevenue']
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(labels, fontsize=11)
ax.set_yticklabels(labels, fontsize=11)
for i in range(2):
    for j in range(2):
        ax.text(j, i, f'{corr_matrix.values[i, j]:.4f}', ha='center', va='center',
                fontsize=14, fontweight='bold',
                color='white' if abs(corr_matrix.values[i, j]) > 0.7 else 'black')
ax.set_title('Correlation Matrix Heatmap', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_correlation_heatmap.png', bbox_inches='tight')
plt.close()
print("[Saved] 04_correlation_heatmap.png")

# Plot 5: Joint Distribution Plot (Histogram + Scatter)
fig, axes = plt.subplots(2, 2, figsize=(12, 10),
                         gridspec_kw={'height_ratios': [1, 3], 'width_ratios': [3, 1]})

# Top histogram
axes[0, 0].hist(advertising, bins=10, color='#43A047', alpha=0.7, edgecolor='white')
axes[0, 0].set_ylabel('Frequency', fontsize=10)
axes[0, 0].set_title('Distribution of Advertising Expenditure', fontsize=11, fontweight='bold')
axes[0, 0].tick_params(labelbottom=False)

# Remove top-right
axes[0, 1].axis('off')

# Main scatter
axes[1, 0].scatter(advertising, sales, color='#43A047', s=80, alpha=0.8, edgecolors='white', linewidth=1.2)
axes[1, 0].plot(x_trend, p_line(x_trend), color='#FF6F00', linewidth=2, linestyle='--')
axes[1, 0].set_xlabel('Advertising Expenditure ($1000s)', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Sales Revenue ($1000s)', fontsize=12, fontweight='bold')

# Right histogram
axes[1, 1].hist(sales, bins=10, color='#1976D2', alpha=0.7, edgecolor='white', orientation='horizontal')
axes[1, 1].set_xlabel('Frequency', fontsize=10)
axes[1, 1].set_title('Sales\nDist.', fontsize=10, fontweight='bold')
axes[1, 1].tick_params(labelleft=False)

fig.suptitle('Joint Distribution: Advertising vs Sales', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_joint_distribution.png', bbox_inches='tight')
plt.close()
print("[Saved] 05_joint_distribution.png")

print()
print("=" * 80)
print("ALL ANALYSES COMPLETE. Output plots saved to:", OUTPUT_DIR)
print("=" * 80)
