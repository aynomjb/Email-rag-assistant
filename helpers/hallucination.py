import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def hallucination_score(answer: str, context: str) -> float:
    """
    Returns a score from 0 to 1 indicating % of answer sentences found in context.
    """
    answer_sentences = sent_tokenize(answer)
    found = 0
    for sent in answer_sentences:
        if sent.lower() in context.lower():
            found += 1

    if not answer_sentences:
        return 1.0  # empty = no hallucination

    return found / len(answer_sentences)



def check_for_hallucination(predicted_answer: str, context: str) -> bool:
    """
    Returns True if hallucination is detected (i.e., content not found in context).
    """
    norm_answer = predicted_answer.lower().strip()
    norm_context = context.lower()

    return norm_answer not in norm_context

test_cases = [
    {
        "question": "Who is expected to attend the Project Phoenix kickoff meeting?",
        "expected_answer": "Alice, Bob, DevOps Team, QA Team"
    }
]

# Your existing function (must return answer + context)
def ask_email_agent_with_context(question):
    predicted = "Alice, Bob, QA Team, and Sales Team"  # <- hallucinated "Sales"
    context = """
    The kickoff meeting for Project Phoenix is scheduled for Tuesday at 2 PM.
    The following individuals are expected to attend:
    1. Alice (Project Manager)
    2. Bob
    3. DevOps Team
    4. QA Team
    """
    return predicted, context

results = evaluate_with_hallucination(test_cases, ask_email_agent_with_context)
log_results_to_csv(results)
