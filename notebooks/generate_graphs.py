"""Run notebook analysis and save graphs. Execute from project root."""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import json, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

os.makedirs('results/graphs', exist_ok=True)

with open('results/outputs.json') as f:
    outputs = json.load(f)

metrics = []
with open('results/evaluation_metrics.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        metrics.append(row)

sem_sims = [o['semantic_similarity_pct'] / 100 for o in outputs]
scores   = [o['predicted_score'] for o in outputs]
kw_covs  = [o['keyword_coverage_pct'] / 100 for o in outputs]
types    = [o['type'] for o in outputs]

type_colors = {
    'exact_match': 'green', 'paraphrased': 'blue',
    'partial_answer': 'orange', 'irrelevant_answer': 'red', 'mixed_correctness': 'purple'
}
colors = [type_colors.get(t, 'gray') for t in types]
patches = [mpatches.Patch(color=v, label=k) for k, v in type_colors.items()]

# Plot 1
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(sem_sims, scores, c=colors, s=100, edgecolors='black', linewidths=0.5)
ax.set_xlabel('Semantic Similarity'); ax.set_ylabel('Predicted Score')
ax.set_title('Semantic Similarity vs Predicted Score')
ax.legend(handles=patches, loc='upper left', fontsize=8); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig('results/graphs/similarity_vs_score.png', dpi=150); plt.close()

# Plot 2
predicted = [float(m['predicted_score']) for m in metrics]
human     = [float(m['human_score']) for m in metrics]
ids       = [m['id'] for m in metrics]
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot([0, 10], [0, 10], 'k--', alpha=0.4, label='Perfect agreement')
ax.scatter(human, predicted, color='steelblue', s=100, edgecolors='black', linewidths=0.5, zorder=5)
for i, txt in enumerate(ids):
    ax.annotate(txt, (human[i], predicted[i]), textcoords='offset points', xytext=(5, 5), fontsize=7)
ax.set_xlabel('Human Score'); ax.set_ylabel('Predicted Score')
ax.set_title('Predicted vs Human Scores')
ax.set_xlim(-0.5, 11); ax.set_ylim(-0.5, 11); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig('results/graphs/predicted_vs_human.png', dpi=150); plt.close()

# Plot 3
errors   = [float(m['absolute_error']) for m in metrics]
mean_err = np.mean(errors)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(range(len(errors)), errors, color='salmon', edgecolor='black', linewidth=0.5)
ax.axhline(mean_err, color='red', linestyle='--', label=f'Mean MAE = {mean_err:.2f}')
ax.set_xticks(range(len(errors))); ax.set_xticklabels(ids, rotation=30, ha='right', fontsize=8)
ax.set_ylabel('Absolute Error'); ax.set_title('Error Distribution')
ax.legend(); ax.grid(True, axis='y', alpha=0.3)
plt.tight_layout(); plt.savefig('results/graphs/error_distribution.png', dpi=150); plt.close()

# Plot 4
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(kw_covs, scores, c=colors, s=100, edgecolors='black', linewidths=0.5)
ax.set_xlabel('Keyword Coverage'); ax.set_ylabel('Predicted Score')
ax.set_title('Keyword Coverage vs Predicted Score')
ax.legend(handles=patches, loc='upper left', fontsize=8); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig('results/graphs/keyword_vs_score.png', dpi=150); plt.close()

print("Graphs saved to results/graphs/")
print(f"  similarity_vs_score.png")
print(f"  predicted_vs_human.png")
print(f"  error_distribution.png")
print(f"  keyword_vs_score.png")
