import pytest

from ai_test_service.validation import validate_plan

def test_validate_plan_valid():
    plan = {
        "plan_id": "123",
        "steps": [
            {
                "id": "example",
                "request": {
                    "method": "GET",
                    "path": "/users"
                }
            }
        ]
    }
    validate_plan(plan)

def test_validate_plan_missing_plan_id():
    plan = {
        "steps": [{"action": "do_something"}]
    }
    with pytest.raises(ValueError, match="The test plan must have a non-empty plan_id string."):
        validate_plan(plan)

def test_validate_plan_empty_steps():
    plan = {
        "plan_id": "123",
        "steps": []
    }
    with pytest.raises(ValueError, match="The test plan must have a non-empty steps list."):
        validate_plan(plan)

def test_validate_plan_step_not_dict():
    plan = {
        "plan_id": "123",
        "steps": ["not_a_dict"]
    }
    with pytest.raises(ValueError, match="Each step must be an object."):
        validate_plan(plan)

def test_validate_plan_not_dict():
    plan = "not_a_dict"
    with pytest.raises(ValueError, match="The test plan must be a JSON object \\(dictionary\\)."):
        validate_plan(plan)

@pytest.mark.parametrize(
    "step",
    [
        "invalid",
        {"id": "example"},
        {"request": {"method": "PATCH", "path": "/users"}},
    ],
)
def test_rejects_invalid_request(step):
    with pytest.raises(ValueError):
        validate_plan({
            "plan_id": "example",
            "steps": [step],
        })


def test_accepts_supported_request():
    validate_plan({
        "plan_id": "example",
        "steps": [
            {
                "id": "find-users",
                "request": {
                    "method": "GET",
                    "path": "/users",
                },
            }
        ],
    })        

@pytest.mark.parametrize(
    "path",
    [
        None,
        "users",
        "https://other-site.test/users",
        "//other-site.test/users",
        "/../users",
        "/users?email=test",
        "/users#fragment",
        "/%2e%2e/users",
        "/users\\other",
    ],
)
def test_rejects_invalid_request_path(path):
    with pytest.raises(ValueError, match="Request path"):
        validate_plan({
            "plan_id": "example",
            "steps": [
                {
                    "id": "find-users",
                    "request": {
                        "method": "GET",
                        "path": path,
                    },
                }
            ],
        })  

@pytest.mark.parametrize("step_id", [None, "", "   "])
def test_rejects_invalid_step_id(step_id):
    with pytest.raises(ValueError, match="non-empty id"):
        validate_plan({
            "plan_id": "example",
            "steps": [
                {
                    "id": step_id,
                    "request": {"method": "GET", "path": "/users"},
                }
            ],
        })


def test_rejects_duplicate_step_ids():
    with pytest.raises(ValueError, match="Duplicate step id"):
        validate_plan({
            "plan_id": "example",
            "steps": [
                {
                    "id": "find-users",
                    "request": {"method": "GET", "path": "/users"},
                },
                {
                    "id": "find-users",
                    "request": {"method": "GET", "path": "/users"},
                },
            ],
        })

@pytest.mark.parametrize(
    "expected",
    [200, 422, "200", None, True, 99, 600],
)
def test_status_assertion_validation(expected):
    plan = {
        "plan_id": "health",
        "steps": [
            {
                "id": "check-health",
                "request": {"method": "GET", "path": "/health"},
                "assertions": [
                    {
                        "type": "status_code",
                        "equals": expected,
                        "requirement_id": "DEMO-HEALTH",
                    }
                ],
            }
        ],
    }

    if type(expected) is int and expected in (200, 422):
        validate_plan(plan)
    else:
        with pytest.raises(ValueError, match="Expected status"):
            validate_plan(plan)

def test_accepts_json_equals_assertion():
    validate_plan({
        "plan_id": "verify-no-user",
        "steps": [
            {
                "id": "find-user",
                "request": {"method": "GET", "path": "/users"},
                "assertions": [
                    {
                        "type": "json_equals",
                        "pointer": "/items",
                        "equals": [],
                        "requirement_id": "DEMO-04",
                    }
                ],
            }
        ],
    })

