
# LearnSure – Adaptive Lesson Quality System

**I have also created a short Loom video explaining the project, its workflow, and implementation. You can watch the video for a quick overview.**
https://www.loom.com/share/caa71733a56844e1981892fbf33f8d91

## Overview

LearnSure is a local AI-powered lesson generation and evaluation system.

It creates beginner-friendly lessons for learners with limited English vocabulary and evaluates the content before approval.

## Problem

AI-generated educational content may contain:

- Incorrect information
- Difficult language
- Missing examples
- Unexplained technical terms
- Poor teaching flow

LearnSure uses a quality evaluation loop to identify these issues and request improvements.

## Technology Stack

- Python
- Streamlit
- Ollama
- Qwen 2.5 3B
- JSON-based persistent memory

## Architecture

1. User enters a topic.
2. The lesson builder generates content.
3. The quality evaluator checks six criteria.
4. Failed lessons are rejected.
5. Feedback is sent to the next generation attempt.
6. The system allows a maximum of two retries.
7. Rejection history and learning guidance are stored in JSON files.

## Evaluation Criteria

1. Accuracy
2. Beginner-friendly language
3. Practical examples
4. Jargon explanation
5. Key point coverage
6. Teaching flow

## Persistent Memory

The system stores:

- Total runs
- Successful runs
- Failed runs
- Improvement guidance
- Rejection history

## Setup

Install Python and Ollama.

Pull the model:

```bash
ollama pull qwen2.5:3b
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## Testing

Enter Introduction to RAG.

Enable the deliberate RAG error checkbox.

The evaluator should reject the deliberately incorrect statement and request a new generation attempt.

## Limitations

- The current RAG factual checks cover selected concepts and known errors.
- Other topics use model-based evaluation and may require human review.
- Persistent memory stores guidance and rejection history, but does not train or fine-tune the language model.
- No external verified knowledge source is connected in this prototype.

## Future Improvements

- Add trusted source retrieval.
- Add topic-specific factual evaluation.
- Improve memory using repeated failure patterns.
- Add human feedback and approval.
- Add more evaluation test cases.

