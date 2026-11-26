import httpx

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

            results.append({
                "step_id": step["id"],
                "status_code": response.status_code,
                "body": response.json() if response.content else None
            })

    return results