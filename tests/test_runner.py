import httpx
import pytest

from ai_test_service.runner import run_plan

def test_runner_plan(monkeypatch):
    calls=[]

    def mock_request(self, method, url, **kwargs):
        calls.append((method, url))
        response = httpx.Response(200, json={"status": "ok"})
        return response

    # Replace real HTTP requests during this test.
    monkeypatch.setattr(httpx.Client, "request", mock_request)

    plan = {
        "plan_id": "demo-health",
        "steps": [
            {
                "id": "check-health",
                "request": {
                    "method": "GET",
                    "path": "/health",
                },
            }
        ],
    }

    results = run_plan(plan)
    assert calls == [("GET", "/health")]
    assert results == [
        {"step_id": "check-health", "status_code": 200}
    ]

def test_runner_validates_entire_plan_before_sending_requests(monkeypatch):
    calls = []

    def fake_request(self, method, url, **kwargs):
        calls.append((method, url))
        return httpx.Response(200)

    monkeypatch.setattr(httpx.Client, "request", fake_request)

    plan = {
        "plan_id": "invalid-plan",
        "steps": [
            {
                "id": "valid-first-step",
                "request": {"method": "GET", "path": "/health"},
            },
            {
                "id": "invalid-second-step",
                "request": {"method": "PATCH", "path": "/users"},
            },
        ],
    }

    with pytest.raises(ValueError, match="Supported methods"):
        run_plan(plan)

    assert calls == []    

def test_runner_records_timeout(monkeypatch):
    def fake_request(self, method, url, **kwargs):
        raise httpx.ReadTimeout("Simulated timeout")

    monkeypatch.setattr(httpx.Client, "request", fake_request)

    plan = {
        "plan_id": "timeout-example",
        "steps": [
            {
                "id": "check-health",
                "request": {"method": "GET", "path": "/health"},
            }
        ],
    }

    assert run_plan(plan) == [
        {
            "step_id": "check-health",
            "error": "Request timed out",
        }
    ] 

def test_runner_records_connection_error(monkeypatch):
    def fake_request(self, method, url, **kwargs):
        raise httpx.ConnectError("Simulated connection failure")

    monkeypatch.setattr(httpx.Client, "request", fake_request)

    plan = {
        "plan_id": "connection-error-example",
        "steps": [
            {
                "id": "check-health",
                "request": {"method": "GET", "path": "/health"},
            }
        ],
    }

    assert run_plan(plan) == [
        {
            "step_id": "check-health",
            "error": "Request failed: Simulated connection failure"
        }
    ]       


def test_runner_sends_json_and_query_parameters(monkeypatch):
    calls = []

    def fake_request(self, method, url, **kwargs):
        calls.append({
            "method": method,
            "path": url,
            "params": kwargs.get("params"),
            "json": kwargs.get("json"),
        })
        return httpx.Response(200)

    monkeypatch.setattr(httpx.Client, "request", fake_request)

    plan = {
        "plan_id": "registration-example",
        "steps": [
            {
                "id": "register-user",
                "request": {
                    "method": "POST",
                    "path": "/users",
                    "json": {
                        "email": "test@example.test",
                        "age": 17,
                    },
                },
            },
            {
                "id": "find-user",
                "request": {
                    "method": "GET",
                    "path": "/users",
                    "params": {"email": "test@example.test"},
                },
            },
        ],
    }

    run_plan(plan)

    assert calls == [
        {
            "method": "POST",
            "path": "/users",
            "params": None,
            "json": {"email": "test@example.test", "age": 17},
        },
        {
            "method": "GET",
            "path": "/users",
            "params": {"email": "test@example.test"},
            "json": None,
        },
    ]    

@pytest.mark.parametrize(
    "actual, expected_passed",
    [(200, True), (500, False)],
)
def test_runner_evaluates_status_assertion(
    monkeypatch, actual, expected_passed
):
    def fake_request(self, method, url, **kwargs):
        return httpx.Response(actual)

    monkeypatch.setattr(httpx.Client, "request", fake_request)

    plan = {
        "plan_id": "health",
        "steps": [
            {
                "id": "check-health",
                "request": {"method": "GET", "path": "/health"},
                "assertions": [
                    {
                        "type": "status_code",
                        "equals": 200,
                        "requirement_id": "DEMO-HEALTH",
                    }
                ],
            }
        ],
    }

    results = run_plan(plan)

    assert results[0]["assertion_results"] == [
        {
            "requirement_id": "DEMO-HEALTH",
            "expected": 200,
            "actual": actual,
            "passed": expected_passed,
        }
    ]

@pytest.mark.parametrize(
    "body, expected_passed",
    [
        ({"items": []}, True),
        ({"items": [{"id": "unexpected-user"}]}, False),
        ({}, False),
    ],
)
def test_runner_evaluates_json_assertion(
    monkeypatch, body, expected_passed
):
    def fake_request(self, method, url, **kwargs):
        return httpx.Response(200, json=body)

    monkeypatch.setattr(httpx.Client, "request", fake_request)

    plan = {
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
    }

    results = run_plan(plan)
    assertion = results[0]["assertion_results"][0]

    assert assertion["passed"] is expected_passed

    if "items" not in body:
        assert assertion["detail"] == "JSON field is missing: /items"
