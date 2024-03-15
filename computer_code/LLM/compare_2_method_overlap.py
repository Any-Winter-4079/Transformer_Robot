import re

# Function to read and extract questions and results from a (results) file
def read_and_extract_questions_and_results(file_path):
    """Read and extract questions and results from a (results) file."""
    with open(file_path, 'r') as file:
        content = file.read()
    questions_and_results = re.findall(r"Question \d+\n-------------\n(.*?)\n.*?Result \d+\n-------------\n(.*?)\n", content, re.DOTALL)
    return {question.strip(): result.strip() for question, result in questions_and_results}

# Function to compare the prediction results from two (results) files
def compare_predictions(file_1_data, file_2_data):
    """Compare the prediction results from two (results) files."""
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

file_1_path = "./results/mixtral-8x7b-instruct-q50_GSM8K_2024-03-09_22-23-54_seed_966_CoT_all samples.txt"
file_2_path = "./results/mixtral-8x7b-instruct-q50_GSM8K_2024-03-06_23-09-31_seed_1337_CoT_all samples.txt"

file_1_data = read_and_extract_questions_and_results(file_1_path)
file_2_data = read_and_extract_questions_and_results(file_2_path)

results_comparison = compare_predictions(file_1_data, file_2_data)

labels = ["Correct in both files", "Correct in file 1 only", "Correct in file 2 only", "Incorrect in both"]
for label, count in zip(labels, results_comparison):
    print(f"{label}: {count}")
