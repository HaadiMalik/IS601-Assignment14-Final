# calculation.py = 131-132
import pytest
from app.schemas.calculation import CalculationBase, CalculationType


def test_calculation_type_validation():
    # upper-case type should be accepted (normalized)
    payload = {"type": "ADDITION", "inputs": [1, 2]}
    obj = CalculationBase(**payload)
    assert obj.type == CalculationType.ADDITION


def test_calculation_inputs_not_list():
    with pytest.raises(Exception):
        CalculationBase(**{"type": "addition", "inputs": "not-a-list"})


def test_calculation_division_by_zero_validation():
    with pytest.raises(Exception):
        CalculationBase(**{"type": "division", "inputs": [10, 0]})
