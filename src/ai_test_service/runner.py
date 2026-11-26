import httpx

from ai_test_service.assertions import check_status_code, check_json_equals, get_json_field
from ai_test_service.validation import validate_plan

def run_plan(plan: dict) -> list[dict]:
    """ Execute basic requests aigainst the local demontration API.

    Args:
        plan (dict): The test plan to execute.

    Returns:
        list[dict]: A list of responses for each step in the plan.
    """
    validate_plan(plan)
    results = []
    with httpx.Client(
        base_url="http://localhost:8001",
        timeout=5,
        follow_redirects=False,
        trust_env=False,
    ) as client:
        for step in plan["steps"]:
            request = step["request"]

            try:
                response = client.request(
                    method=request["method"],
                    url=request["path"],
                    params=request.get("params"),
                    json=request.get("json")
                )
            except httpx.TimeoutException:
                results.append({
                    "step_id": step["id"],
                    "error": "Request timed out",
                })
                break
            except httpx.RequestError as e:
                results.append({
                    "step_id": step["id"],
                    "error": f"Request failed: {str(e)}",
                })
                break

            result = {
                "step_id": step["id"],
                "status_code": response.status_code
            }

            assertions = step.get("assertions", [])

            if assertions:
                assertion_results = []

                for assertion in assertions:
                    expected = assertion["equals"]
                    assertion_type = assertion["type"]
                    detail = None

                    if assertion_type == "status_code":
                        actual = response.status_code
                        passed = check_status_code(actual, expected)

                    else:
                        pointer = assertion["pointer"]

                        try:
                            body = response.json()
                        except ValueError:
                            actual = None
                            passed = False
                            detail = "Response is not valid JSON."
                        else:
                            if not isinstance(body, dict):
                                actual = None
                                passed = False
                                detail = "Response JSON must be an object."
                            else:
                                try:
                                    actual = get_json_field(body, pointer)
                                except KeyError:
                                    actual = None
                                    passed = False
                                    detail = f"JSON field is missing: {pointer}"
                                else:
                                    passed = check_json_equals(
                                        body, pointer, expected
                                    )

                    assertion_result = {
                        "requirement_id": assertion["requirement_id"],
                        "expected": expected,
                        "actual": actual,
                        "passed": passed,
                    }

                    if detail:
                        assertion_result["detail"] = detail

                    assertion_results.append(assertion_result)

                result["assertion_results"] = assertion_results

            results.append(result)

    return results