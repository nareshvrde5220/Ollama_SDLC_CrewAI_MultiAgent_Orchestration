# Phase UUID: f2414dd1-419a-4ae4-8f15-38aa79458b2d

"""
Comprehensive pytest test suite for Simple Calculator application.
"""

import pytest
from unittest.mock import patch, MagicMock
from calculator import Calculator, get_operand, get_operation, perform_calculation, ask_continue, main


class TestCalculator:
    """Test cases for the Calculator class."""

    def test_add(self):
        """Test addition operation."""
        calc = Calculator()
        assert calc.add(5, 3) == 8
        assert calc.add(-1, 1) == 0
        assert calc.add(0, 0) == 0
        assert calc.add(-5, -3) == -8

    def test_subtract(self):
        """Test subtraction operation."""
        calc = Calculator()
        assert calc.subtract(10, 4) == 6
        assert calc.subtract(5, 10) == -5
        assert calc.subtract(0, 0) == 0
        assert calc.subtract(-5, -3) == -2

    def test_multiply(self):
        """Test multiplication operation."""
        calc = Calculator()
        assert calc.multiply(7, 6) == 42
        assert calc.multiply(0, 5) == 0
        assert calc.multiply(-3, 4) == -12
        assert calc.multiply(-2, -3) == 6

    def test_divide_normal(self):
        """Test division operation with normal inputs."""
        calc = Calculator()
        assert calc.divide(20, 5) == 4
        assert calc.divide(10, 2) == 5
        assert calc.divide(-10, 2) == -5
        assert calc.divide(10, -2) == -5

    def test_divide_by_zero_raises_error(self):
        """Test division by zero raises ZeroDivisionError."""
        calc = Calculator()
        with pytest.raises(ZeroDivisionError, match="Division by zero."):
            calc.divide(10, 0)


class TestGetOperand:
    """Test cases for get_operand function."""

    @patch('builtins.input', side_effect=['5'])
    def test_get_operand_valid_input(self, mock_input):
        """Test get_operand with valid numeric input."""
        result = get_operand("Enter operand: ")
        assert result == 5.0

    @patch('builtins.input', side_effect=['abc', '5'])
    def test_get_operand_invalid_then_valid(self, mock_input):
        """Test get_operand with invalid input followed by valid input."""
        result = get_operand("Enter operand: ")
        assert result == 5.0

    @patch('builtins.input', side_effect=['-3.5'])
    def test_get_operand_negative_float(self, mock_input):
        """Test get_operand with negative float input."""
        result = get_operand("Enter operand: ")
        assert result == -3.5

    @patch('builtins.input', side_effect=['0'])
    def test_get_operand_zero(self, mock_input):
        """Test get_operand with zero input."""
        result = get_operand("Enter operand: ")
        assert result == 0.0


class TestGetOperation:
    """Test cases for get_operation function."""

    @patch('builtins.input', side_effect=['add'])
    def test_get_operation_valid_add(self, mock_input):
        """Test get_operation with valid 'add' input."""
        result = get_operation()
        assert result == 'add'

    @patch('builtins.input', side_effect=['SUBTRACT'])
    def test_get_operation_valid_uppercase(self, mock_input):
        """Test get_operation with uppercase input."""
        result = get_operation()
        assert result == 'subtract'

    @patch('builtins.input', side_effect=['multiply', 'divide'])
    def test_get_operation_valid_multiple(self, mock_input):
        """Test get_operation with multiple valid inputs."""
        result1 = get_operation()
        result2 = get_operation()
        assert result1 == 'multiply'
        assert result2 == 'divide'

    @patch('builtins.input', side_effect=['invalid', 'add'])
    def test_get_operation_invalid_then_valid(self, mock_input):
        """Test get_operation with invalid input followed by valid input."""
        result = get_operation()
        assert result == 'add'

    @pytest.mark.parametrize("invalid_input", ['invalid', 'addition', 'div', ''])
    @patch('builtins.input', side_effect=[invalid_input, 'add'])
    def test_get_operation_multiple_invalid(self, mock_input, invalid_input):
        """Test get_operation with multiple invalid inputs."""
        result = get_operation()
        assert result == 'add'


class TestPerformCalculation:
    """Test cases for perform_calculation function."""

    @patch('calculator.get_operand', side_effect=[5, 3])
    @patch('calculator.get_operation', return_value='add')
    @patch('builtins.print')
    def test_perform_calculation_add(self, mock_print, mock_operation, mock_operand):
        """Test perform_calculation with addition."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result == 8.0

    @patch('calculator.get_operand', side_effect=[10, 2])
    @patch('calculator.get_operation', return_value='divide')
    @patch('builtins.print')
    def test_perform_calculation_divide(self, mock_print, mock_operation, mock_operand):
        """Test perform_calculation with division."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result == 5.0

    @patch('calculator.get_operand', side_effect=[10, 0])
    @patch('calculator.get_operation', return_value='divide')
    @patch('builtins.print')
    def test_perform_calculation_divide_by_zero(self, mock_print, mock_operation, mock_operand):
        """Test perform_calculation with division by zero."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result is None

    @patch('calculator.get_operand', side_effect=['abc', 5])
    @patch('calculator.get_operation', return_value='add')
    @patch('builtins.print')
    def test_perform_calculation_invalid_operand(self, mock_print, mock_operation, mock_operand):
        """Test perform_calculation with invalid operand."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result is None


class TestAskContinue:
    """Test cases for ask_continue function."""

    @patch('builtins.input', return_value='y')
    def test_ask_continue_yes(self, mock_input):
        """Test ask_continue with 'y' input."""
        result = ask_continue()
        assert result is True

    @patch('builtins.input', return_value='yes')
    def test_ask_continue_yes_full(self, mock_input):
        """Test ask_continue with 'yes' input."""
        result = ask_continue()
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_ask_continue_no(self, mock_input):
        """Test ask_continue with 'n' input."""
        result = ask_continue()
        assert result is False

    @patch('builtins.input', return_value='no')
    def test_ask_continue_no_full(self, mock_input):
        """Test ask_continue with 'no' input."""
        result = ask_continue()
        assert result is False

    @patch('builtins.input', side_effect=['invalid', 'y'])
    def test_ask_continue_invalid_then_valid(self, mock_input):
        """Test ask_continue with invalid input followed by valid input."""
        result = ask_continue()
        assert result is True

    @pytest.mark.parametrize("invalid_input", ['maybe', '1', ''])
    @patch('builtins.input', side_effect=[invalid_input, 'n'])
    def test_ask_continue_multiple_invalid(self, mock_input, invalid_input):
        """Test ask_continue with multiple invalid inputs."""
        result = ask_continue()
        assert result is False


class TestMainFunction:
    """Test cases for main function."""

    @patch('calculator.perform_calculation', return_value=None)
    @patch('calculator.ask_continue', return_value=False)
    @patch('builtins.print')
    def test_main_exit_immediately(self, mock_print, mock_ask_continue, mock_perform):
        """Test main function exits immediately."""
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)

    @patch('calculator.perform_calculation', return_value=None)
    @patch('calculator.ask_continue', side_effect=[True, False])
    @patch('builtins.print')
    def test_main_multiple_calculations(self, mock_print, mock_ask_continue, mock_perform):
        """Test main function with multiple calculations."""
        with patch('sys.exit') as mock_exit:
            main()
            assert mock_perform.call_count == 2
            mock_exit.assert_called_once_with(0)

    @patch('calculator.perform_calculation', side_effect=[None, ZeroDivisionError("Division by zero")])
    @patch('calculator.ask_continue', side_effect=[True, False])
    @patch('builtins.print')
    def test_main_error_handling(self, mock_print, mock_ask_continue, mock_perform):
        """Test main function error handling."""
        with patch('sys.exit') as mock_exit:
            main()
            assert mock_perform.call_count == 2
            mock_exit.assert_called_once_with(0)

    @patch('calculator.perform_calculation', side_effect=KeyboardInterrupt)
    @patch('calculator.ask_continue', return_value=False)
    @patch('builtins.print')
    def test_main_keyboard_interrupt(self, mock_print, mock_ask_continue, mock_perform):
        """Test main function with keyboard interrupt."""
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)


# Edge cases and boundary value tests
class TestEdgeCases:
    """Test edge cases and boundary values."""

    def test_calculator_with_floats(self):
        """Test calculator with floating point numbers."""
        calc = Calculator()
        assert calc.add(0.1, 0.2) == pytest.approx(0.3, rel=1e-10)
        assert calc.multiply(0.5, 0.5) == 0.25
        assert calc.divide(1.0, 3.0) == pytest.approx(0.3333333333333333, rel=1e-10)

    def test_calculator_with_large_numbers(self):
        """Test calculator with large numbers."""
        calc = Calculator()
        large_num = 1e10
        assert calc.add(large_num, large_num) == 2e10
        assert calc.multiply(large_num, 2) == 2e10

    def test_calculator_with_negative_numbers(self):
        """Test calculator with negative numbers."""
        calc = Calculator()
        assert calc.add(-5, -3) == -8
        assert calc.subtract(-5, -3) == -2
        assert calc.multiply(-5, -3) == 15
        assert calc.divide(-10, -2) == 5

    def test_calculator_with_zero(self):
        """Test calculator with zero."""
        calc = Calculator()
        assert calc.add(0, 5) == 5
        assert calc.subtract(5, 0) == 5
        assert calc.multiply(5, 0) == 0
        with pytest.raises(ZeroDivisionError):
            calc.divide(5, 0)


# Integration tests
class TestIntegration:
    """Integration tests for the complete calculator flow."""

    @patch('calculator.get_operand', side_effect=[5, 3])
    @patch('calculator.get_operation', return_value='add')
    @patch('builtins.print')
    def test_integration_addition(self, mock_print, mock_operation, mock_operand):
        """Integration test for addition operation."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result == 8.0
        mock_print.assert_called_with("Result: 8.0")

    @patch('calculator.get_operand', side_effect=[10, 2])
    @patch('calculator.get_operation', return_value='multiply')
    @patch('builtins.print')
    def test_integration_multiplication(self, mock_print, mock_operation, mock_operand):
        """Integration test for multiplication operation."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result == 20.0
        mock_print.assert_called_with("Result: 20.0")

    @patch('calculator.get_operand', side_effect=[20, 4])
    @patch('calculator.get_operation', return_value='divide')
    @patch('builtins.print')
    def test_integration_division(self, mock_print, mock_operation, mock_operand):
        """Integration test for division operation."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result == 5.0
        mock_print.assert_called_with("Result: 5.0")

    @patch('calculator.get_operand', side_effect=[10, 0])
    @patch('calculator.get_operation', return_value='divide')
    @patch('builtins.print')
    def test_integration_division_by_zero(self, mock_print, mock_operation, mock_operand):
        """Integration test for division by zero error."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result is None
        mock_print.assert_called_with("Error: Division by zero.")


# Error handling tests
class TestErrorHandling:
    """Test error handling scenarios."""

    @patch('calculator.get_operand', side_effect=['invalid', '5'])
    @patch('calculator.get_operation', return_value='add')
    @patch('builtins.print')
    def test_error_handling_invalid_operand(self, mock_print, mock_operation, mock_operand):
        """Test error handling for invalid operand input."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result is None
        # Should have printed error message twice (once for invalid input, once for valid input)
        assert mock_print.call_count >= 2

    @patch('calculator.get_operand', side_effect=[5, 3])
    @patch('calculator.get_operation', side_effect=['invalid', 'add'])
    @patch('builtins.print')
    def test_error_handling_invalid_operation(self, mock_print, mock_operation, mock_operand):
        """Test error handling for invalid operation input."""
        calc = Calculator()
        result = perform_calculation(calc)
        assert result == 8.0  # Should succeed on second attempt
        assert mock_print.call_count >= 2  # Should have printed error message

    def test_calculator_divide_by_zero_error_message(self):
        """Test that divide by zero error has correct message."""
        calc = Calculator()
        with pytest.raises(ZeroDivisionError) as exc_info:
            calc.divide(10, 0)
        assert str(exc_info.value) == "Division by zero."