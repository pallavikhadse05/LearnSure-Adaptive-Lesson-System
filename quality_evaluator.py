
import ollama
import json
import re

MODEL_NAME = "qwen2.5:3b"

client = ollama.Client(host="http://localhost:11434")


def check_rag_facts(topic, lesson):

    if "rag" not in topic.lower():
        return []

    text = lesson.lower()
    issues = []

    if "random answer generation" in text:
        issues.append(
            "RAG does not stand for Random Answer Generation."
        )

    retrieval_words = [
        "retrieve", "retrieval", "search", "fetch"
    ]

    if not any(word in text for word in retrieval_words):
        issues.append(
            "Explain how relevant information is retrieved."
        )

    source_words = [
        "knowledge base", "external source",
        "documents", "database"
    ]

    if not any(word in text for word in source_words):
        issues.append(
            "Explain where the information comes from."
        )

    if "context" not in text:
        issues.append(
            "Explain how retrieved information is used as context."
        )

    generation_words = [
        "language model", "llm",
        "generates an answer", "generate an answer"
    ]

    if not any(word in text for word in generation_words):
        issues.append(
            "Explain how the language model generates the answer."
        )

    return issues


def evaluate_lesson(topic, lesson):

    if not lesson or not lesson.strip():
        return {
            "overall_status": "FAIL",
            "checks": {},
            "feedback": ["The lesson is empty."],
            "suggestions": ["Generate the lesson again."]
        }

    prompt = f"""
You are a strict lesson quality evaluator.

TOPIC: {topic}

LESSON:
{lesson}

LEARNER:
A beginner with limited English vocabulary.

Evaluate these six criteria:

1. accuracy
2. beginner_friendly
3. practical_examples
4. jargon_explanation
5. key_points
6. teaching_flow

Give PASS only when the criterion is properly satisfied.
Otherwise give FAIL.

Return only JSON in this format:

{{
 "checks": {{
  "accuracy": {{"status": "PASS", "reason": "Reason"}},
  "beginner_friendly": {{"status": "PASS", "reason": "Reason"}},
  "practical_examples": {{"status": "PASS", "reason": "Reason"}},
  "jargon_explanation": {{"status": "PASS", "reason": "Reason"}},
  "key_points": {{"status": "PASS", "reason": "Reason"}},
  "teaching_flow": {{"status": "PASS", "reason": "Reason"}}
 }}
}}

Use only PASS or FAIL.
Be strict. Do not approve incomplete lessons.
"""

    try:
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0,
                "num_ctx": 1024,
                "num_predict": 400
            }
        )

        response_text = response["message"]["content"]

        match = re.search(
            r"\{.*\}",
            response_text,
            re.DOTALL
        )

        if not match:
            raise ValueError("Invalid JSON from evaluator.")

        result = json.loads(match.group())

        required_checks = [
            "accuracy",
            "beginner_friendly",
            "practical_examples",
            "jargon_explanation",
            "key_points",
            "teaching_flow"
        ]

        checks = result.get("checks", {})

        for name in required_checks:

            if name not in checks:
                raise ValueError(f"Missing check: {name}")

            status = checks[name].get("status", "").upper()

            if status not in ["PASS", "FAIL"]:
                raise ValueError(f"Invalid status: {name}")

            checks[name]["status"] = status

        feedback = []

        for name in required_checks:
            if checks[name]["status"] == "FAIL":
                feedback.append(
                    f"{name}: {checks[name].get('reason', 'Failed')}"
                )

        rag_issues = check_rag_facts(topic, lesson)
        feedback.extend(rag_issues)

        if rag_issues:
            checks["accuracy"]["status"] = "FAIL"
            checks["accuracy"]["reason"] = (
                "Additional RAG factual checks failed."
            )

        passed = all(
            checks[name]["status"] == "PASS"
            for name in required_checks
        )

        return {
            "overall_status": "PASS" if passed else "FAIL",
            "checks": checks,
            "feedback": feedback,
            "suggestions": [
                "Correct the failed points.",
                "Explain missing concepts clearly.",
                "Use simple examples."
            ] if feedback else []
        }

    except Exception as error:

        return {
            "overall_status": "FAIL",
            "checks": {},
            "feedback": [
                f"Evaluation failed: {error}"
            ],
            "suggestions": [
                "Check Ollama and try again."
            ]
        }
