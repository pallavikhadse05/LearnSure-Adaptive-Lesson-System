
import ollama

MODEL_NAME = "qwen2.5:3b"

client = ollama.Client(host="http://localhost:11434")


def generate_lesson(
    topic,
    memory_guidance=None,
    retry_feedback=None,
    attempt=1
):
    memory_guidance = memory_guidance or []
    retry_feedback = retry_feedback or []

    memory_text = "\n".join(
        f"- {item}" for item in memory_guidance
    ) or "No previous guidance."

    feedback_text = "\n".join(
        f"- {item}" for item in retry_feedback
    ) or "No previous failure."

    prompt = f"""
You are a patient teacher creating lessons for beginners in India.

TOPIC: {topic}

LEARNER:
- Completed 12th grade.
- Limited English vocabulary.
- No previous knowledge of this topic.

TEACHING RULES:
1. Use simple English and short sentences.
2. Explain the topic from zero.
3. Explain why it is useful.
4. Explain how it works step by step.
5. Explain technical words.
6. Include at least two practical examples.
7. Include one real-life analogy.
8. Avoid unsupported facts.
9. Cover the important concepts.

PREVIOUS LEARNING GUIDANCE:
{memory_text}

FEEDBACK FROM PREVIOUS FAILED ATTEMPT:
{feedback_text}

ATTEMPT NUMBER:
{attempt}

WRITE THE LESSON IN THIS FORMAT:

# Title

## 1. What is this topic?

## 2. Why is it important?

## 3. How does it work?
Explain step by step.

## 4. Real-life analogy

## 5. Practical examples
Give at least two examples.

## 6. Important terms

## 7. Quick recap

Write only the lesson.
Do not include your internal reasoning.
"""

    try:
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.3,
                "num_ctx": 1024,
                "num_predict": 700
            }
        )

        lesson = response["message"]["content"].strip()

        if not lesson:
            raise ValueError("Empty lesson generated.")

        return lesson

    except Exception as error:
        raise RuntimeError(
            f"Lesson generation failed: {error}"
        )
