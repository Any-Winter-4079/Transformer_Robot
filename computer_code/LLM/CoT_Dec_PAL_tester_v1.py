import os
import re
import time
import string
import tempfile
import subprocess
import numpy as np
from llama_cpp import Llama
from datetime import datetime
from datasets import load_dataset
from sympy import solve, sympify, Symbol
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

#################
# Description   #
#################
# This script tests the LLM on the GSM8K dataset using the Chain of Thought, Program-aided Language Models, and Declarative methods.
# To run the LLM, the script uses the Llama C++ library and the Llama Python wrapper.
# https://github.com/ggerganov/llama.cpp
# https://github.com/abetlen/llama-cpp-python

# The script is a bit chaotic (in particular, commented vs. uncommented code),
# and could be improved. It is only kept for reproducibility of the /results folder.
# Some breaking changes are going to be made, such as removing the ability to concatenate several
# method exemplars into a single prompt, moving towards a more modular approach,
# so I decided to keep this script as is for reproducibility.

# Some explanations that might help:
# You can change the MODELS and CONTEXT_WINDOWS dictionaries to test different models.
# MODELS_TO_TEST is a subset of the MODELS dictionary keys, in particular those you want to test.

# SEED affects the order of the samples in the dataset as well as the behavior of the LLM.
# Regarding the LLM, different seeds will generate different answers.
# Only 1 seed is used (meaning this script is not designed to change seed mid-execution to ask for more LLM samples)

# You can set SPLIT to "train" to test the effect of exemplar changes (even adding the LLM predictions
# on them to the exemplars, e.g. as negative exemplars if the LLM did not generate a correct answer).
# Once you are happy with the exemplars, you can test the LLM on the "test" split.

# The results are saved after the execution of the tests in /results. Be careful, because nothing is saved
# until the full dataset (or N_SAMPLES) is processed.

# Code execution is stopped if it takes more than PAL_TIMEOUT (for example, if the LLM creates an infinite loop).
# This does not cause any problem to the tests.

# Exemplars are loaded from the EXEMPLARS_PATHS dictionary. METHODS defines which methods to test (for which
# exemplars will be loaded). This works in a similar fashion to MODELS and MODELS_TO_TEST.
# Exemplars work well on their own, but they may not be very coherent for concatenation, which is what
# construct_prompt allows for. In other words, if you choose METHODS = ["CoT", "PAL"], make sure
# your "CoT" and "PAL" exemplars being concatenated make sense, for example.
# In the exemplars folder, you can see some are 8-shot, some are 4-shot, some are 4-shot positive and
# 4-shot negative, some ask the LLM to answer within the file itself, which is why if you concatenate
# I'd suggest you to create a new exemplars file per method you want to concatenate
# (to ask the LLM to generate solutions in ALL formats in the same
# reply or to choose one and generate the response, also in a single reply).

#################
# Configuration #
#################
MODEL_BASE_PATH = "llama.cpp/models/" # Path to the LLM models
MODELS = {
    "llama-7b-q4_0": MODEL_BASE_PATH + "7b/ggml-model-q4_0.bin",
    "llama-7b-f16": MODEL_BASE_PATH + "7b/ggml-model-f16.bin",
    "llama-13b-q4_0": MODEL_BASE_PATH + "13b/ggml-model-q4_0.bin",
    "llama-7b-chat-q4_0": MODEL_BASE_PATH + "7b-chat/ggml-model-q4_0.bin",
    "llama-13b-chat-q4_0": MODEL_BASE_PATH + "13b-chat/ggml-model-q4_0.bin",
    "mixtral-8x7b-instruct-q8_0": MODEL_BASE_PATH + "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-v0.1.Q8_0.gguf",
    "mixtral-8x7b-instruct-q5_0": MODEL_BASE_PATH + "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-q5_0.gguf",
    "mixtral-8x7b-instruct-Q4_K_M": MODEL_BASE_PATH + "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-Q4_K_M.gguf",
    "mixtral-8x7b-instruct-Q3_K_M": MODEL_BASE_PATH + "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-Q3_K_M.gguf",
    "mistral-7b-instruct-v0.2.Q8_0": MODEL_BASE_PATH + "mistral-7b-instruct-v0.2/mistral-7b-instruct-v0.2.Q8_0.gguf",
    "70b-code-q4": MODEL_BASE_PATH + "70b-code/codellama-70b-python.Q4_K_M.gguf",
    "tora-13b": MODEL_BASE_PATH + "tora-13b-v1.0/tora-13b-v1.0.Q5_K_M.gguf",
    "deepseek-coder-33B-instruct-Q5_K_M": MODEL_BASE_PATH + "deepseek-coder-33B-instruct/deepseek-coder-33b-instruct.Q5_K_M.gguf",
    "deepseek-math-7b-instruct-Q4_K_M": MODEL_BASE_PATH + "deepseek-math-7b-instruct/deepseek-math-7b-instruct.Q4_K_M.gguf",
    "deepseek-llm-67b-chat-Q4_K_M": MODEL_BASE_PATH + "deepseek-llm-67b-chat/deepseek-llm-67b-chat.Q4_K_M.gguf",
}
CONTEXT_WINDOWS = {
    "llama-7b-q4_0": 4096,
    "llama-7b-f16": 4096,
    "llama-13b-q4_0": 4096,
    "llama-7b-chat-q4_0": 4096,
    "llama-13b-chat-q4_0": 4096,
    "mixtral-8x7b-instruct-q8_0": 32768,
    "mixtral-8x7b-instruct-q5_0": 32768,
    "mixtral-8x7b-instruct-Q4_K_M": 32768,
    "mixtral-8x7b-instruct-Q3_K_M": 32768,
    "mistral-7b-instruct-v0.2.Q8_0": 4096,
    "70b-code-q4": 4096,
    "tora-13b": 4096,
    "deepseek-coder-33B-instruct-Q5_K_M": 16384,
    "deepseek-math-7b-instruct-Q4_K_M": 4096,
    "deepseek-llm-67b-chat-Q4_K_M": 4096,
}
SEED = 1337
SPLIT = "test" # Use the test set
GSM8K = load_dataset("gsm8k", "socratic")
EXEMPLARS_PATHS = {
    "PAL": "exemplars/GSM8k_Program_Aided_LM_Principles.txt", # Program-aided Language Models [https://arxiv.org/pdf/2211.10435.pdf]
    "CoT": "exemplars/GSM8K_Chain_of_Thought_8-shot.txt", # Chain of Thought
    "Dec8": "exemplars/GSM8K_Declarative_8-shot.txt", # Declarative (SymPy)
    "Dec3P": "exemplars/GSM8K_Declarative_3-shot_Principles.txt", # Declarative (SymPy)
    "Dec4MP": "exemplars/GSM8K_Declarative_4-shot_More_Principles.txt", # Declarative (SymPy)
    "Dec8MP_Own": "exemplars/GSM8K_Declarative_8-shot_More_Principles_Own.txt", # Declarative (SymPy)
    "Dec8MP_Own_multi": "exemplars/GSM8K_Declarative_8-shot_More_Principles_Own_3.txt", # Declarative (SymPy)
}
SAVE_FOLDER = "./results"
MAX_TOKENS = 1024 # Maximum output length for the LLM

MODELS_TO_TEST = ["mixtral-8x7b-instruct-q5_0"] # Models to test, in case you don't want to test all of them
N_SAMPLES = 300 # None for all samples
METHODS = ["PAL"] # Methods to test
PAL_TIMEOUT = 5 # Timeout for the PAL method

# Create the save folder if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Function to load the exemplar contents for the specified methods
def load_exemplars():
    """Load exemplar contents for the specified methods."""
    exemplar_contents = {}
    for method in METHODS:
        if method in EXEMPLARS_PATHS:
            with open(EXEMPLARS_PATHS[method], 'r') as file:
                if "Dec" in method:
                    exemplar_contents["Dec"] = file.read()
                elif "CoT" in method:
                    exemplar_contents["CoT"] = file.read()
                elif "PAL" in method:
                    exemplar_contents["PAL"] = file.read()
    return exemplar_contents

# Function to construct a prompt using the loaded exemplar contents
def construct_prompt(exemplar_contents):
    """Construct a prompt using the loaded exemplar contents"""
    sections = []
    if len(METHODS) > 1:
        sections.append("###########\n# Instructions #\n###########\n" + "Solve the problems below using only one of the described methods, the one you think is more appropriate:\n")
    if "CoT" in exemplar_contents:
        if len(METHODS) > 1:
            sections.append("###########\n# CoT method #\n###########\n")
        sections.append(exemplar_contents["CoT"])
    if "Dec" in exemplar_contents:
        if len(METHODS) > 1:
            sections.append("###########\n# Declarative method #\n###########\n")
        sections.append(exemplar_contents["Dec"])
    if "PAL" in exemplar_contents:
        if len(METHODS) > 1:
            sections.append("###########\n# PAL method #\n###########\n")
        sections.append(exemplar_contents["PAL"])

    if len(METHODS) > 1:
        sections.append("###########\n# Problems #\n###########\n")
    return "\n".join(sections)

# Function to execute the PAL code with a timeout using the subprocess module
def run_code_with_subprocess_timeout(code, timeout=PAL_TIMEOUT):
    """Execute the PAL code with a timeout using the subprocess module."""
    code = code + '\nprint(solution())'
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w+') as temp_script:
        temp_script_name = temp_script.name
        temp_script.write(code)
    try:
        completed_process = subprocess.run(['python', temp_script_name], 
                                           capture_output=True, text=True, timeout=timeout)
        if completed_process.returncode == 0:
            return completed_process.stdout.strip()
        else:
            return f"Error: {completed_process.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Execution timed out"
    except Exception as e:
        return f"Execution failed: {str(e)}"
    finally:
        os.remove(temp_script_name)

# Function to test the LLM on the GSM8K dataset
def test_gsm8k():
    """Test the LLM on the GSM8K dataset using the Chain of Thought, Program-aided Language Models, or Declarative methods."""
    start_time = time.time() # Start time for the test
    data_to_save = [] # Data to save to file
    n_correct = 0 # Number of correct predictions

    # Load the exemplars for the method as the context
    context = load_exemplars()

    # Select either a subset or the entire dataset
    if N_SAMPLES is None or N_SAMPLES > len(GSM8K[SPLIT]):
        dataset_to_iterate = GSM8K[SPLIT].shuffle(seed=SEED)
    else:
        dataset_to_iterate = GSM8K[SPLIT].shuffle(seed=SEED).select(range(N_SAMPLES))
    
    # Loop through a random (seeded) (sub)set of GSM8K
    for idx, example in enumerate(dataset_to_iterate, start=1):
        print(f"Processing sample {idx}...")
        # Extract the question and answer and format the answer
        # For example, 1000, 1,000, 1000.00, etc. -> 1,000.00
        question = example["question"] # GSM8K question to be answered
        answer = example["answer"] # GSM8K answer with explanation
        concise_answer = extract_and_format_value(answer.split("####")[-1].strip()) # GSM8K numerical answer

        # Run the LLM with the question and context
        message = construct_prompt(context)
        message = f"{message}\nQ: {question}\nA: " # TODO: Try other model-specific prompts
        prediction = run_llm(message)
        concise_prediction = None
        if any(method.startswith("Dec") for method in METHODS) and "[[answer" in prediction: # Declarative [https://arxiv.org/pdf/2304.09102.pdf]
            eq_list = get_declarative_equations(prediction)
            print(f"\tDec: {eq_list}")
            predicted_answer = get_final_using_sympy(eq_list)
            if predicted_answer in ["invalid equations", "no goal found", "no solution", "bug"]:
                concise_prediction = "bug"
            else:
                concise_prediction = extract_and_format_value(predicted_answer)
            print("\tDec:", concise_prediction)
            prediction = f"{prediction}\n#### {concise_prediction}"
        elif any(method.startswith("PAL") for method in METHODS) and "def solution():" in prediction: # Program-aided Language Models [https://arxiv.org/pdf/2211.10435.pdf]
            try:
                print(f"\tPAL: {prediction}")
                predicted_answer = run_code_with_subprocess_timeout(prediction)
            except Exception as e:
                print(f"\tError in PAL: {e}")
                predicted_answer = "bug"
            predicted_answer = extract_and_format_value(predicted_answer)
            concise_prediction = extract_and_format_value(predicted_answer)
            print("\tPAL:", concise_prediction)
            prediction = f"{prediction}\n#### {concise_prediction}"
        elif any(method.startswith("CoT") for method in METHODS): # Chain of Thought [https://arxiv.org/pdf/2201.11903.pdf]
            predicted_answer = prediction.split("The answer is ")[-1].strip()
            predicted_answer = extract_and_format_value(predicted_answer)
            print("\tCoT:", predicted_answer)
            concise_prediction = extract_and_format_value(predicted_answer)

        if concise_prediction == concise_answer:
            result = "Correct"
            n_correct += 1
        else:
            result = "Incorrect"

        data_to_save.append({
            "index": idx,
            "question": question,
            "answer": answer,
            "concise_answer": concise_answer,
            "prediction": prediction,
            "concise_prediction": concise_prediction,
            "result": result
        })

    datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    samples = "all samples" if N_SAMPLES is None else "1 sample" if N_SAMPLES == 1 else f"{N_SAMPLES} samples"
    method_names = "_".join(METHODS)
    save_path = f"{SAVE_FOLDER}/{MODEL_NAME}_GSM8K_{datetime_str}_seed_{SEED}_{method_names}_{samples}.txt"

    save_results(data_to_save, save_path, start_time, n_correct)

# Function to run the LLM with the given message 
def run_llm(message):
    """Run the LLM with the given message."""
    try:
        llm_output = LLM(
            message,
            max_tokens=MAX_TOKENS, # Set to None to generate up to the end of the context window
            stop=["Q:"], # Stop generating just before the model would generate a new question or decides to use a tool
            echo=False # Echo the prompt back in the output. Useful for debugging but False for PAL and SymPy
        )
        return llm_output['choices'][0]['text'].strip()
    except Exception as e:
        print(f"run_llm: {e}")
        return "-1"

# Function to save the results to a file
def save_results(data_to_save, save_path, start_time, n_correct):
    """Save the results to a file."""
    with open(save_path, "w") as file:
        for item in data_to_save:
            sections = [
                ("Question", item["question"]),
                ("Answer", item["answer"]),
                ("Concise answer", item["concise_answer"]),
                ("Prediction", item["prediction"]),
                ("Concise prediction", item["concise_prediction"]),
                ("Result", item["result"])
            ]
            for section_title, section_content in sections:
                file.write("-------------\n")
                file.write(f"{section_title} {item['index']}\n")
                file.write("-------------\n")
                file.write(f"{section_content}\n\n")

        end_time = time.time()
        file.write(f"Time: {(end_time - start_time):.2f} seconds\n")
        n_samples = len(data_to_save)
        file.write(f"Accuracy: {n_correct / n_samples:.3f}\n")

# (start of) https://github.com/joyheyueya/declarative-math-word-problem.git (adapted)
# Function to simplify the variables longer than one character in the equations
def simplify_variables(equations):
    """Simplify the variables longer than one character in the equations."""
    var_names = set(re.findall(r'\b[a-zA-Z_]\w*\b', equations))
    long_var_names = [var for var in var_names if len(var) > 1]
    
    unused_chars = [chr(i) for i in range(97, 123) if chr(i) not in var_names]  # a-z
    var_mapping = {var: unused_chars.pop(0) for var in long_var_names}
    
    for long_var, short_var in var_mapping.items():
        equations = re.sub(r'\b{}\b'.format(long_var), short_var, equations)
    
    return equations, var_mapping

# Function to clean the equation text
def clean_equation_text(equation_text):
    """Clean the equation text."""
    cleaned_equation_text = re.sub(r'[^\w\s=+\-*/()0-9.\[\]]', '', equation_text)
    return cleaned_equation_text

def reformat_incre_equations(x):
    result = ''
    if len(x) >= 1:
        for eq in x:
            if len(result) == 0:
                result += eq[2 : -2]
            else:
                result += ', ' + eq[2 : -2]
    return result

def reformat_equations_from_peano(eq_list):
    result = ''
    for eq in eq_list.split(','):
        if 'eq' in eq:
            if len(result) == 0:
                result += eq[eq.index('eq') + 2:]
            else:
                result += ', ' + eq[eq.index('eq') + 2:]
        elif 'answer' in eq:
            if len(result) == 0:
                result += eq[eq.index('answer') + 6:].strip() + ' = ?'
            else:
                result += ', ' + eq[eq.index('answer') + 6:].strip() + ' = ?'     
    return result

def get_declarative_equations(prediction):
    eq_list = re.findall(r'\[\[.*?\]\]', prediction)
    
    cleaned_eq_list = []
    
    if len(eq_list) > 0:
        for eq in eq_list:
            cleaned_eq = clean_equation_text(eq)
            cleaned_eq_list.append(cleaned_eq)
        
        return reformat_equations_from_peano(reformat_incre_equations(cleaned_eq_list))
    else:
        return prediction

def get_final_using_sympy(equations):
    try:
        equations, var_mapping = simplify_variables(equations)
        transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
        if str(equations) == 'nan':
            return np.nan
        equation_list = equations.split(',')
        for eq in equation_list:
            for c in range(len(eq)):
                if c < len(eq) - 2:
                    if eq[c].isalpha() and eq[c+1].isalpha() and eq[c+2].isalpha():
                        return 'invalid equations'

        goal_var = None
        goal_expression_list = []
            
        if equation_list[-1].split('=')[0].strip().isalpha() or len(equation_list[-1].split('=')[0].strip()) == 2:
            goal_var = equation_list[-1].split('=')[0].strip()
        elif '=' in equation_list[-1]:
            for l in list(string.ascii_lowercase) + list(string.ascii_uppercase):
                if l not in equation_list[-1]:
                    goal_var = l
                    break
            if goal_var is not None:
                goal_expression = goal_var + ' - (' + equation_list[-1].split('=')[0].strip() + ')'
                goal_expression = parse_expr(goal_expression, transformations=transformations)
                goal_expression = sympify(goal_expression)
                try:
                    return float(solve(goal_expression)[0])
                except Exception as e:
                    pass
                goal_expression_list.append(goal_expression)
            else:
                return 'invalid equations'

        if len(equation_list) == 1:
            try:
                goal_expression = parse_expr(equation_list[0].split('=')[0], transformations=transformations)
                return float(sympify(goal_expression))
            except Exception as e:
                return 'invalid equations'

        if goal_var == None:
            return 'no goal found'

        for i in range(len(equation_list) - 1):
            sub_eqs = equation_list[i]  
            if '?' not in sub_eqs:
                try:    
                    sub_eqs_split = sub_eqs.split('=')
                    sub_eqs = sub_eqs_split[0].strip() + ' - (' + sub_eqs_split[1].strip() + ')'
                    sub_eqs = parse_expr(sub_eqs, transformations=transformations)
                    sub_eqs = sympify(sub_eqs)
                except Exception as e:
                    return 'invalid equations'
                goal_expression_list.append(sub_eqs)

                try:
                    try:
                        return float(solve(goal_expression_list)[Symbol(goal_var)])
                    except Exception as e:
                        return float(solve(goal_expression_list)[0][Symbol(goal_var)])
                except Exception as e:
                    pass

        return 'no solution'
    except Exception as e:
        print(e)
        return 'bug'
# (end of) https://github.com/joyheyueya/declarative-math-word-problem.git (adapted)

# Function to extract and format the numerical value from a string
def extract_and_format_value(input_value):
    """Extract and format the numerical value from a string."""
    if not isinstance(input_value, str):
        input_value = str(input_value)
    
    reversed_input = input_value[::-1]
    numeric_part_reversed = ""
    found_digit = False
    
    for char in reversed_input:
        if char.isdigit() or (char == '.' and found_digit):
            found_digit = True
            numeric_part_reversed += char
        elif char == ',' and found_digit:
            continue
        elif char == '-' and found_digit:
            numeric_part_reversed += char
            break
        elif found_digit:
            break
    
    numeric_part = numeric_part_reversed[::-1]
    
    try:
        formatted_value = "{:,.2f}".format(float(numeric_part.replace(',', '')))
        return formatted_value
    except ValueError:
        return "bug"

if __name__ == "__main__":
    for MODEL_NAME in MODELS_TO_TEST:
        CONTEXT_WINDOW = CONTEXT_WINDOWS[MODEL_NAME]
        MODEL = MODELS[MODEL_NAME]
        LLM = Llama(
            model_path=MODEL,
            n_gpu_layers=-1,
            seed=SEED,
            verbose=False,
            n_ctx=CONTEXT_WINDOW,
        )
        test_gsm8k()
#     prompt =  """
# Teresa sells large stuffed animals for three times the price of small stuffed animals. [[eq price_large = 3 * price_small]].
# Today, she sold twice as many small stuffed animals as large ones. [[eq small_sold = 2 * large_sold]].
# Earned $120 from the sales [[eq total_earned = price_small * small_sold + price_large * large_sold]].
# Each small stuffed animal costs $4 [[eq price_small = 4]]. [[eq total_earned = 120]]
# How many small stuffed animals did she sell? The answer is [[eq small_sold]].
# [[answer small_sold]]."""
#     eq_list = get_declarative_equations(prompt)
#     print(eq_list)
#     predicted_answer = get_final_using_sympy(eq_list)
#     print(predicted_answer)
