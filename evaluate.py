# Member C
from generate_answer import ask_vera, llm_client, LLM_MODEL
from golden_test_set import golden_test_set
import json
import time
import json
from datetime import datetime


def call_with_retry(func, *args, max_retries=5, **kwargs):
    """Retries a function call if we hit a rate limit, waiting progressively longer each time."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if any(keyword in str(e) for keyword in ["429", "Too Many Requests", "Empty response", "Connection error", "Server disconnected"]):
                wait_time = 30 * (attempt + 1)  # 30s, 60s, 90s, 120s, 150s
                print(f"  Rate limited — waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")


def judge_correctness(question, expected_answer, actual_answer):
    """Uses AI to judge if the actual answer means the same thing as the expected answer."""
    prompt = f"""You are a strict grading assistant. Compare the actual answer to the expected answer for the given question.
They don't need to match word-for-word, but must convey the same correct information.

Question: {question}
Expected Answer: {expected_answer}
Actual Answer: {actual_answer}

Respond ONLY in this JSON format:
{{
  "correct": <true or false>,
  "explanation": "<one sentence explaining why>"
}}"""
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    cleaned = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned)

def log_failure(question, expected, actual, trust_score, explanation, category, category_reason):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "expected_answer": expected,
        "actual_answer": actual,
        "trust_score": trust_score,
        "judge_explanation": explanation,
        "failure_category": category,
        "category_reason": category_reason
    }
    try:
        with open("failure_log.json", "r") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []
    log.append(entry)
    with open("failure_log.json", "w") as f:
        json.dump(log, f, indent=2)


def run_evaluation():
    results = []
    test_questions = golden_test_set[:2]  # TEMPORARY: only test first 2 questions for now
    for i, item in enumerate(test_questions, 1):
        question = item["question"]
        expected = item["expected_answer"]
        print(f"\n[{i}/{len(test_questions)}] Testing: {question}")

        vera_result = call_with_retry(ask_vera, question)
        judge = call_with_retry(judge_correctness, question, expected, vera_result["answer"])

        time.sleep(3)  # small pause between questions to avoid hitting rate limits

        results.append({
            "question": question,
            "expected_answer": expected,
            "actual_answer": vera_result["answer"],
            "trust_score": vera_result["trust_score"],
            "correct": judge["correct"],
            "judge_explanation": judge["explanation"]
        })

        status = "CORRECT" if judge["correct"] else "INCORRECT"
        print(f"  {status} | Trust Score: {vera_result['trust_score']}/100")
    if not judge["correct"]:
            category_result = call_with_retry(
        categorize_failure, question, expected, vera_result["answer"], vera_result["sources"]
    )
    log_failure(
        question,
        expected,
        vera_result["answer"],
        vera_result["trust_score"],
        judge["explanation"],
        category_result["category"],
        category_result["reason"]
    )
       
def categorize_failure(question, expected_answer, actual_answer, retrieved_chunks):
    """Classifies why a failure happened, using the retrieved context as evidence."""
    context_preview = "\n\n".join(retrieved_chunks)
    prompt = f"""You are analyzing why an AI system's answer was incorrect.

Question: {question}
Expected Answer: {expected_answer}
Actual Answer: {actual_answer}
Retrieved Context: {context_preview}

Classify the failure into EXACTLY ONE of these categories:
- "no_information" - the retrieved context genuinely does not contain the information needed
- "retrieval_issue" - the information likely exists in the source document, but the wrong sections were retrieved
- "generation_issue" - the right information was retrieved, but the answer was still wrong

Respond ONLY in this JSON format:
{{
  "category": "<one of the three categories above>",
  "reason": "<one sentence explaining your classification>"
}}"""
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    content = response.choices[0].message.content
    if content is None:
        raise Exception("Empty response from model - likely a transient issue")
    cleaned = content.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned)

    # Summary
    total = len(results)
    correct_count = sum(1 for r in results if r["correct"])
    avg_trust = sum(r["trust_score"] for r in results) / total

    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total Questions: {total}")
    print(f"Correct Answers: {correct_count}/{total} ({correct_count/total*100:.1f}%)")
    print(f"Average Trust Score: {avg_trust:.1f}/100")

    failures = [r for r in results if not r["correct"]]
    if failures:
        print(f"\n--- Failed Questions ({len(failures)}) ---")
        for f in failures:
            print(f"\nQ: {f['question']}")
            print(f"Expected: {f['expected_answer']}")
            print(f"Got: {f['actual_answer']}")
            print(f"Why wrong: {f['judge_explanation']}")

    return results


if __name__ == "__main__":
    run_evaluation()