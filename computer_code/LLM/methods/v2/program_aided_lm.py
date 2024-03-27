import re
import os
import tempfile
import subprocess
from config.v2.config import PAL_TIMEOUT
from utils.v2.utils import run_llm, extract_and_format_value

# Function to execute the code with a timeout using the subprocess module
def run_code_with_subprocess_timeout(code, timeout=PAL_TIMEOUT):
    """Execute the code with a timeout using the subprocess module."""
    code = code + '\nprint(solution())'
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w+') as temp_script:
        temp_script_name = temp_script.name
        temp_script.write(code)
    try:
        completed_process = subprocess.run(['python', temp_script_name], 
                                           capture_output=True, text=True, timeout=timeout)
        if completed_process.returncode == 0:
            # print(f"\tOutput: {completed_process.stdout.strip()}")
            return completed_process.stdout.strip()
        else:
            # print(f"\tError: {completed_process.stderr.strip()}")
            return "bug"
    except subprocess.TimeoutExpired:
        # print("\tExecution timed out")
        return "bug"
    except Exception as e:
        # print(f"\tExecution failed: {str(e)}")
        return "bug"
    finally:
        os.remove(temp_script_name)

# Function to run the Program-aided Language Models (PAL) method
def run_pal(question, exemplars, cpp=False):
    """Run the Program-aided Language Models (PAL) method."""
    message = f"{exemplars}\nQ: {question}\nA: "
    predictions = run_llm(message, ["Q:"], cpp=cpp)
    augmented_predictions = []
    concise_predictions = []
    for prediction in predictions:
        try:
            pattern = r"(def solution.*?return result[^\n]*)"
            match = re.search(pattern, prediction, re.DOTALL)
            prediction = match.group(1) if match else ""
            # print(f"\tPAL: {prediction}")
            predicted_answer = run_code_with_subprocess_timeout(prediction)
        except Exception as e:
            # print(f"\tError in PAL: {e}")
            predicted_answer = "bug"
        
        if predicted_answer != "bug":
            predicted_answer = extract_and_format_value(predicted_answer)
        concise_predictions.append(predicted_answer)
        print("\tPAL:", predicted_answer)
        prediction = f"{prediction}\n#### {predicted_answer}"
        augmented_predictions.append(prediction)

    return {
        "message": message,
        "predictions": augmented_predictions,
        "concise_predictions": concise_predictions
    }
