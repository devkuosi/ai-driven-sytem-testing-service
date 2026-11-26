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
                "body": {"status": "ok"},
            }
        ],
    }

    results = run_plan(plan)
    assert calls == [("GET", "/health")]
    assert results == [
        {"step_id": "check-health", "status_code": 200, "body": {"status": "ok"}}
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