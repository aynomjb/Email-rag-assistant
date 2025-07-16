from helpers.scoring import (
    evaluate_rag,
    log_results_to_json,
    log_results_to_csv
)


test_cases = [
    {
        "question": "When is the kickoff meeting for Project Phoenix scheduled?",
        "expected_answer": "Tuesday at 2 PM"
    },
    {
        "question": "Who is expected to attend the Project Phoenix kickoff meeting?",
        "expected_answer": "Alice, Bob, DevOps Team, QA Team"
    },
    {
        "question": "What will be discussed during the kickoff meeting?",
        "expected_answer": "Scope and objectives, Sprint 0 planning, Risk identification"
    }
]
results = evaluate_rag(test_cases)
log_results_to_json(results, "rag_results.json")
log_results_to_csv(results, "rag_results.csv")