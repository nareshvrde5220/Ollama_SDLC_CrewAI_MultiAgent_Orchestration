# Phase UUID: 31449389-5682-452d-b491-8a8d0fad712e

"""
Simple Calculator Application

This module implements a command-line calculator that supports basic arithmetic
operations: addition, subtraction, multiplication, and division. It handles
input validation, error cases like division by zero, and allows continuous
calculation until the user chooses to exit.
"""

import sys
from typing import Optional, Tuple


class Calculator:
    """A simple calculator that performs basic arithmetic operations."""

    def __init__(self) -> None:
        """Initialize the calculator."""
        pass

    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.

        Args:
            a: First operand
            b: Second operand

        Returns:
            The sum of a and b
        """
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """
        Subtract second number from first number.

        Args:
            a: First operand
            b: Second operand

        Returns:
            The difference of a and b
        """
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.

        Args:
            a: First operand
            b: Second operand

        Returns:
            The product of a and b
        """
        return a * b

    def divide(self, a: float, b: float) -> float:
        """
        Divide first number by second number.

        Args:
            a: First operand (dividend)
            b: Second operand (divisor)

        Returns:
            The quotient of a and b

        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Division by zero.")
        return a / b


def get_operand(prompt: str) -> float:
    """
    Get a numeric operand from user input.

    Args:
        prompt: The prompt to display to the user

    Returns:
        The numeric value entered by the user

    Raises:
        ValueError: If the input cannot be converted to a float
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Error: Invalid numeric input.")


def get_operation() -> str:
    """
    Get the operation from user input.

    Returns:
        The selected operation as a string
    """
    operations = ["add", "subtract", "multiply", "divide"]
    while True:
        operation = input("Select operation (add, subtract, multiply, divide): ").strip().lower()
        if operation in operations:
            return operation
        print("Invalid operation. Please choose from: add, subtract, multiply, divide")


def perform_calculation(calc: Calculator) -> Optional[float]:
    """
    Perform a single calculation based on user input.

    Args:
        calc: Calculator instance to use for calculations

    Returns:
        The result of the calculation or None if user wants to exit
    """
    try:
        operand1 = get_operand("Enter the first operand: ")
        operand2 = get_operand("Enter the second operand: ")
        operation = get_operation()

        if operation == "add":
            result = calc.add(operand1, operand2)
        elif operation == "subtract":
            result = calc.subtract(operand1, operand2)
        elif operation == "multiply":
            result = calc.multiply(operand1, operand2)
        elif operation == "divide":
            result = calc.divide(operand1, operand2)

        print(f"Result: {result}")
        return result

    except ZeroDivisionError as e:
        print(f"Error: {e}")
        return None


def ask_continue() -> bool:
    """
    Ask user if they want to perform another calculation.

    Returns:
        True if user wants to continue, False otherwise
    """
    while True:
        choice = input("Do you want to perform another calculation? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        print("Please enter 'y' for yes or 'n' for no.")


def main() -> None:
    """
    Main function to run the calculator application.
    """
    print("Simple Calculator")
    print("=" * 15)
    
    calculator = Calculator()
    
    while True:
        try:
            perform_calculation(calculator)
            
            if not ask_continue():
                print("Thank you for using the calculator. Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\nCalculator interrupted by user. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()