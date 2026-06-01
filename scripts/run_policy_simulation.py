import csv
from pathlib import Path

INPUT_FILE = Path("data/promptware_test_cases.csv")
OUTPUT_FILE = Path("results/policy_simulation_results.csv")


def decide_tool_permission(row):
    prompt = row["prompt"].lower()

    blocked_patterns = [
        ".env",
        "api key",
        "token",
        "ssh key",
        "credential",
        "home directory",
        "shell",
        "curl",
        "wget",
        "npm install",
        "pip install",
        "delete",
        "upload",
        "external url",
    ]

    for pattern in blocked_patterns:
        if pattern in prompt:
            return "Denied"

    return row["tool_permission"]


def decide_final_action(row, tool_result):
    shield_decision = row["shield_decision"].lower()

    if "high" in shield_decision:
        if tool_result == "Denied":
            return "Block"
        return "Human Review"

    if "suspicious" in shield_decision:
        return "Block"

    return "Allow"


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    output_rows = []

    for row in rows:
        tool_result = decide_tool_permission(row)
        final_action = decide_final_action(row, tool_result)

        output_rows.append({
            "test_id": row["test_id"],
            "attack_type": row["attack_type"],
            "expected_nova": row["expected_nova"],
            "shield_decision": row["shield_decision"],
            "tool_permission_result": tool_result,
            "final_action": final_action,
            "notes": row["notes"],
        })

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "test_id",
            "attack_type",
            "expected_nova",
            "shield_decision",
            "tool_permission_result",
            "final_action",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Policy simulation completed. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
