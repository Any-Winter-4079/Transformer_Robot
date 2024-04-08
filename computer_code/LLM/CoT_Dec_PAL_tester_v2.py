import os
import time
from datetime import datetime
from config.v2.config import *
from methods.v2.decider import run_decider
from methods.v2.program_aided_lm import run_pal
from methods.v2.chain_of_thought import run_cot
from methods.v2.declarative import run_declarative
from utils.v2.utils import extract_and_format_value, load_exemplars, save_results, select_mode_or_sample

#################
# Description   #
#################
# The script is v2 of the LLM tester for the GSM8K dataset, CoT_Dec_PAL_tester_v1.py.
# This version improves:
# CoT: 0.593 (1337 seed) -> 0.719 (1337 seed) using 5-iter SC (Self-Consistency) [Fastest per iteration].
# Dec: 0.553 (1337 seed) -> 0.572 (1337 seed) using more roubust SymPy equations extraction.
# PAL: 0.679 (1337 seed) -> 0.782 (1337 seed) using 5-iter SC (Self-Consistency) [Best result].
# You can choose one or more methods to test, each with one or more iterations (seeds) using SC.
# For example, you can test the PAL method with 5 iterations (seeds) using SC, or the PAL method with 3 iterations (seeds)
# and the CoT method with 2 iterations (seeds) using SC.
# Dec(with Simpy) is not tested with SC in my results because it is slower than the other methods (but it could be done).

# /results: Contains the results of the tests (starting with v2).
# Earlier versions do not, but later versions have the decider's way of selecting the answer added in the log, from:
# unanimous (all SC iterations agree on the same answer), sampling (no SC iteration agrees on the same answer,
# or there is a tied-mode, so sampling is used), or mode (there is a most common answer, so that one is used).
# Early exiting is not implemented (for example if already 3 out of 5 agree), but is planned for the next version.
# There exists a fourth way to decide implemented (Decider.py), via LLM, but did not work well, as it chose
# answers outside the given pool of options, so it is not used in the results. There is a way to constrain the
# LLM to a set of options, and that might be the way to go for the Decider, but it is not implemented yet.

# Organization also improves:
# /config/v2/config.py: Contains the configuration for the script.
# /methods/v2: Contains the methods to run the LLM (CoT, Dec, PAL) and the Decider.
# /utils/v2/utils.py: Contains utility functions to load exemplars, save results, and select the best response.

# To run the LLM, the script uses the Llama C++ library and the Llama Python wrapper (you can choose which one to use).
# https://github.com/ggerganov/llama.cpp
# https://github.com/abetlen/llama-cpp-python
# Make sure to have llama.cpp in /LLM as well as have llama-cpp-python installed.

# A custom GSM8K dataset is created, so far with only 40 pairs of questions and answers, to test models alternatively, as contamination
# from GSM8K leaking into the training data might have tainted some models. The questions include set theory, probability, and so on,
# so they are not the exact type of questions the original GSM8K dataset has, but they are similar enough to test the models.
# /datasets/custom_gsm8k.json: Contains the custom GSM8K dataset.

# Create the save folder if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Function to test the LLM on the GSM8K dataset
def test_gsm8k():
    """Test the LLM on the GSM8K dataset using the Chain of Thought, Program-aided Language Models, or Declarative methods."""
    start_time = time.time() # Start time for the test
    data_to_save = [] # Data to save to file
    n_correct = 0 # Number of correct predictions

    # Load the exemplars for the method as the context
    context = load_exemplars()

    # Select either a subset or the entire dataset
    if not CUSTOM_GSM8K:
        if N_SAMPLES is None or N_SAMPLES > len(GSM8K):
            dataset_to_iterate = GSM8K.shuffle(seed=seed)
        else:
            dataset_to_iterate = GSM8K.shuffle(seed=seed).select(range(N_SAMPLES))
    else:
        if N_SAMPLES is None or N_SAMPLES > len(GSM8K):
            dataset_to_iterate = GSM8K
        else:
            dataset_to_iterate = GSM8K[:N_SAMPLES]
    
    # Loop through a random (seeded) (sub)set of GSM8K
    for idx, example in enumerate(dataset_to_iterate, start=1):
        print(f"\nProcessing sample {idx}...")
        question = example["question"]
        answer = example["answer"]
        concise_answer = extract_and_format_value(answer.split("####")[-1].strip())

        method_responses = {}
        for method_to_test in METHODS_TO_PICK_FROM:
            method_response = run_method(method_to_test, question, context, cpp=CPP)
            method_responses[method_to_test] = method_response

        unique_valid_concise = {}
        for method, responses in method_responses.items():
            for concise_pred, detailed_pred in zip(responses["concise_predictions"], responses["predictions"]):
                if concise_pred != "bug":
                    if concise_pred not in unique_valid_concise:
                        unique_valid_concise[concise_pred] = []
                    unique_valid_concise[concise_pred].append(detailed_pred)

        valid_responses = {
            "predictions": [],
            "concise_predictions": []
        }
        
        for concise, detailed_list in unique_valid_concise.items():
            valid_responses["concise_predictions"].append(concise)
            valid_responses["predictions"].extend(detailed_list)

        # Handle unanimous responses or bug-only responses
        if len(valid_responses["concise_predictions"]) <= 1:
            if len(valid_responses["concise_predictions"]) == 0:
                best_response = "bug"
            else:
                best_response = valid_responses["concise_predictions"][0]
            print(f"\tUnanimous: {best_response}")
            decision_type = "unanimous"
        else:
            if not DECIDER:
                decision = "select_mode_or_sample"
                best_response, decision_type = select_mode_or_sample(unique_valid_concise)
            else:
                # Run a decider if there are multiple unique responses
                decision_question = f"{question}\nC: " + ", ".join(valid_responses["concise_predictions"])
                decision = run_method("Decider", decision_question, context)
                best_response = decision["concise_prediction"]

        # Evaluate the prediction
        result = "Correct" if best_response == concise_answer else "Incorrect"
        if result == "Correct":
            n_correct += 1

        # Save detailed results for analysis, including the best response
        all_detailed_predictions = []
        for method, responses in method_responses.items():
            all_detailed_predictions.extend(responses["predictions"])
        data_to_save.append({
            "index": idx,
            "question": question,
            "answer": answer,
            "concise_answer": concise_answer,
            "prediction": "\n\n".join(all_detailed_predictions) + 
                          (f"\n\nDecider ({decision_type}): {best_response}") +
                          f"\n#### {best_response}",
            "concise_prediction": best_response,
            "result": result
        })

    datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    desc_samples = "all samples" if N_SAMPLES is None else "1 sample" if N_SAMPLES == 1 else f"{N_SAMPLES} samples"
    method_names = "_".join(METHODS_TO_PICK_FROM)
    gsm8k_type = "custom_" if CUSTOM_GSM8K else ""
    save_path = f"{SAVE_FOLDER}/v2_{MODEL_TO_TEST}_{gsm8k_type}GSM8K_{SPLIT}_{datetime_str}_seed_{seed}_{method_names}_{N_ITERATIONS}_iters_{desc_samples}.txt"

    end_time = time.time() # End time for the test
    duration = end_time - start_time
    save_results(data_to_save, save_path, duration, n_correct)

# Function to run the specified method with the given question and context
def run_method(method, question, context, cpp=False):
    """Run the specified method with the given question and context."""
    if "CoT" in method:
        return run_cot(question, context["CoT"], cpp=cpp)
    elif "Decl" in method:
        return run_declarative(question, context["Decl"], cpp=cpp)
    elif "PAL" in method:
        return run_pal(question, context["PAL"], cpp=cpp)
    elif "Decider" in method:
        return run_decider(question, context["Decider"])

if __name__ == "__main__":
        test_gsm8k()
