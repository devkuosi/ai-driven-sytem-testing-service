import pytest

from ai_test_service.plan_loader import load_plan, load_and_validate_plan


def test_load_plan(tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text('{"key": "value"}', encoding="utf-8")
    plan = load_plan(plan_file)
    assert plan == {"key": "value"}

def test_load_plan_invalid_json(tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text('["not", "a", "dict"]', encoding="utf-8")
    with pytest.raises(ValueError, match="The test plan must be a JSON object"):
        load_plan(plan_file)

def test_load_validated_plan_accepts_valid_file(tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(
        '''
        {
            "plan_id": "example",
            "steps": [
                {
                    "id": "find-users",
                    "request": {
                        "method": "GET",
                        "path": "/users"
                    }
                }
            ]
        }
        ''',
        encoding="utf-8",
    )

    plan = load_and_validate_plan(plan_file)

    assert plan["plan_id"] == "example"


def test_load_validated_plan_rejects_invalid_file(tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(
        '{"plan_id": "example", "steps": []}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="steps"):
        load_and_validate_plan(plan_file)