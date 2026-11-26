def validate_plan(plan: dict) -> None:
    """
    Validate a test plan dictionary.

    Args:
        plan (dict): The test plan to validate.

    Raises:
        ValueError: If the test plan is not a dictionary.
    """
    if not isinstance(plan, dict):
        raise ValueError("The test plan must be a JSON object (dictionary).")

    plan_id = plan.get("plan_id")
    if not isinstance(plan_id, str) or not plan_id.strip():
        raise ValueError("The test plan must have a non-empty plan_id string.")


    steps = plan.get("steps")
    seen_ids = set()

    if not isinstance(steps, list) or not steps:
        raise ValueError("The test plan must have a non-empty steps list.")
    
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("Each step must be an object.")

        step_id = step.get("id")

        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError("Each step must have a non-empty id string.")
        
        if step_id in seen_ids:
            raise ValueError(f"Duplicate step id '{step_id}' found.")
        
        seen_ids.add(step_id)

        request = step.get("request")

        if not isinstance(request, dict):
            raise ValueError("Each step must contain a request object.")

        method = request.get("method")

        if method not in ("GET", "POST", "DELETE"):
            raise ValueError("Supported methods are GET, POST, DELETE.")    

        path = request.get("path")

        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError("Request path must start with '/'.")

        if (
            path.startswith("//")
            or "\\" in path
            or "?" in path
            or "#" in path
            or "%" in path
            or any(part in (".", "..") for part in path.split("/"))
        ):
            raise ValueError("Request path contains unsupported syntax.")
        
        assertions = step.get("assertions", [])

        if not isinstance(assertions, list):
            raise ValueError("assertions must be a list.")

        for assertion in assertions:
            if not isinstance(assertion, dict):
                raise ValueError("Each assertion must be an object.")

            assertion_type = assertion.get("type")

            if assertion_type not in ("status_code", "json_equals"):
                raise ValueError("Unsupported assertion type.")

            requirement_id = assertion.get("requirement_id")

            if not isinstance(requirement_id, str) or not requirement_id.strip():
                raise ValueError("Assertion must reference a requirement.")

            if assertion_type == "status_code":
                expected = assertion.get("equals")

                if type(expected) is not int or not 100 <= expected <= 599:
                    raise ValueError(
                        "Expected status must be an integer from 100 to 599."
                    )

            elif assertion_type == "json_equals":
                pointer = assertion.get("pointer")

                if (
                    not isinstance(pointer, str)
                    or not pointer.startswith("/")
                    or "/" in pointer[1:]
                    or "~" in pointer
                ):
                    raise ValueError(
                        "Only simple top-level pointers are supported."
                    )

                if "equals" not in assertion:
                    raise ValueError("JSON assertion must contain equals.")