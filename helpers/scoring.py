from sklearn.metrics import f1_score
import re
from query import ask_email_agent2
import json
from datetime import datetime
from pathlib import Path
import csv

def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())

def compute_exact_match(pred, true):
    return normalize(pred) == normalize(true)

def compute_f1(pred, true):
    pred_tokens = normalize(pred).split()
    true_tokens = normalize(true).split()
    common = set(pred_tokens) & set(true_tokens)

    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(true_tokens)
    return 2 * (precision * recall) / (precision + recall)

def evaluate_rag(test_cases):
    scores = []

    for case in test_cases:
        print(f"\n🧪 Question: {case['question']}")
        pred = ask_email_agent2(case["question"])
        
        em = compute_exact_match(pred, case["expected_answer"])
        f1 = compute_f1(pred, case["expected_answer"])
        
        print(f"✅ Expected: {case['expected_answer']}")
        print(f"🤖 Predicted: {pred}")
        print(f"📊 EM: {em}, F1: {f1:.2f}")

        scores.append({
            "question": case["question"],
            "expected": case["expected_answer"],
            "predicted": pred,
            "em": em,
            "f1": f1
        })

    return scores


def log_results_to_json(results, output_path="rag_eval_results.json"):
    output = Path(output_path)
    if output.exists():
        existing = json.loads(output.read_text())
    else:
        existing = []

    existing.extend(results)
    output.write_text(json.dumps(existing, indent=2))
    print(f"✅ Logged {len(results)} results to {output_path}")


def log_results_to_csv(results, output_path="rag_eval_results.csv"):
    fieldnames = ["question", "expected_answer", "predicted_answer", "exact_match", "f1_score"]

    with open(output_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        for r in results:
            writer.writerow({
                "question": r["question"],
                "expected_answer": r["expected"],
                "predicted_answer": r["predicted"],
                "exact_match": r["em"],
                "f1_score": round(r["f1"], 2)
            })

    print(f"✅ Logged {len(results)} results to {output_path}")