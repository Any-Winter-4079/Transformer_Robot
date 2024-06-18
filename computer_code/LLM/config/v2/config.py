import json
from pathlib import Path
from llama_cpp import Llama
from datasets import load_dataset

#################
# Models        #
#################
MODEL_BASE_PATH = (Path(__file__).parent / "../../llama.cpp/models/").resolve() # Path to the LLM models
MODEL_PATHS = {
    "llama-7b-q4_0": MODEL_BASE_PATH / "7b/ggml-model-q4_0.bin",
    "llama-7b-f16": MODEL_BASE_PATH / "7b/ggml-model-f16.bin",
    "llama-13b-q4_0": MODEL_BASE_PATH / "13b/ggml-model-q4_0.bin",
    "llama-7b-chat-q4_0": MODEL_BASE_PATH / "7b-chat/ggml-model-q4_0.bin",
    "llama-13b-chat-q4_0": MODEL_BASE_PATH / "13b-chat/ggml-model-q4_0.bin",
    "MetaMath-Mistral-7B": MODEL_BASE_PATH / "MetaMath-Mistral-7B/MetaMath-Mistral-7B.Q4_K_M.gguf.gguf",
    "mixtral-8x7b-instruct-q8_0": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-v0.1.Q8_0.gguf",
    "mixtral-8x7b-instruct-q5_0": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-q5_0.gguf",
    "mixtral-8x7b-instruct-Q4_K_M": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-Q4_K_M.gguf",
    "mixtral-8x7b-instruct-Q3_K_M": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-Q3_K_M.gguf",
    "phi-3-mini-4k-instruct-q4": MODEL_BASE_PATH / "Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-q4.gguf",
    "Cerebrum-1.0-8x7b": MODEL_BASE_PATH / "Cerebrum-1.0-8x7b/Cerebrum-1.0-8x7b-Q4_K_M.gguf",
    "mistral-7b-instruct-v0.2.Q8_0": MODEL_BASE_PATH / "mistral-7b-instruct-v0.2/mistral-7b-instruct-v0.2.Q8_0.gguf",
    "70b-code-q4": MODEL_BASE_PATH / "70b-code/codellama-70b-python.Q4_K_M.gguf",
    "tora-13b": MODEL_BASE_PATH / "tora-13b-v1.0/tora-13b-v1.0.Q5_K_M.gguf",
    "deepseek-coder-33B-instruct-Q5_K_M": MODEL_BASE_PATH / "deepseek-coder-33B-instruct/deepseek-coder-33b-instruct.Q5_K_M.gguf",
    "deepseek-math-7b-instruct-Q4_K_M": MODEL_BASE_PATH / "deepseek-math-7b-instruct/deepseek-math-7b-instruct.Q4_K_M.gguf",
    "deepseek-llm-67b-chat-Q4_K_M": MODEL_BASE_PATH / "deepseek-llm-67b-chat/deepseek-llm-67b-chat.Q4_K_M.gguf",
}
CONTEXT_WINDOWS = {
    "llama-7b-q4_0": 4096,
    "llama-7b-f16": 4096,
    "llama-13b-q4_0": 4096,
    "llama-7b-chat-q4_0": 4096,
    "llama-13b-chat-q4_0": 4096,
    "MetaMath-Mistral-7B": 4096,
    "mixtral-8x7b-instruct-q8_0": 32768,
    "mixtral-8x7b-instruct-q5_0": 32768,
    "mixtral-8x7b-instruct-Q4_K_M": 32768,
    "mixtral-8x7b-instruct-Q3_K_M": 32768,
    "phi-3-mini-4k-instruct-q4": 4096,
    "Cerebrum-1.0-8x7b": 32768,
    "mistral-7b-instruct-v0.2.Q8_0": 4096,
    "70b-code-q4": 4096,
    "tora-13b": 4096,
    "deepseek-coder-33B-instruct-Q5_K_M": 16384,
    "deepseek-math-7b-instruct-Q4_K_M": 4096,
    "deepseek-llm-67b-chat-Q4_K_M": 4096,
}
#################
# Datasets      #
#################
SPLIT = "test" # train or test
CUSTOM_GSM8K = False # Use the custom GSM8K dataset or the original dataset
CUSTOM_GSM8K_PATH = (Path(__file__).parent / "../../datasets/custom_gsm8k.json").resolve() # Path to the custom GSM8K dataset
if CUSTOM_GSM8K:
    with open(str(CUSTOM_GSM8K_PATH), 'r') as file:
        GSM8K = json.load(file)
        flattened = []
        for category, questions in GSM8K["categories"].items():
            for question in questions:
                question['category'] = category
                flattened.append(question)
        GSM8K = flattened
        print(f"Loaded {len(GSM8K)} questions from the custom GSM8K dataset.")
else:
    GSM8K = load_dataset("gsm8k", "socratic")[SPLIT]
#################
# Exemplars     #
#################
EXEMPLARS_BASE_PATH =  (Path(__file__).parent / "../../exemplars/").resolve() # Path to the exemplars
EXEMPLARS_PATHS = {
    "PAL": EXEMPLARS_BASE_PATH / "GSM8k_Program_Aided_LM_Principles.txt", # Program-aided Language Models [https://arxiv.org/pdf/2211.10435.pdf]
    "PALassert": EXEMPLARS_BASE_PATH / "GSM8K_Program_Aided_LM_Custom-Assert.txt", # Program-aided Language Models [https://arxiv.org/pdf/2211.10435.pdf]
    "CoT": EXEMPLARS_BASE_PATH / "GSM8K_Chain_of_Thought_8-shot.txt", # Chain of Thought
    "Decl8": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_8-shot.txt", # Declarative (SymPy)
    "Decl3P": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_3-shot_Principles.txt", # Declarative (SymPy)
    "Decl4MP": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_4-shot_More_Principles.txt", # Declarative (SymPy)
    "Decl8MP_Own": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_8-shot_More_Principles_Own.txt", # Declarative (SymPy)
    "Decl8MP_Own_multi": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_8-shot_More_Principles_Own_3.txt", # Declarative (SymPy)
}
SAVE_FOLDER = (Path(__file__).parent / "../../results").resolve() # Path to the results
#################
# Choices       #
#################
MODEL_TO_TEST = "mixtral-8x7b-instruct-q5_0" # Model to test
N_SAMPLES = 1 # None for all samples
PAL_TIMEOUT = 5 # Timeout for the PAL method
CPP = False # Run the LLM with llama-cpp vs. llama-cpp-python
#################
# Methods       #
#################
METHODS_TO_PICK_FROM = ["CoT"]
#################
# Decider       #
#################
DECIDER = False # Use a decider or choose mode / sample
DECIDER_PATH = EXEMPLARS_BASE_PATH / "GSM8K_Decider.txt"
#################
# LLM           #
#################
seed = 1337 # Seed for reproducibility
max_tokens = 1024 # Maximum output length for the LLM
N_ITERATIONS = 1 # Number of iterations for the LLM (using different seeds)
# llama-cpp-python
llm = Llama(
            model_path=str(MODEL_PATHS[MODEL_TO_TEST]),
            n_gpu_layers=-1,
            seed=seed,
            verbose=False,
            n_ctx=CONTEXT_WINDOWS[MODEL_TO_TEST],
)
# llama-cpp
LLAMA_BASE_PATH = (Path(__file__).parent / "../../llama.cpp/").resolve()
