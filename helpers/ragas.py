from ragas.metrics import faithfulness, answer_relevancy, context_recall
from ragas import evaluate
from datasets import Dataset

# Prepare Dataset
data = [
    {
        "question": "Who will attend Project Phoenix kickoff?",
        "contexts": ["Alice and Bob will attend.", "QA and DevOps are also joining."],
        "answer": "Alice, Bob, QA, and DevOps",
        "ground_truth": "Alice, Bob, QA Team, DevOps Team"
    }
]

ds = Dataset.from_list(data)

# Run Evaluation
report = evaluate(ds, metrics=[faithfulness, context_recall, answer_relevancy])
print(report)
