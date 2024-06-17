from config.v3.config import MODEL_TEMPLATE, STOP
from utils.v3.utils import run_llm, extract_and_format_value

# Function to run the Decider method
def run_decider(question, exemplars):
    """Run the Decider method."""
    user_end = MODEL_TEMPLATE["user_end"]
    assistant_start = MODEL_TEMPLATE["assistant_start"]
    message = f"{exemplars}{question}{user_end}\n{assistant_start}"
    prediction = run_llm(message, STOP)
    concise_prediction = prediction.split("The answer is ")[-1].strip()
    concise_prediction = extract_and_format_value(concise_prediction)
    print("\tDecider:", concise_prediction)
    return message, prediction, concise_prediction