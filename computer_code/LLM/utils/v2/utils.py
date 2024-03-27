import os
import time
import random
import tempfile
import subprocess
from config.v2.config import *

# Function to load the exemplar contents for the specified methods
def load_exemplars():
    """Load exemplar contents for the specified methods."""
    exemplar_contents = {}
    for method_to_test in METHODS_TO_PICK_FROM:
        with open(EXEMPLARS_PATHS[method_to_test], 'r') as file:
            if "Decl" in method_to_test:
                exemplar_contents["Decl"] = file.read()
            elif "CoT" in method_to_test:
                exemplar_contents["CoT"] = file.read()
            elif "PAL" in method_to_test:
                exemplar_contents["PAL"] = file.read()
    if len(METHODS_TO_PICK_FROM) > 1:
        with open(DECIDER_PATH, 'r') as file:
            exemplar_contents["Decider"] =  file.read()
    return exemplar_contents

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

# Function to select the mode answer or sample an answer based on frequency
def select_mode_or_sample(unique_valid_concise):
    """Select the mode answer or sample an answer based on frequency."""
    concise_pred_frequencies = {concise: len(details) for concise, details in unique_valid_concise.items()}
    
    max_frequency = max(concise_pred_frequencies.values())
    modes = [concise for concise, freq in concise_pred_frequencies.items() if freq == max_frequency]
    
    if len(modes) == 1:
        mode = modes[0]
        print(f"\tDecider (mode): {mode}")
        return mode, "mode"
    else:
        # print("\tTie detected: resorting to sampling among modes.")
        weighted_modes = [mode for mode in modes for _ in range(concise_pred_frequencies[mode])]
        choice = random.choice(weighted_modes)
        print(f"\tDecider (sampling): {choice}")
        return choice, "sampling"

# Function to sample based on frequency
def sample_based_on_frequency(unique_valid_concise):
    """Sample an answer from unique_valid_concise based on its frequency, represented by the length of each value."""
    weighted_answers = [concise for concise, details in unique_valid_concise.items() for _ in range(len(details))]
    choice = random.choice(weighted_answers)
    print(f"\tDecider (sampling): {choice}")
    return choice, "sampling"

# Function to save the results to a file
def save_results(data_to_save, save_path, duration, n_correct):
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

        file.write(f"Time: {(duration):.2f} seconds\n")
        n_samples = len(data_to_save)
        file.write(f"Accuracy: {n_correct / n_samples:.3f}\n")

# Function to run the LLM with the given message 
def run_llm(message, stop_list, cpp=False, decider=False):
    """Run the LLM with the given message."""
    llm_outputs =  []
    iterations = 1 if decider else N_ITERATIONS
    durations = []
    for iteration in range(iterations):
        start_time = time.time()
        if not cpp:
            try:
                llm_output = llm(
                    message,
                    max_tokens=max_tokens, # Set to None to generate up to the end of the context window
                    stop=stop_list, # Stop generating just before the model would generate a new question
                    echo=False # Echo the prompt back in the output. Useful for debugging but False for PAL and SymPy
                )
                llm_outputs.append(llm_output['choices'][0]['text'].strip())
            except Exception as e:
                print(f"run_llm: {e}")
                llm_outputs.append("-1")
        else:
            try:
                # command_base = [
                #     "bash", "-c",
                #     f"cd {LLAMA_BASE_PATH} && make -j && ./main -m {str(MODEL_PATHS[MODEL_TO_TEST])} -n {max_tokens} -e -s {seed} --log-disable"
                # ]

                with tempfile.NamedTemporaryFile('w', delete=False) as temp_prompt_file:
                    temp_prompt_file.write(message)
                    temp_prompt_file_path = temp_prompt_file.name
                command = [
                    "bash", "-c",
                    f"{LLAMA_BASE_PATH}/main -m {str(MODEL_PATHS[MODEL_TO_TEST])} -n {max_tokens} -e -s {seed+iteration} -f {temp_prompt_file_path} -c {CONTEXT_WINDOWS[MODEL_TO_TEST]} -ngl -1 -r 'Q:' --prompt-cache prompt_cache_{MODEL_TO_TEST}"
                ]
                # command = [
                #     "bash", "-c",
                #     f"{LLAMA_BASE_PATH}/parallel -m {str(MODEL_PATHS[MODEL_TO_TEST])} -n {max_tokens} -s {seed+iteration} -f {temp_prompt_file_path} -c {CONTEXT_WINDOWS[MODEL_TO_TEST]} -ngl -1 -np 4 -ns 4 -cb -b 512 -r 'Q:' --prompt-cache prompt_cache"
                # ]
                # ./parallel -m models/mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-q5_0.gguf -n 1024 -t 1 -ngl -1 -c 1024 -b 512 -s 1 -np 4 -ns 4 -cb -p "Are you familiar with the Special Theory of Relativity and can you explain it to me?"

                result = subprocess.run(command, cwd=LLAMA_BASE_PATH, capture_output=True, text=True)
                result.stdout = result.stdout.replace(message, "").replace("Q:", "").strip()
                os.remove(temp_prompt_file_path)

                if result.returncode == 0:
                    llm_outputs.append(result.stdout)
                else:
                    print("Error executing command:", result.stderr)
                    llm_outputs.append("-1")
            except Exception as e:
                print(f"run_llm: {e}")
                llm_outputs.append("-1")
        end_time = time.time()
        durations.append(end_time - start_time)
    print("In " + f", ".join([f"{duration:.2f}s" for duration in durations]) + ":")
    return llm_outputs
