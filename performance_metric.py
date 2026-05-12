import time
import json
import pandas as pd
import requests
from pathlib import Path

INPUT_CSV = "hist_fig_sample.csv" # Data generated from dataset_sampler.py
OUTPUT_CSV = "ollama_biography_results.csv"

OLLAMA_URL = "http://localhost:11434/api/chat" #UPDATE THIS DEPENDING ON PORT USED !
MODEL_NAME = "qwen2.5:1.5b"

HARDWARE_LABEL = "rtx_5070_ubuntu"  # UPDATE THIS DEPENDING ON HARDWARE!

TEMPERATURE = 0
TOP_P = 1
TOP_K = 1
SEED = 42

def build_prompt(name: str) -> str:
    return f"""
Write a factual biography of the historical figure: {name}.

Focus on:
- who they were
- where/when they lived
- why they are historically significant
- major accomplishments or events associated with them

Keep the biography concise but informative.
"""

def call_ollama(name: str) -> dict:
    prompt = build_prompt(name)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a world history assistant. Provide factual, historically grounded answers."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "top_k": TOP_K,
            "seed": SEED
        }
    }

    start_time = time.perf_counter()

    response = requests.post(
        OLLAMA_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=300
    )

    end_time = time.perf_counter()
    total_time_seconds = end_time - start_time

    response.raise_for_status()
    data = response.json()

    generated_text = data.get("message", {}).get("content", "")

    # Ollama durations are usually in nanoseconds
    eval_count = data.get("eval_count")
    eval_duration = data.get("eval_duration")
    prompt_eval_count = data.get("prompt_eval_count")
    prompt_eval_duration = data.get("prompt_eval_duration")
    total_duration = data.get("total_duration")
    load_duration = data.get("load_duration")

    tokens_per_second = None
    if eval_count and eval_duration and eval_duration > 0:
        tokens_per_second = eval_count / (eval_duration / 1e9)

    return {
        "name": name,
        "hardware": HARDWARE_LABEL,
        "model": MODEL_NAME,
        "prompt": prompt.strip(),
        "generated_biography": generated_text.strip(),
        "response_chars": len(generated_text),
        "response_words": len(generated_text.split()),
        "measured_total_time_seconds": total_time_seconds,
        "ollama_total_duration_ns": total_duration,
        "ollama_load_duration_ns": load_duration,
        "ollama_prompt_eval_count": prompt_eval_count,
        "ollama_prompt_eval_duration_ns": prompt_eval_duration,
        "ollama_eval_count": eval_count,
        "ollama_eval_duration_ns": eval_duration,
        "tokens_per_second": tokens_per_second,
        "raw_response_json": json.dumps(data)
    }

def main():
    input_path = Path(INPUT_CSV)

    if not input_path.exists():
        raise FileNotFoundError(f"Could not find input CSV: {INPUT_CSV}")

    df = pd.read_csv(input_path)

    required_columns = {"name", "biography"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")

    results = []

    for index, row in df.iterrows():
        name = str(row["name"]).strip()
        original_biography = str(row["biography"]).strip()

        print(f"[{index + 1}/{len(df)}] Generating biography for: {name}")

        try:
            result = call_ollama(name)
            result["original_biography"] = original_biography

            results.append(result)

        except Exception as e:
            print(f"[ERROR] Failed for {name}: {e}")

            results.append({
                "name": name,
                "hardware": HARDWARE_LABEL,
                "model": MODEL_NAME,
                "prompt": build_prompt(name).strip(),
                "generated_biography": "",
                "original_biography": original_biography,
                "error": str(e)
            })

    output_df = pd.DataFrame(results)
    output_df.to_csv(OUTPUT_CSV, index=False)

    print(f"\nSaved results to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()