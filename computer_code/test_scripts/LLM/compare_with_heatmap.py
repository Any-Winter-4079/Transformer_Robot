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

results_matrix = np.array([[528, 254], [227, 310]])

cot_labels = ["Correct in\n8-shot CoT", "Incorrect in\n8-shot CoT"]
declarative_labels = ["Correct in\n8-shot (4 pos & 4 neg)\n+ 8 principles Declarative\n(own prompt, adapted code)",
                      "Incorrect in\n8-shot (4 pos & 4 neg)\n+ 8 principles Declarative\n(own prompt, adapted code)"]

cmap = mcolors.LinearSegmentedColormap.from_list("custom", ["#FFB347", "#387761"], N=256)

plt.figure(figsize=(10, 8))
sns.heatmap(
    results_matrix,
    annot=True,
    fmt="d",
    cmap=cmap,
    xticklabels=declarative_labels,
    yticklabels=cot_labels)

plt.title('Mixtral-8x7b-instruct-Q5_0: CoT & Declarative overlap', fontsize=14)

plt.tight_layout()

plt.show()
