import os
import time
import json
from datetime import datetime
from config.v3.config import *
from collections import defaultdict
from methods.v3.decider import run_decider
from methods.v3.zero_shot import run_zero_shot
from methods.v3.program_aided_lm import run_pal
from methods.v3.chain_of_thought import run_cot
from methods.v3.declarative import run_declarative
from utils.v3.utils import extract_and_format_value, load_exemplars, save_results, select_mode_or_sample

#################
# Description   #
#################
# This script tests the LLM on the DATASET dataset using the Chain of Thought, Program-aided Language Models, and Declarative methods.
# To run the LLM, the script uses the Llama C++ library and the Llama Python wrapper.
# https://github.com/ggerganov/llama.cpp
# https://github.com/abetlen/llama-cpp-python

# Create the save folder if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Function to test the LLM on the DATASET dataset
def test_DATASET():
    """Test the LLM on the DATASET dataset using the Chain of Thought, Program-aided Language Models, or Declarative methods."""
    start_time = time.time() # Start time for the test
    data_to_save = [] # Data to save to file
    n_correct = 0 # Number of correct predictions

    # Load the exemplars for the method as the context
    context = load_exemplars()

    # Select either a subset or the entire dataset
    if not CUSTOM_DATASET:
        if N_SAMPLES is None or N_SAMPLES > len(DATASET):
            dataset_to_iterate = DATASET.shuffle(seed=seed)
        else:
            dataset_to_iterate = DATASET.shuffle(seed=seed).select(range(N_SAMPLES))
    else:
        if N_SAMPLES is None or N_SAMPLES > len(DATASET):
            dataset_to_iterate = DATASET
        else:
            dataset_to_iterate = DATASET[:N_SAMPLES]
    
    # Loop through a random (seeded) (sub)set of DATASET
    for idx, example in enumerate(dataset_to_iterate, start=1):
        print(f"\nProcessing sample {idx}...")
        question = example["question"]
        answer = example["answer"]
        concise_answer = extract_and_format_value(answer.split("####")[-1].strip())

        valid_concise_predictions_with_counts = defaultdict(int)
        method_responses = defaultdict(lambda: {"predictions": [], "concise_predictions": []})
        early_stop = False
        for method_to_test, iterations in METHODS_AND_ITERATIONS_PER_METHOD.items():
            if early_stop:
                print("Early stopping")
                break
            for iteration in range(iterations):
                _, prediction, concise_prediction = run_method(method_to_test, question, context, cpp=CPP, iteration=iteration)
                method_responses[method_to_test]["predictions"].append(prediction)
                method_responses[method_to_test]["concise_predictions"].append(concise_prediction)
                if concise_prediction != "bug":
                    valid_concise_predictions_with_counts[concise_prediction] += 1
                    if valid_concise_predictions_with_counts[concise_prediction] >= EARLY_STOPPING:
                        early_stop = True
                        break

        print("Valid preds and counts:", json.dumps(dict(valid_concise_predictions_with_counts), indent=4))
        # Handle unanimous responses or bug-only responses
        if len(valid_concise_predictions_with_counts) <= 1:
            if len(valid_concise_predictions_with_counts) == 0:
                best_prediction = "bug"
            else:
                best_prediction = max(valid_concise_predictions_with_counts, key=valid_concise_predictions_with_counts.get)
            print(f"Unanimous: {best_prediction}")
            decision_type = "unanimous"
        # Handle mode selection or decider
        else:
            if not LLM_DECIDER:
                decision = "select_mode_or_sample"
                best_prediction, decision_type = select_mode_or_sample(valid_concise_predictions_with_counts)
            else:
                # Run a decider if there are multiple unique responses
                decision_question = f"{question}\nC: " + ", ".join(valid_concise_predictions_with_counts.keys())
                decision = run_method("Decider", decision_question, context)
                best_prediction = decision["concise_prediction"]

        # Evaluate the prediction
        result = "Correct" if best_prediction == concise_answer else "Incorrect"
        if result == "Correct":
            n_correct += 1

        # Save detailed results for analysis, including the best response
        all_detailed_predictions = []
        for _, responses in method_responses.items():
            all_detailed_predictions.extend(responses["predictions"])
        data_to_save.append({
            "index": idx,
            "question": question,
            "answer": answer,
            "concise_answer": concise_answer,
            "prediction": "\n\n".join(all_detailed_predictions) + 
                          (f"\n\nDecider ({decision_type}): {best_prediction}") +
                          f"\n#### {best_prediction}",
            "concise_prediction": best_prediction,
            "result": result
        })

    datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    desc_samples = "all_samples" if N_SAMPLES is None else "1_sample" if N_SAMPLES == 1 else f"{N_SAMPLES}_samples"
    method_its_parts = [f"{method}_{its}_iters" for method, its in METHODS_AND_ITERATIONS_PER_METHOD.items()]
    method_its_str = "_".join(method_its_parts)
    dataset_type = "custom_" if CUSTOM_DATASET else ""
    save_path = f"{SAVE_FOLDER}/v3_{MODEL_TO_TEST}_{dataset_type}GSM8K_{SPLIT}_{datetime_str}_seed_{seed}_{method_its_str}_{desc_samples}.txt"

    end_time = time.time() # End time for the test
    duration = end_time - start_time
    save_results(data_to_save, save_path, duration, n_correct)

# Function to run the specified method with the given question and context
def run_method(method, question, context, cpp=False, iteration=0):
    """Run the specified method with the given question and context."""
    if "0Shot" in method:
        return run_zero_shot(question, context["0Shot"], cpp=cpp, iteration=iteration)
    elif "CoT" in method:
        context = context["CoTR"] if "CoTR" in context else context["CoT"]
        return run_cot(question, context, cpp=cpp, iteration=iteration)
    elif "Decl" in method:
        return run_declarative(question, context["Decl"], cpp=cpp, iteration=iteration)
    elif "PAL" in method:
        return run_pal(question, context["PAL"], cpp=cpp, iteration=iteration)
    elif "Decider" in method:
        return run_decider(question, context["Decider"])

if __name__ == "__main__":
        test_DATASET()
