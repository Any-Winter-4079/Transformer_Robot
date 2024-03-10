import re

#################
# Description   #
#################
# This is a script to compare the prediction results from two files.
# You may want to compare both different methods, such as CoT and Declarative, and the same method with different seeds.
# The interest is in whether different methods help solve different problems or if using different seeds is enough.
# For example, I expected CoT to struggle with the same problems using different seeds, but I observed:

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

# Which means we could theoretically improve the predictions up to >=0.7 accuracy where CoT with 1 seed sits at ~0.58.
# This is of course, if we have a decider tbat can choose the best prediction from the two methods.

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

# Function to read and extract questions and results from a file
def read_and_extract_questions_and_results(file_path):
    """Read and extract questions and results from a file."""
    with open(file_path, 'r') as file:
        content = file.read()
    questions_and_results = re.findall(r"Question \d+\n-------------\n(.*?)\n.*?Result \d+\n-------------\n(.*?)\n", content, re.DOTALL)
    return {question.strip(): result.strip() for question, result in questions_and_results}

# Function to compare the prediction results
def compare_predictions(file_1_data, file_2_data):
    """Compare the prediction results from two files."""
    correct_in_both, correct_in_file_1_only, correct_in_file_2_only, incorrect_in_both = 0, 0, 0, 0
    for question, result_1 in file_1_data.items():
        if question in file_2_data:
            result_2 = file_2_data[question]
            if result_1 == "Correct" and result_2 == "Correct":
                correct_in_both += 1
            elif result_1 == "Correct" and result_2 == "Incorrect":
                correct_in_file_1_only += 1
            elif result_1 == "Incorrect" and result_2 == "Correct":
                correct_in_file_2_only += 1
            elif result_1 == "Incorrect" and result_2 == "Incorrect":
                incorrect_in_both += 1
    return correct_in_both, correct_in_file_1_only, correct_in_file_2_only, incorrect_in_both

file_1_path = "../../../LLM/results/mixtral-8x7b-instruct-q50_GSM8K_2024-03-09_08-49-58_seed_1337_CoT_all samples.txt"
file_2_path = "../../../LLM/results/mixtral-8x7b-instruct-q50_GSM8K_2024-03-09_01-41-48_seed_1337_Dec8MP_Own_all samples.txt"

file_1_data = read_and_extract_questions_and_results(file_1_path)
file_2_data = read_and_extract_questions_and_results(file_2_path)

results_comparison = compare_predictions(file_1_data, file_2_data)

labels = ["Correct in both files", "Correct in file 1 only", "Correct in file 2 only", "Incorrect in both files"]
for label, count in zip(labels, results_comparison):
    print(f"{label}: {count}")
