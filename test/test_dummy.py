import pytest


@pytest.mark.parametrize("test_input, expected", [
    (1, True),
    (0, False),
])
def test_project(test_input, expected):
    assert test_input == expected
