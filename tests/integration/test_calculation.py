import pytest
import uuid

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Exponentiation,
)

# Helper function to create a dummy user_id for testing.
def dummy_user_id():
    return uuid.uuid4()

def test_addition_get_result():
    """
    Test that Addition.get_result returns the correct sum.
    """
    inputs = [10, 5, 3.5]
    addition = Addition(user_id=dummy_user_id(), inputs=inputs)
    result = addition.get_result()
    assert result == sum(inputs), f"Expected {sum(inputs)}, got {result}"

def test_subtraction_get_result():
    """
    Test that Subtraction.get_result returns the correct difference.
    """
    inputs = [20, 5, 3]
    subtraction = Subtraction(user_id=dummy_user_id(), inputs=inputs)
    # Expected: 20 - 5 - 3 = 12
    result = subtraction.get_result()
    assert result == 12, f"Expected 12, got {result}"

def test_multiplication_get_result():
    """
    Test that Multiplication.get_result returns the correct product.
    """
    inputs = [2, 3, 4]
    multiplication = Multiplication(user_id=dummy_user_id(), inputs=inputs)
    result = multiplication.get_result()
    assert result == 24, f"Expected 24, got {result}"

def test_division_get_result():
    """
    Test that Division.get_result returns the correct quotient.
    """
    inputs = [100, 2, 5]
    division = Division(user_id=dummy_user_id(), inputs=inputs)
    # Expected: 100 / 2 / 5 = 10
    result = division.get_result()
    assert result == 10, f"Expected 10, got {result}"

def test_division_by_zero():
    """
    Test that Division.get_result raises ValueError when dividing by zero.
    """
    inputs = [50, 0, 5]
    division = Division(user_id=dummy_user_id(), inputs=inputs)
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        division.get_result()

def test_calculation_factory_addition():
    """
    Test the Calculation.create factory method for addition.
    """
    inputs = [1, 2, 3]
    calc = Calculation.create(
        calculation_type='addition',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    # Check that the returned instance is an Addition.
    assert isinstance(calc, Addition), "Factory did not return an Addition instance."
    assert calc.get_result() == sum(inputs), "Incorrect addition result."

def test_calculation_factory_subtraction():
    """
    Test the Calculation.create factory method for subtraction.
    """
    inputs = [10, 4]
    calc = Calculation.create(
        calculation_type='subtraction',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    # Expected: 10 - 4 = 6
    assert isinstance(calc, Subtraction), "Factory did not return a Subtraction instance."
    assert calc.get_result() == 6, "Incorrect subtraction result."

def test_calculation_factory_multiplication():
    """
    Test the Calculation.create factory method for multiplication.
    """
    inputs = [3, 4, 2]
    calc = Calculation.create(
        calculation_type='multiplication',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    # Expected: 3 * 4 * 2 = 24
    assert isinstance(calc, Multiplication), "Factory did not return a Multiplication instance."
    assert calc.get_result() == 24, "Incorrect multiplication result."

def test_calculation_factory_division():
    """
    Test the Calculation.create factory method for division.
    """
    inputs = [100, 2, 5]
    calc = Calculation.create(
        calculation_type='division',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    # Expected: 100 / 2 / 5 = 10
    assert isinstance(calc, Division), "Factory did not return a Division instance."
    assert calc.get_result() == 10, "Incorrect division result."

def test_calculation_factory_invalid_type():
    """
    Test that Calculation.create raises a ValueError for an unsupported calculation type.
    """
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(
            calculation_type='modulus',  # unsupported type
            user_id=dummy_user_id(),
            inputs=[10, 3],
        )

def test_invalid_inputs_for_addition():
    """
    Test that providing non-list inputs to Addition.get_result raises a ValueError.
    """
    addition = Addition(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        addition.get_result()

def test_invalid_inputs_for_subtraction():
    """
    Test that providing fewer than two numbers to Subtraction.get_result raises a ValueError.
    """
    subtraction = Subtraction(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        subtraction.get_result()

def test_invalid_inputs_for_division():
    """
    Test that providing fewer than two numbers to Division.get_result raises a ValueError.
    """
    division = Division(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        division.get_result()

### exponent tests
def test_exponentiation_get_result():
    """
    Test that Exponentiation.get_result returns the correct power.
    """
    inputs = [2, 8]
    exp = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exp.get_result()
    assert result == 256, f"Expected 256, got {result}"


def test_exponentiation_negative_exponent():
    """
    Test exponentiation with a negative exponent.
    """
    inputs = [2, -3]
    exp = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    assert exp.get_result() == pytest.approx(2 ** -3)


def test_exponentiation_fractional_exponent():
    """
    Test exponentiation with a fractional exponent.
    """
    inputs = [9, 0.5]
    exp = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    assert exp.get_result() == pytest.approx(3.0)


def test_exponentiation_invalid_inputs_count():
    """
    Test that Exponentiation.get_result raises when wrong number of inputs provided.
    """
    exp = Exponentiation(user_id=dummy_user_id(), inputs=[2])
    with pytest.raises(ValueError, match="Exponentiation requires exactly two numbers"):
        exp.get_result()


def test_exponentiation_non_list_inputs_raises():
    """
    Non-list inputs should raise a ValueError.
    """
    exp = Exponentiation(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        exp.get_result()


def test_exponentiation_non_numeric_raises():
    """
    Non-numeric exponent should raise a ValueError during computation.
    """
    exp = Exponentiation(user_id=dummy_user_id(), inputs=[2, 'a'])
    with pytest.raises(ValueError, match="Error computing exponentiation"):
        exp.get_result()


def test_calculation_factory_exponentiation():
    """
    Ensure Calculation.create returns an Exponentiation instance and computes correctly.
    """
    calc = Calculation.create('exponentiation', dummy_user_id(), [3, 3])
    assert isinstance(calc, Exponentiation)
    assert calc.get_result() == 27
###