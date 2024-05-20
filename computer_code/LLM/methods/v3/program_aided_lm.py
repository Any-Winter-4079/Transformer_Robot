import re
import os
import tempfile
import subprocess
from utils.v3.utils import run_llm, extract_and_format_value
from config.v3.config import MODEL_TEMPLATE, STOP, PAL_TIMEOUT

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
def run_pal(question, exemplars, cpp=False, iteration=0):
    """Run the Program-aided Language Models (PAL) method."""
    user_end = MODEL_TEMPLATE["user_end"]
    assistant_start = MODEL_TEMPLATE["assistant_start"]
    message = f"{exemplars}{question}{user_end}\n{assistant_start}"
    prediction = run_llm(message, STOP, cpp=cpp, iteration=iteration)
    try:
        pattern = r"(def solution.*?return result[^\n]*)"
        match = re.search(pattern, prediction, re.DOTALL)
        prediction = match.group(1) if match else ""
        # print(f"\tPAL: {prediction}")
        concise_prediction = run_code_with_subprocess_timeout(prediction)
    except Exception as e:
        # print(f"\tError in PAL: {e}")
        concise_prediction = "bug"
    if concise_prediction != "bug":
        concise_prediction = extract_and_format_value(concise_prediction)
    print("\tPAL:", concise_prediction)
    prediction = f"{prediction}\n#### {concise_prediction}"
    return message, prediction, concise_prediction
