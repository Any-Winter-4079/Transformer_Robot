import json
from pathlib import Path
from llama_cpp import Llama
from datasets import load_dataset

#################
# Choices       #
#################
MODEL_TO_TEST = "cerebrum-1.0-8x7b" # Model to test
TEMP = 0 # Temperature for the LLM
N_SAMPLES = None # None for all samples
PAL_TIMEOUT = 5 # Timeout for the PAL method
CPP = False # Run the LLM with llama-cpp vs. llama-cpp-python
METHODS_AND_ITERATIONS_PER_METHOD = {
    # # Note order matters if you use early stopping
    # "0Shot": 1,
    "PALpy": 1,
}
EARLY_STOPPING = 3 # Stop when N iterations agree on the same answer
#################
# Models        #
#################
MODEL_BASE_PATH = (Path(__file__).parent / "../../llama.cpp/models/").resolve() # Path to the LLM models
MODEL_PATHS = {
    "llama-2-7b-q4_0": MODEL_BASE_PATH / "7b/ggml-model-q4_0.bin",
    "llama-2-7b-f16": MODEL_BASE_PATH / "7b/ggml-model-f16.bin",
    "llama-2-13b-q4_0": MODEL_BASE_PATH / "13b/ggml-model-q4_0.bin",
    "llama-2-7b-chat-q4_0": MODEL_BASE_PATH / "7b-chat/ggml-model-q4_0.bin",
    "llama-2-13b-chat-q4_0": MODEL_BASE_PATH / "13b-chat/ggml-model-q4_0.bin",
    "llama-3-8b": MODEL_BASE_PATH / "llama-3-8b/ggml-model-f16.gguf",
    "llama-3-8b-instruct": MODEL_BASE_PATH / "llama-3-8b-instruct/H-ggml-model-f16.gguf",
    "phi-3-mini-4k-instruct-fp16": MODEL_BASE_PATH / "Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-fp16.gguf",
    "phi-3-mini-4k-instruct-q4": MODEL_BASE_PATH / "Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-q4.gguf",
    "phi-3-mini-128k-instruct-fp16": MODEL_BASE_PATH / "Phi-3-mini-128k-instruct/ggml-model-f16.gguf",
    "phi-3-small-8k-instruct-fp16": MODEL_BASE_PATH / "Phi-3-small-8k-instruct/ggml-model-f16.gguf",
    "phi-3-medium-4k-instruct-fp16": MODEL_BASE_PATH / "Phi-3-medium-4k-instruct/ggml-model-f16.gguf",
    "phi-3-medium-4k-instruct-q4_k_m": MODEL_BASE_PATH / "Phi-3-medium-4k-instruct/Phi-3-medium-4k-instruct-Q4_K_M.gguf",
    "phi-3-medium-4k-instruct-q2_k": MODEL_BASE_PATH / "Phi-3-medium-4k-instruct/Phi-3-medium-4k-instruct-Q2_K.gguf",
    "phi-3-medium-128k-instruct-q4_k_m": MODEL_BASE_PATH / "Phi-3-medium-128k-instruct/Phi-3-medium-128k-instruct-Q4_K_M.gguf",
    "metamath-mistral-7b": MODEL_BASE_PATH / "MetaMath-Mistral-7B/MetaMath-Mistral-7B.Q4_K_M.gguf.gguf",
    "mixtral-8x7b-instruct-q8_0": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-v0.1.Q8_0.gguf",
    "mixtral-8x7b-instruct-q5_0": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-q5_0.gguf",
    "mixtral-8x7b-instruct-q4_k_m": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-Q4_K_M.gguf",
    "mixtral-8x7b-instruct-q3_k_m": MODEL_BASE_PATH / "mixtral-8x7b-instruct-v0.1/mixtral-8x7b-instruct-Q3_K_M.gguf",
    "cerebrum-1.0-8x7b": MODEL_BASE_PATH / "Cerebrum-1.0-8x7b/Cerebrum-1.0-8x7b-Q4_K_M.gguf",
    "mistral-7b-instruct-v0.2-q8_0": MODEL_BASE_PATH / "mistral-7b-instruct-v0.2/mistral-7b-instruct-v0.2.Q8_0.gguf",
    "70b-code-q4": MODEL_BASE_PATH / "70b-code/codellama-70b-python.Q4_K_M.gguf",
    "tora-13b": MODEL_BASE_PATH / "tora-13b-v1.0/tora-13b-v1.0.Q5_K_M.gguf",
    "deepseek-coder-33b-instruct-q5_k_m": MODEL_BASE_PATH / "deepseek-coder-33B-instruct/deepseek-coder-33b-instruct.Q5_K_M.gguf",
    "deepseek-math-7b-instruct-q4_k_m": MODEL_BASE_PATH / "deepseek-math-7b-instruct/deepseek-math-7b-instruct.Q4_K_M.gguf",
    "deepseek-llm-67b-chat-q4_k_m": MODEL_BASE_PATH / "deepseek-llm-67b-chat/deepseek-llm-67b-chat.Q4_K_M.gguf",
    # LMM (Large Multimodal Model)
    "moondream2-fp16": MODEL_BASE_PATH / "moondream2/moondream2-text-model-f16.gguf",
    "mistral-7b-instruct-q_5_k-llava-1.6": MODEL_BASE_PATH / "llava-v1.6-mistral-7b/ggml-mistral-7b-q_5_k.gguf",
    "phi-3-mini-4k-instruct-fp16-llava": MODEL_BASE_PATH / "llava-phi-3-mini/ggml-model-f16.gguf",
}
MMPROJ_PATHS = {
    "mistral-7b-instruct-q_5_k-llava-1.6-mmproj": MODEL_BASE_PATH / "llava-v1.6-mistral-7b/mmproj-mistral7b-f16-q6_k.gguf",
    "moondream2-fp16-mmproj": MODEL_BASE_PATH / "moondream2/moondream2-mmproj-f16.gguf",
    "phi-3-mini-4k-instruct-fp16-llava-mmproj": MODEL_BASE_PATH / "llava-phi-3-mini/mmproj-model-f16.gguf",
}
MMPROJ_KEY = next((key for key in MMPROJ_PATHS if key.lower().startswith(MODEL_TO_TEST.lower())), None)
MMPROJ_PATH = MMPROJ_PATHS[MMPROJ_KEY] if MMPROJ_KEY else None
CONTEXT_WINDOWS = {
    "llama-2-7b-q4_0": 4096,
    "llama-2-7b-f16": 4096,
    "llama-2-13b-q4_0": 4096,
    "llama-2-7b-chat-q4_0": 4096,
    "llama-2-13b-chat-q4_0": 4096,
    "llama-3-8b": 8192,
    "llama-3-8b-instruct": 8192,
    "phi-3-mini-4k-instruct-fp16": 4096,
    "phi-3-mini-4k-instruct-q4": 4096,
    "phi-3-mini-128k-instruct-fp16": 131072,
    "phi-3-small-8k-instruct-fp16": 8192,
    "phi-3-medium-4k-instruct-fp16": 4096,
    "phi-3-medium-4k-instruct-q4_k_m": 4096,
    "phi-3-medium-4k-instruct-q2_k": 4096,
    "phi-3-medium-128k-instruct-q4_k_m": 131072,
    "metamath-mistral-7b": 4096,
    "mixtral-8x7b-instruct-q8_0": 32768,
    "mixtral-8x7b-instruct-q5_0": 32768,
    "mixtral-8x7b-instruct-q4_k_m": 32768,
    "mixtral-8x7b-instruct-q3_k_m": 32768,
    "cerebrum-1.0-8x7b": 32768,
    "mistral-7b-instruct-v0.2-q8_0": 4096,
    "70b-code-q4": 4096,
    "tora-13b": 4096,
    "deepseek-coder-33b-instruct-q5_k_m": 16384,
    "deepseek-math-7b-instruct-q4_k_m": 4096,
    "deepseek-llm-67b-chat-q4_k_m": 4096,
    # LMM (Large Multimodal Model)
    "mistral-7b-instruct-q_5_k-llava-1.6": 4096,
    "moondream2-fp16": 4096,
    "phi-3-mini-4k-instruct-fp16-llava": 4096,
}
#################
#  LMM image    #
#################
IMAGE_PATH = MODEL_BASE_PATH / "llava-v1.6-mistral-7b/a.png"
#################
# Datasets      #
#################
DATASETS_BASE_PATH = (Path(__file__).parent / "../../datasets/").resolve() # Path to the datasets
SPLIT = "test" # train or test
CUSTOM_DATASET = False # Use the custom DATASET dataset or the original dataset
CUSTOM_DATASET_PATH = (Path(__file__).parent / "../../datasets/custom_gsm8k.json").resolve() # Path to the custom DATASET dataset
if CUSTOM_DATASET:
    with open(str(CUSTOM_DATASET_PATH), 'r') as file:
        DATASET = json.load(file)
        flattened = []
        for category, questions in DATASET["categories"].items():
            for question in questions:
                question['category'] = category
                flattened.append(question)
        DATASET = flattened
        print(f"Loaded {len(DATASET)} questions from the custom dataset.")
else:
    DATASET = load_dataset("gsm8k", "socratic")[SPLIT]
#################
# Exemplars     #
#################
EXEMPLARS_BASE_PATH =  (Path(__file__).parent / "../../exemplars/").resolve() # Path to the exemplars
EXEMPLARS_PATHS = {
    "0Shot": EXEMPLARS_BASE_PATH / "GSM8k_0-shot.py",
    "PAL": EXEMPLARS_BASE_PATH / "GSM8k_Program_Aided_LM_Principles.txt", # Program-aided Language Models [https://arxiv.org/pdf/2211.10435.pdf]
    "PALpy": EXEMPLARS_BASE_PATH / "GSM8K_Program_Aided_LM_Principles.py", # Program-aided Language Models [https://arxiv.org/pdf/2211.10435.pdf]
    "PALassert": EXEMPLARS_BASE_PATH / "GSM8K_Program_Aided_LM_Custom-Assert.txt", # Program-aided Language Models
    "PALR": EXEMPLARS_BASE_PATH / "GSM8k_Program_Aided_LM_Principles_rephrase.txt", # Program-aided Language Models
    "CoT": EXEMPLARS_BASE_PATH / "GSM8K_Chain_of_Thought_8-shot.txt", # Chain-of-Thought [https://arxiv.org/abs/2201.11903]
    "CoTpy": EXEMPLARS_BASE_PATH / "GSM8k_Chain_of_Thought-8-shot.py", # Chain-of-Thought [https://arxiv.org/abs/2201.11903]
    "CoTR": EXEMPLARS_BASE_PATH / "GSM8K_Chain_of_Thought_8-shot_rephrase.py", # Chain-of-Thought and EchoPrompt [https://arxiv.org/abs/2309.10687] / Rephrase and Respond [https://arxiv.org/abs/2311.04205]
    "Decl8": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_8-shot.txt", # Declarative (SymPy) [https://arxiv.org/abs/2304.09102]
    "Decl3P": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_3-shot_Principles.txt", # Declarative (SymPy)
    "Decl4MP": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_4-shot_More_Principles.txt", # Declarative (SymPy)
    "Decl8MP_Own": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_8-shot_More_Principles_Own.txt", # Declarative (SymPy)
    "Decl8MP_Own_multi": EXEMPLARS_BASE_PATH / "GSM8K_Declarative_8-shot_More_Principles_Own_3.txt", # Declarative (SymPy)
}
SAVE_FOLDER = (Path(__file__).parent / "../../results").resolve() # Path to the results
#################
# Templates     #
#################
USER_LEAD_METHOD_TEMPLATES = {
    "0Shot": "Use reasoning to solve the following problem, writing 'The answer is {number}.' at the end. Don't write any other numerical value after 'The answer is {number}.'.\n",
    "CoT": "",
    "CoTpy": "",
    "CoTR": "\nFirst rephrase, then answer, the following problem:\n",
    "Dec": "",
    "DecR": "\nFirst rephrase, then answer, the following problem:\n",
    "PAL": "",
    "PALpy": "",
    "PALR": "\nFirst rephrase, then answer, the following problem:\n",
    "Decider": "",
}
MODEL_TEMPLATES = {
    "mixtral-8x7b": {
        "system_start": "",
        "system_message": "",
        "system_end": "",
        "user_start": "",
        "user_end": "\n",
        "assistant_start": "",
        "assistant_end": "",
        "stop": "First rephrase, then answer, the following problem:\n" # hack, but depends on the method
        # so we must update this for each method we want to test and can't test multiple methods at once
        # unless they all share the same template because the stop seq. needs to be known.
        # In other words you can mix CoTR with DecR and PALR for SC but not CoTR with Dec/PAL
    },
    "mistral-7b": {
        "system_start": "",
        "system_message": "",
        "system_end": "",
        "user_start": "",
        "user_end": "\n",
        "assistant_start": "",
        "assistant_end": "",
        "stop": "First rephrase, then answer, the following problem:\n" # hack, but depends on the method
        # so we must update this for each method we want to test and can't test multiple methods at once
        # unless they all share the same template because the stop seq. needs to be known.
        # In other words you can mix CoTR with DecR and PALR for SC but not CoTR with Dec/PAL
    },
    "metamath-mistral-7b": {
        "system_start": "",
        "system_message": "Below is an instruction that describes a task. Write a response that appropriately completes the request.",
        "system_end": "\n",
        "user_start": "### Instruction:\n",
        "user_end": "\n",
        "assistant_start": "### Response: Let's think step by step.",
        "assistant_end": "\n",
        "stop": "### Instruction:\n"
    },
    "cerebrum-1.0-8x7b": {
        "system_start": "",
        "system_message": "A chat between a user and a thinking artificial intelligence assistant. The assistant describes its thought process and gives helpful and detailed answers to the user's questions.",
        "system_end": "",
        "user_start": "User:",
        "user_end": "",
        "assistant_start": "AI:",
        "assistant_end": "",
        "stop": "User:"
    },
    "phi-3": {
        "system_start": "<|system|>\n",
        "system_message": "You are a helpful AI assistant.",
        "system_end": "<|end|>",
        "user_start": "<|user|>",
        "user_end": "<|end|>",
        "assistant_start": "<|assistant|>\n",
        "assistant_end": "<|end|>",
        "stop": "<|end|>"
    }
}
MODEL_TEMPLATE_KEY = next((key for key in MODEL_TEMPLATES if MODEL_TO_TEST.lower().startswith(key.lower())), None)
MODEL_TEMPLATE = MODEL_TEMPLATES[MODEL_TEMPLATE_KEY]
#################
# Decider       #
#################
LLM_DECIDER = False # Use a decider or choose mode / sample
LLM_DECIDER_PATH = EXEMPLARS_BASE_PATH / "GSM8K_Decider.txt"
#################
# LLM           #
#################
seed = 1337 # Seed for reproducibility
max_tokens = 1024 # Maximum output length for the LLM
stop = MODEL_TEMPLATE["stop"]
STOP = [stop] if stop else []
# llama-cpp-python
if not CPP:
    llm = Llama(
                model_path=str(MODEL_PATHS[MODEL_TO_TEST]),
                n_gpu_layers=-1,
                seed=seed,
                verbose=False,
                n_ctx=CONTEXT_WINDOWS[MODEL_TO_TEST],
    )
# llama-cpp
else:
    LLAMA_BASE_PATH = (Path(__file__).parent / "../../llama.cpp/").resolve()
