import argparse
import numpy as np
import util
from pathlib import Path
from datasets import Dataset, concatenate_datasets
from transformers import AutoTokenizer

# THIS SCRIPT IS MEANT TO BE RUN IN THE Hailo AI Software Suite Docker container

BASE_DIR = Path("/home/alvaro/Desktop/HAILO_10H/shared_with_docker/HistLLM_compile/qwen2_lora_compile")
OUTPUT_DIR = BASE_DIR / "calibration"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HF_MODEL_ID = "Qwen/Qwen2-1.5B-Instruct"

SYSTEM_PROMPT = (
    "You are a world history expert. Answer historical questions with factual, "
    "accurate, and clear responses. Focus on relevant historical context, key facts, "
    "causes, effects, people, places, and dates when appropriate. If you do not have "
    "enough context, say so rather than inventing details."
)



def row_to_prompt(row):
    if "question" in row and row["question"]:
        return row["question"]

    if "name" in row and row["name"]:
        return f"Tell me about {row['name']}."

    if "event_name" in row and row["event_name"]:
        return f"Explain the historical event: {row['event_name']}."

    return None


def format_for_calibration(row, tokenizer):
    user_prompt = row_to_prompt(row)

    if not user_prompt:
        return {"input_text": ""}

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    return {"input_text": input_text}


def tokenize_for_calibration(dataset, tokenizer, max_length):
    input_ids = []
    attention_masks = []

    for row in dataset:
        if not row["input_text"]:
            continue

        tokens = tokenizer(
            row["input_text"],
            return_tensors="np",
            padding="max_length",
            truncation=True,
            max_length=max_length,
        )

        input_ids.append(tokens["input_ids"][0])
        attention_masks.append(tokens["attention_mask"][0])

    return {
        "input_ids": np.stack(input_ids).astype(np.int32),
        "attention_mask": np.stack(attention_masks).astype(np.int32),
    }


def create_calibration_dataset(engine, tokenizer, max_samples, max_length):
    qa_dataset = util.load_table_as_dataset(
        engine=engine,
        table_name="qa_pairs",
        columns=["id", "question", "answer", "time_period"],
    )

    bio_dataset = util.load_table_as_dataset(
        engine=engine,
        table_name="biographies",
        columns=["curid", "name", "biography"],
    )

    events_dataset = util.load_table_as_dataset(
        engine=engine,
        table_name="historical_events",
        columns=["id", "event_name"],
    )

    qa_sample = qa_dataset.shuffle(seed=42).select(
        range(min(len(qa_dataset), max_samples))
    )

    bio_sample = bio_dataset.shuffle(seed=42).select(
        range(min(len(bio_dataset), max_samples))
    )

    events_sample = events_dataset.shuffle(seed=42).select(
        range(min(len(events_dataset), max_samples))
    )

    calibration_dataset = concatenate_datasets([
        qa_sample,
        bio_sample,
        events_sample,
    ]).shuffle(seed=42)

    calibration_dataset = calibration_dataset.map(
        lambda row: format_for_calibration(row, tokenizer)
    )

    return tokenize_for_calibration(
        calibration_dataset,
        tokenizer=tokenizer,
        max_length=max_length,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-per-dataset", type=int, default=32)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_DIR / "calibration_input_dict.npz"),
    )

    args = parser.parse_args()

    engine = util.get_engine()

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)

    input_dict = create_calibration_dataset(
        engine=engine,
        tokenizer=tokenizer,
        max_samples=args.samples_per_dataset,
        max_length=args.max_length,
    )

    print("Calibration shapes:")
    for key, value in input_dict.items():
        print(f"{key}: {value.shape}, {value.dtype}")

    np.savez(
        args.output,
        input_ids=input_dict["input_ids"],
        attention_mask=input_dict["attention_mask"],
    )

    print(f"Saved calibration data to {args.output}")


if __name__ == "__main__":
    main()