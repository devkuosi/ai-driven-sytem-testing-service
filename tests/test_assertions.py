import pytest

from ai_test_service.assertions import check_json_equals, check_status_code, get_json_field


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

def test_get_json_field_reads_empty_list():
    assert get_json_field({"items": []}, "/items") == []


def test_get_json_field_reads_existing_users():
    users = [{"id": "user-1"}]
    assert get_json_field({"items": users}, "/items") == users


def test_get_json_field_rejects_missing_field():
    with pytest.raises(KeyError, match="missing"):
        get_json_field({}, "/items")    

@pytest.mark.parametrize(
    "body, expected, result",
    [
        ({"items": []}, [], True),
        ({"items": [{"id": "user-1"}]}, [], False),
        ({}, [], False),
        ({"items": None}, [], False),
        ({"items": [True]}, [1], False),
    ],
)
def test_check_json_equals(body, expected, result):
    assert check_json_equals(body, "/items", expected) is result        