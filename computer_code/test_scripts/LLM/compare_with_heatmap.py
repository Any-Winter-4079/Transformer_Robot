import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

#################
# Description   #
#################
# This script visually compares the prediction results from two files.

# seed_966 and seed_1337
# Correct in both files: 589
# Correct in file 1 only: 184
# Correct in file 2 only: 193
# Incorrect in both files: 353

# seed_966 and seed_7625
# Correct in both files: 586
# Correct in file 1 only: 187
# Correct in file 2 only: 204
# Incorrect in both files: 342

# seed_1337 and seed_7625
# Correct in both files: 604
# Correct in file 1 only: 178
# Correct in file 2 only: 186
# Incorrect in both files: 351

# Which means we could theoretically improve the predictions up to >=0.7 accuracy where CoT with a single seed sits at ~0.58.
# This is of course if we have a decider capable of choosing the best prediction from the two methods.

# While comparing CoT and Declarative, I observed:
# seed_1337 and seed_1337
# Correct in both files: 528
# Correct in file 1 only: 254
# Correct in file 2 only: 227
# Incorrect in both files: 310

# Resulting in more diversity, but not by a large margin, which I found surprising.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

results_matrix = np.array([[604, 178], [186, 351]])

# y_labels = ["Correct in\n8-shot CoT", "Incorrect in\n8-shot CoT"]
# y_labels = ["Correct in 8-shot \nCoT (seed: 966)", "Incorrect in 8-shot \nCoT (seed: 966)"]
# y_labels = ["Correct in 8-shot \nCoT (seed: 966)", "Incorrect in 8-shot \nCoT (seed: 966)"]
y_labels = ["Correct in 8-shot \nCoT (seed: 1337)", "Incorrect in 8-shot \nCoT (seed: 1337)"]

# x_labels = ["Correct in\n8-shot (4 pos & 4 neg)\n+ 8 principles Declarative\n(own prompt, adapted code)",
#             "Incorrect in\n8-shot (4 pos & 4 neg)\n+ 8 principles Declarative\n(own prompt, adapted code)"]
# x_labels = ["Correct in\n8-shot CoT (seed: 1337)", "Incorrect in\n8-shot CoT (seed: 1337)"]
# x_labels = ["Correct in\n8-shot CoT (seed: 7625)", "Incorrect in\n8-shot CoT (seed: 7625)"]
x_labels = ["Correct in\n8-shot CoT (seed: 7625)", "Incorrect in\n8-shot CoT (seed: 7625)"]

cmap = mcolors.LinearSegmentedColormap.from_list("custom", ["#FFB347", "#387761"], N=256)

plt.figure(figsize=(10, 8))
sns.heatmap(
    results_matrix,
    annot=True,
    fmt="d",
    cmap=cmap,
    xticklabels=x_labels,
    yticklabels=y_labels,
    annot_kws={'size': 16}  # Increase font size of the numbers
)

plt.title('Mixtral-8x7b-instruct-Q5_0: CoT overlap', fontsize=14)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.tight_layout()

plt.show()
