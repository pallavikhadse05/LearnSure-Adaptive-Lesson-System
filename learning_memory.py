
import json
import os
from datetime import datetime

DATA_DIR = "data"

MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
REJECTION_FILE = os.path.join(DATA_DIR, "rejection_log.json")


def ensure_data_files():

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(MEMORY_FILE):
        default_memory = {
            "runs_seen": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "guidance": [
                "Assume the learner starts from zero.",
                "Use short and simple sentences.",
                "Explain technical words.",
                "Teach concepts with practical examples."
            ]
        }

        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(default_memory, file, indent=4)

    if not os.path.exists(REJECTION_FILE):
        with open(REJECTION_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def load_memory():

    ensure_data_files()

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_rejection_log():

    ensure_data_files()

    with open(REJECTION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def update_memory(evaluation):

    memory = load_memory()

    memory["runs_seen"] += 1

    if evaluation["overall_status"] == "PASS":
        memory["successful_runs"] += 1
    else:
        memory["failed_runs"] += 1

    for feedback in evaluation.get("feedback", []):

        guidance = (
            "Improve this recurring issue: " + feedback
        )

        if guidance not in memory["guidance"]:
            memory["guidance"].append(guidance)

    memory["guidance"] = memory["guidance"][-20:]

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)


def save_rejection(topic, attempt, evaluation, changed_on_retry=""):

    logs = load_rejection_log()

    entry = {
        "topic": topic,
        "attempt": attempt,
        "date": datetime.now().isoformat(timespec="seconds"),
        "status": evaluation["overall_status"],
        "failed_checks": evaluation.get("feedback", []),
        "suggestions": evaluation.get("suggestions", []),
        "changed_on_retry": changed_on_retry
    }

    logs.append(entry)

    with open(REJECTION_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=4)
