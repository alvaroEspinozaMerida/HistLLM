import argparse
from pathlib import Path

import numpy as np
from hailo_sdk_client.runner.client_runner import ClientRunner

import pandas as pd
import tensorflow as tf
from datasets import Dataset
from transformers import AutoTokenizer
# THIS SCRIPT IS MEANT TO BE RUN IN THE Hailo AI Software Suite Docker container


BASE_DIR = Path("/local/workspace/qwen2_compile_work")

MODEL_NAME = "qwen2_1.5b_instruct"

model_path = BASE_DIR / "models" / f"{MODEL_NAME}.q.har"
model_script_path = BASE_DIR / "models" / f"{MODEL_NAME}.alls"

HW_ARCH = "hailo10h"
HAILO_INPUT_PREFIX = "Qwen2-1_5B-Instruct"
MAX_LENGTH = 512

dataset_path = BASE_DIR /"calibration"/ "calibration_data_mixed.csv"


SYSTEM_PROMPT = (
    "You are a world history expert. Answer historical questions with factual, "
    "accurate, and clear responses. Focus on relevant historical context, key facts, "
    "causes, effects, people, places, and dates when appropriate. If you do not have "
    "enough context, say so rather than inventing details."
)


def format_calibration_set(dataset, tokenizer, calibset_size, max_length):
    dataset_list = [x for x in dataset]
    input_texts = []
    group_size = len(dataset_list) // calibset_size
    for i in range(calibset_size):
        # Fill each calibration sample with as many examples as possible
        sample_group = dataset_list[int(i * group_size): int((i + 1) * group_size)]
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]
        for data in sample_group:
            messages.extend(
                [
                    {
                        "role": "user",
                        "content": data["prompt"],
                    },
                    {
                        "role": "assistant",
                        "content": data["answer"],
                    },
                ]
            )

        input_texts.append(
            tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        )

    tokenized_inputs = tokenizer(
        input_texts,
        truncation=True,
        padding="max_length",
        max_length=max_length,
        padding_side="left",
    )

    input_ids = np.array(tokenized_inputs["input_ids"]).reshape(-1, 1, max_length)
    current_position = np.sum(np.array(tokenized_inputs["attention_mask"]), axis=-1)
    return input_ids, current_position

def main():
    parser = argparse.ArgumentParser(
        description="Optimize and compile Qwen2 LoRA adapter with Hailo DFC."
    )

    parser.add_argument(
        "adapter_name",
        choices=["qa_only_lora", "mixed_sft_lora", "curriculum_lora"],
        help="Adapter folder name inside adapters/",
    )

    args = parser.parse_args()
    # compile_adapter(args.adapter_name)

    lora_weights_path = BASE_DIR / "adapters" / args.adapter_name / "adapter_model.safetensors"

    adapter_name = args.adapter_name

    print("=== CONFIG Settings ===")
    print("\nModel Settings:")
    print(f"MODEL_NAME: {MODEL_NAME}")
    print(f"adapter_name: {adapter_name}")
    print(f"HW_ARCH: {HW_ARCH}")
    print("="*20)
    print("Directory structure:")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"model_path: {model_path}")
    print(f"model_script_path: {model_script_path}")
    print(f"dataset_path: {dataset_path}")
    print("="*20)
    print("Dataset Settings:")
    print(f"MAX_LENGTH: {MAX_LENGTH}")
    print("="*20)
    print("=== EXISTENCE CHECK ===")
    print(f"model_path exists: {model_path.exists()}")
    print(f"model_script_path exists: {model_script_path.exists()}")
    print(f"dataset_path exists: {dataset_path.exists()}")
    print("=======================")
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-1.5B-Instruct")
    print("Tokenizer loaded.")

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    dataset = Dataset.from_pandas(df)
    print("Dataset loaded.")

    print("Loading model...")
    runner = ClientRunner(hw_arch=HW_ARCH)
    runner.load_har(str(model_path))
    print("Model loaded.")
    print("Loading trained lora weights...")
    runner.load_lora_weights(
        lora_weights_path=str(lora_weights_path),
        lora_adapter_name=adapter_name,
    )
    print("After loading the new adapter, reloading the model script to apply it on the new model")

    hn_dict = runner.load_model_script(str(model_script_path))

    max_length = hn_dict["net_params"]["cache_size"]
    calibset_size = 64
    input_ids, current_position = format_calibration_set(dataset, tokenizer,calibset_size, max_length)

    input_dict = {
        f"{adapter_name}/input_layer1": input_ids,
        f"{adapter_name}/input_layer2": current_position,  # attention mask
        f"{adapter_name}/input_layer3": current_position,  # position id to the RoPE cos of the q component
        f"{adapter_name}/input_layer4": current_position,  # position id to the RoPE sin of the q component
        f"{adapter_name}/input_layer5": current_position,  # position id to the RoPE cos of the k component
        f"{adapter_name}/input_layer6": current_position,  # position id to the RoPE sin of the k component
    }

    runner.optimize(input_dict)

    runner.save_har(
        f"{MODEL_NAME}.lora.q.har",
        params_serialization=".hdf5",
        compilation_only=False
    )

    # Initialize a new ClientRunner with the optimized HAR
    runner = ClientRunner(
        hw_arch="hailo10h",
        har=f"{MODEL_NAME}.lora.q.har"
    )

    hef = runner.compile()

    hef_path = BASE_DIR / "outputs" / adapter_name / f"{MODEL_NAME}_{adapter_name}.hef"
    hef_path.parent.mkdir(parents=True, exist_ok=True)

    with open(hef_path, "wb") as f:
        f.write(hef)

    print(f"Saved HEF to: {hef_path}")


if __name__ == "__main__":
    main()