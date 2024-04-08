from utils.v2.utils import run_llm, extract_and_format_value

# Function to run the Decider method
def run_decider(question, exemplars):
    """Run the Decider method."""
    message = f"{exemplars}\nQ: {question}\n\nA: "
    prediction = run_llm(message, ["Q:"], decider=True)[0]
    predicted_answer = prediction.split("The answer is ")[-1].strip()
    predicted_answer = extract_and_format_value(predicted_answer)
    print("\tDecider:", predicted_answer)
    return {
        "message": message,
        "prediction": prediction,
        "concise_prediction": predicted_answer
    }
