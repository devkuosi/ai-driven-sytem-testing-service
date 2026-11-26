def check_status_code(actual: int, expected: int) -> bool:
    """Return True when the actual status matches the expected status."""
    return actual == expected


def get_json_field(body: dict, pointer: str):
    """Read a top-level JSON field, such as /items."""
    if (
        not pointer.startswith("/")
        or "/" in pointer[1:]
        or "~" in pointer
    ):
        raise ValueError("Only simple top-level pointers are supported.")

    field = pointer[1:]

    if field not in body:
        raise KeyError(f"JSON field is missing: {field}")

    return body[field]

def check_json_equals(body: dict, pointer: str, expected) -> bool:
    """Compare a top-level JSON field with its expected value."""
    try:
        actual = get_json_field(body, pointer)
    except KeyError:
        return False

    # Distinguish values such as True and 1, including nested values.
    return json_values_equal(actual, expected)


def json_values_equal(actual, expected) -> bool:
    """Compare JSON values without treating booleans as numbers."""
    if type(actual) is not type(expected):
        return False

    if isinstance(actual, list):
        return (
            len(actual) == len(expected)
            and all(
                json_values_equal(a, e)
                for a, e in zip(actual, expected)
            )
        )

    if isinstance(actual, dict):
        return (
            actual.keys() == expected.keys()
            and all(
                json_values_equal(actual[key], expected[key])
                for key in actual
            )
        )

    return actual == expected