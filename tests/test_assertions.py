import pytest

from ai_test_service.assertions import check_status_code


@pytest.mark.parametrize(
    "actual, expected, result",
    [
        (422, 422, True),   # Correct rejection.
        (201, 422, False),  # User created instead of rejected.
        (500, 422, False),  # Server error instead of expected rejection.
    ],
)
def test_check_status_code(actual, expected, result):
    assert check_status_code(actual, expected) is result