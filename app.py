
import streamlit as st
import os
import json

from lesson_builder import generate_lesson
from quality_evaluator import evaluate_lesson
from learning_memory import (
    load_memory,
    load_rejection_log,
    update_memory,
    save_rejection
)

MAX_RETRIES = 2

OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(
    page_title="LearnSure",
    page_icon="📘",
    layout="wide"
)

st.title("📘 LearnSure")
st.subheader("Adaptive Lesson Quality System")

st.write(
    "Generate beginner-friendly lessons and improve them "
    "using automatic quality evaluation."
)

topic = st.text_input(
    "Enter your lesson topic",
    placeholder="Example: Introduction to RAG"
)

deliberate_error = st.checkbox(
    "Inject a deliberate RAG error (for testing)"
)

if st.button("Generate and Evaluate Lesson", type="primary"):

    if not topic.strip():
        st.warning("Please enter a topic.")

    else:

        try:
            memory = load_memory()
            guidance = memory.get("guidance", [])

            feedback = []
            attempt_history = []
            final_lesson = ""
            final_evaluation = None
            passed = False

            progress = st.progress(0)
            status = st.empty()

            total_attempts = MAX_RETRIES + 1

            for attempt in range(1, total_attempts + 1):

                status.info(
                    f"Generating lesson: Attempt {attempt}"
                )

                lesson = generate_lesson(
                    topic=topic,
                    memory_guidance=guidance,
                    retry_feedback=feedback,
                    attempt=attempt
                )

                # Add a known false statement for the demo
                if deliberate_error and attempt == 1:
                    if "rag" in topic.lower():
                        lesson += (
                            "\n\nIncorrect test statement: "
                            "RAG stands for Random Answer Generation."
                        )

                status.info(
                    f"Evaluating lesson: Attempt {attempt}"
                )

                evaluation = evaluate_lesson(topic, lesson)

                attempt_history.append({
                    "attempt": attempt,
                    "status": evaluation["overall_status"],
                    "feedback": evaluation.get("feedback", [])
                })

                if evaluation["overall_status"] == "PASS":

                    final_lesson = lesson
                    final_evaluation = evaluation
                    passed = True

                    progress.progress(100)
                    break

                # Save every rejected attempt
                save_rejection(
                    topic,
                    attempt,
                    evaluation,
                    changed_on_retry=(
                        "Feedback was sent to the next generation attempt."
                        if attempt < total_attempts else
                        "No retries remaining."
                    )
                )

                feedback = evaluation.get("feedback", [])

                final_lesson = lesson
                final_evaluation = evaluation

                progress.progress(
                    int(attempt / total_attempts * 100)
                )

            # Update persistent memory once per complete run
            update_memory(final_evaluation)

            st.divider()

            if passed:

                st.success(
                    "PASS — Lesson approved by the evaluator."
                )

                output_path = os.path.join(
                    OUTPUT_DIR,
                    "final_lesson.md"
                )

                with open(
                    output_path,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(final_lesson)

                st.markdown(final_lesson)

                st.download_button(
                    "Download Approved Lesson",
                    data=final_lesson,
                    file_name="final_lesson.md",
                    mime="text/markdown"
                )

            else:

                st.error(
                    "FAIL — Lesson did not pass after the allowed attempts."
                )

                st.warning(
                    "This draft is not approved. Review the feedback before using it."
                )

                draft_path = os.path.join(
                    OUTPUT_DIR,
                    "unapproved_draft.md"
                )

                with open(
                    draft_path,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(final_lesson)

                st.markdown(final_lesson)

                st.download_button(
                    "Download Unapproved Draft",
                    data=final_lesson,
                    file_name="unapproved_draft.md",
                    mime="text/markdown"
                )

            with st.expander("Evaluation details"):

                st.json(final_evaluation)

            with st.expander("Attempt history"):

                st.json(attempt_history)

            with st.expander("Persistent memory"):

                st.json(load_memory())

            with st.expander("Rejection log"):

                st.json(load_rejection_log())

        except Exception as error:

            st.error(f"Something went wrong: {error}")
            st.info(
                "Check that Ollama is running and Qwen 2.5 3B is installed."
            )
