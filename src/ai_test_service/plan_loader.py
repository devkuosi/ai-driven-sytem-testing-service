import json
from pathlib import Path
from ai_test_service.validation import validate_plan

def load_plan(path: str | Path) -> dict:
    """
    Load a test plan from a JSON file.

    Args:
        path (str | Path): The path to the JSON file containing the test plan.

    Returns:
        dict: The loaded test plan as a dictionary.
    """
    with Path(path).open("r", encoding="utf-8") as file:
        plan = json.load(file)

    if not isinstance(plan, dict):
        raise ValueError("The test plan must be a JSON object (dictionary).")
    
    return plan

def load_and_validate_plan(path: str | Path) -> dict:
    plan = load_plan(path)
    validate_plan(plan)
    return plan