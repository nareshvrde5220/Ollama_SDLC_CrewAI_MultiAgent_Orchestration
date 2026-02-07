<!-- Phase UUID: 7a1ca7ac-ec1e-433b-af4a-53fc7e1f0def -->

# Simple Calculator

A lightweight, command‑line calculator that supports the four basic arithmetic operations—addition, subtraction, multiplication, and division—on two numeric operands.  
The application validates user input, handles division‑by‑zero, and continues to run until the user chooses to exit.

> **TL;DR**  
> ```bash
> $ python -m simple_calculator
> ```

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Non‑Interactive Mode (CLI arguments)](#non-interactive-mode-cli-arguments)
- [API Reference](#api-reference)
  - [`Calculator`](#calculator)
  - `get_operand`, `get_operation`, `perform_calculation`, `ask_continue`, `main`
- [Code Architecture](#code-architecture)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The calculator is written in **Python 3.8+** and uses only the standard library.  
It follows a clean, modular design:

| Layer | Responsibility |
|-------|----------------|
| **UI** | Prompting the user, printing results, handling user decisions |
| **Validation** | Converting input to `float`, checking for division by zero |
| **Business Logic** | Performing arithmetic operations |
| **Error Handling** | Graceful handling of invalid input, division by zero, and unexpected errors |

The design makes it trivial to add new operations (e.g., exponentiation) by extending the `Calculator` class and updating the operation dispatcher.

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/simple-calculator.git
   cd simple-calculator
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install the package**

   ```bash
   pip install -e .
   ```

   > *The `-e` flag installs the package in editable mode, allowing you to modify the source code without reinstalling.*

4. **Run the calculator**

   ```bash
   python -m simple_calculator
   ```

---

## Usage

### Interactive Mode

Running the module starts an interactive session:

```bash
$ python -m simple_calculator
Simple Calculator
=================
Enter the first operand: 12
Enter the second operand: 4
Select operation (add, subtract, multiply, divide): divide
Result: 3.0
Do you want to perform another calculation? (y/n): n
Thank you for using the calculator. Goodbye!
```

### Non‑Interactive Mode (CLI arguments)

While the original specification focuses on interactive input, you can extend the tool to accept command‑line arguments.  
Add the following snippet to `main()` if you want to support this:

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Simple Calculator")
    parser.add_argument("a", type=float, help="First operand")
    parser.add_argument("b", type=float, help="Second operand")
    parser.add_argument("op", choices=["add", "subtract", "multiply", "divide"],
                        help="Operation")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    calc = Calculator()
    try:
        if args.op == "add":
            result = calc.add(args.a, args.b)
        elif args.op == "subtract":
            result = calc.subtract(args.a, args.b)
        elif args.op == "multiply":
            result = calc.multiply(args.a, args.b)
        else:  # divide
            result = calc.divide(args.a, args.b)
        print(f"Result: {result}")
    except ZeroDivisionError as e:
        print(f"Error: {e}")
```

Now you can run:

```bash
$ python -m simple_calculator 10 5 divide
Result: 2.0
```

---

## API Reference

The library exposes a single public class `Calculator` and a handful of helper functions.  
All functions are documented with type hints and docstrings.

### `Calculator`

```python
class Calculator:
    """A simple calculator that performs basic arithmetic operations."""
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `add(a: float, b: float) -> float` | Adds two numbers. |
| `subtract(a: float, b: float) -> float` | Subtracts `b` from `a`. |
| `multiply(a: float, b: float) -> float` | Multiplies two numbers. |
| `divide(a: float, b: float) -> float` | Divides `a` by `b`. Raises `ZeroDivisionError` if `b == 0`. |

### Helper Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_operand(prompt: str) -> float` | Prompts the user until a valid float is entered. |
| `get_operation() -> str` | Prompts the user to choose an operation. |
| `perform_calculation(calc: Calculator) -> Optional[float]` | Orchestrates a single calculation cycle. |
| `ask_continue() -> bool` | Asks the user whether to perform another calculation. |
| `main() -> None` | Entry point for the CLI. |

---

## Code Architecture

```
simple_calculator/
├── simple_calculator/
│   ├── __init__.py
│   └── calculator.py   # Core logic
├── tests/
│   └── test_calculator.py
├── README.md
├── setup.py
└── pyproject.toml
```

### `calculator.py`

```python
# ──────────────────────────────────────────────────────────────────────
# 1. Imports
# ──────────────────────────────────────────────────────────────────────
import sys
from typing import Optional, Tuple

# ──────────────────────────────────────────────────────────────────────
# 2. Calculator Class
# ──────────────────────────────────────────────────────────────────────
class Calculator:
    """A simple calculator that performs basic arithmetic operations."""
    def __init__(self) -> None: pass

    def add(self, a: float, b: float) -> float: return a + b
    def subtract(self, a: float, b: float) -> float: return a - b
    def multiply(self, a: float, b: float) -> float: return a * b
    def divide(self, a: float, b: float) -> float:
        if b == 0: raise ZeroDivisionError("Division by zero.")
        return a / b

# ──────────────────────────────────────────────────────────────────────
# 3. Input Helpers
# ──────────────────────────────────────────────────────────────────────
def get_operand(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Error: Invalid numeric input.")

def get_operation() -> str:
    ops = ["add", "subtract", "multiply", "divide"]
    while True:
        op = input("Select operation (add, subtract, multiply, divide): ").strip().lower()
        if op in ops: return op
        print("Invalid operation. Please choose from: add, subtract, multiply, divide")

# ──────────────────────────────────────────────────────────────────────
# 4. Calculation Flow
# ──────────────────────────────────────────────────────────────────────
def perform_calculation(calc: Calculator) -> Optional[float]:
    try:
        a = get_operand("Enter the first operand: ")
        b = get_operand("Enter the second operand: ")
        op = get_operation()
        if op == "add": result = calc.add(a, b)
        elif op == "subtract": result = calc.subtract(a, b)
        elif op == "multiply": result = calc.multiply(a, b)
        else: result = calc.divide(a, b)
        print(f"Result: {result}")
        return result
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        return None

def ask_continue() -> bool:
    while True:
        choice = input("Do you want to perform another calculation? (y/n): ").strip().lower()
        if choice in ['y', 'yes']: return True
        if choice in ['n', 'no']: return False
        print("Please enter 'y' for yes or 'n' for no.")

# ──────────────────────────────────────────────────────────────────────
# 5. Main
# ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("Simple Calculator")
    print("=" * 15)
    calc = Calculator()
    while True:
        try:
            perform_calculation(calc)
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
```

### Extending the Calculator

To add a new operation:

1. Add a method to `Calculator` (e.g., `def power(self, a, b): return a ** b`).
2. Update `get_operation()` to include the new keyword.
3. Add a branch in `perform_calculation()` to call the new method.

No other files need modification.

---

## Configuration

The calculator has no external configuration files.  
All behavior is controlled by user input.  
If you want to change the prompt text or supported operations, edit the constants in `calculator.py`.

### Environment Variables (Optional)

You can enable a *debug* mode by setting:

```bash
export SIMPLE_CALC_DEBUG=1
```

Add the following snippet to `main()` to print stack traces when an error occurs:

```python
import os
debug = os.getenv("SIMPLE_CALC_DEBUG") == "1"

# In the exception block:
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    if debug:
        import traceback; traceback.print_exc()
    print("Please try again.")
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **`Error: Invalid numeric input.`** | User typed non‑numeric value (e.g., `abc`). | Re‑enter a valid number. |
| **`Error: Division by zero.`** | Second operand is `0` and operation is `divide`. | Use a non‑zero divisor or choose another operation. |
| **`KeyboardInterrupt` (Ctrl‑C)** | User pressed `Ctrl‑C`. | The program exits gracefully; press `Ctrl‑C` again to force exit. |
| **`ImportError: No module named simple_calculator`** | The package is not installed or the virtual environment is not activated. | Run `pip install -e .` and activate the virtual environment. |
| **`SyntaxError` or `IndentationError`** | Edited the source file incorrectly. | Restore the original file or run `git checkout -- simple_calculator/calculator.py`. |
| **`ZeroDivisionError` not caught** | Division by zero occurs but the exception is not handled. | Ensure `perform_calculation()` catches `ZeroDivisionError`. |

---

## Contributing

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feature/xyz`).  
3. Write tests in `tests/`.  
4. Run `pytest` to ensure all tests pass.  
5. Submit a pull request.

All contributions must follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.

---

## License

MIT © 2026 Simple Calculator Project

---