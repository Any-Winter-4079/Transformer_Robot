from utils.v2.utils import run_llm, extract_and_format_value

# Function to run the Chain of Thought (CoT) method
def run_cot(question, exemplars, cpp=False):
    """Run the Chain of Thought (CoT) method."""
    message = f"{exemplars}\nQ: {question}\nA: "
    predictions = run_llm(message, ["Q:"], cpp=cpp)
    augmented_predictions = []
    concise_predictions = []
    for prediction in predictions:
        predicted_answer = prediction.split("The answer is ")[-1].strip()
        predicted_answer = extract_and_format_value(predicted_answer)
        augmented_predictions.append(prediction)
        concise_predictions.append(predicted_answer)
        print("\tCoT:", predicted_answer)
    return {
        "message": message,
        "predictions": predictions,
        "concise_predictions": concise_predictions
    }
