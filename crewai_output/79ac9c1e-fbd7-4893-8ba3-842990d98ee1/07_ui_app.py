# Phase UUID: 6c9719de-45fb-4a9c-a4dd-711122894259

"""
Streamlit UI for the Simple Calculator

This app provides a modern, responsive interface for performing basic
arithmetic operations on two numeric operands.  It uses Streamlit
components such as columns, tabs, expanders, a sidebar, loading spinners,
and feedback messages to create a clean user experience.
"""

import streamlit as st
from typing import Tuple, Union

# --------------------------------------------------------------------------- #
# Page configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Simple Calculator",
    page_icon="🧮",
    layout="wide",
)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def _calculate(op: str, a: float, b: float) -> Tuple[Union[float, None], str]:
    """
    Perform the requested arithmetic operation.

    Parameters
    ----------
    op : str
        One of 'add', 'subtract', 'multiply', 'divide'.
    a : float
        First operand.
    b : float
        Second operand.

    Returns
    -------
    result : float or None
        The numeric result, or None if an error occurred.
    message : str
        Success or error message to display to the user.
    """
    try:
        if op == "add":
            return a + b, f"Result: {a} + {b} = {a + b}"
        if op == "subtract":
            return a - b, f"Result: {a} - {b} = {a - b}"
        if op == "multiply":
            return a * b, f"Result: {a} × {b} = {a * b}"
        if op == "divide":
            if b == 0:
                raise ZeroDivisionError
            return a / b, f"Result: {a} ÷ {b} = {a / b}"
    except ZeroDivisionError:
        return None, "Error: Division by zero."
    except Exception as exc:
        return None, f"Error: {exc}"
    return None, "Error: Unknown operation."

# --------------------------------------------------------------------------- #
# Sidebar navigation
# --------------------------------------------------------------------------- #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select page", ["Calculator", "About"])

# --------------------------------------------------------------------------- #
# About page
# --------------------------------------------------------------------------- #
if page == "About":
    st.title("Simple Calculator")
    st.markdown(
        """
        This Streamlit application implements a lightweight calculator that
        supports the four basic arithmetic operations: **addition**, **subtraction**,
        **multiplication**, and **division**.  
        It validates input, handles division‑by‑zero errors, and displays
        clear feedback messages.

        **Features**

        - Modern layout with columns, tabs, and expanders
        - Loading spinner while calculations are performed
        - Graceful error handling and user‑friendly messages
        - Responsive design that works on desktop and mobile

        **How to use**

        1. Choose an operation from the tabs in the main area.  
        2. Enter two numeric operands.  
        3. Click **Calculate**.  
        4. View the result or any error message below the button.

        Enjoy!
        """
    )
    st.image(
        "https://images.unsplash.com/photo-1584697964154-1c4b7c0b6b2e",
        caption="Calculator in action",
        use_column_width=True,
    )
    st.stop()

# --------------------------------------------------------------------------- #
# Calculator page
# --------------------------------------------------------------------------- #
st.title("🧮 Simple Calculator")

# Explanation expander
with st.expander("How it works"):
    st.markdown(
        """
        - **Operands**: Enter any real number (integer or floating‑point).  
        - **Operation**: Select one of the four basic operations.  
        - **Result**: The calculation is performed instantly; a loading
          spinner appears briefly to simulate processing time.  
        - **Error handling**:  
          * Division by zero → *Error: Division by zero.*  
          * Invalid input → *Error: Invalid numeric input.*  
        """
    )

# Tabs for each operation
tabs = st.tabs(["Add", "Subtract", "Multiply", "Divide"])

# Mapping tab index to operation name
op_map = {0: "add", 1: "subtract", 2: "multiply", 3: "divide"}

for idx, tab in enumerate(tabs):
    op_name = op_map[idx]
    with tab:
        # Two columns for operands
        col1, col2 = st.columns(2)

        with col1:
            a = st.number_input(
                label="First operand",
                value=0.0,
                key=f"{op_name}_a",
                format="%.6f",
            )
        with col2:
            b = st.number_input(
                label="Second operand",
                value=0.0,
                key=f"{op_name}_b",
                format="%.6f",
            )

        # Form to group inputs and button
        with st.form(key=f"{op_name}_form"):
            calculate_btn = st.form_submit_button(label="Calculate")
            reset_btn = st.form_submit_button(label="Reset")

        if reset_btn:
            # Reset values to defaults
            st.session_state[f"{op_name}_a"] = 0.0
            st.session_state[f"{op_name}_b"] = 0.0
            st.session_state.pop(f"{op_name}_result", None)
            st.session_state.pop(f"{op_name}_message", None)
            st.experimental_rerun()

        if calculate_btn:
            with st.spinner("Calculating..."):
                result, message = _calculate(op_name, a, b)
                st.session_state[f"{op_name}_result"] = result
                st.session_state[f"{op_name}_message"] = message

        # Display result or error
        if f"{op_name}_message" in st.session_state:
            msg = st.session_state[f"{op_name}_message"]
            if msg.startswith("Result"):
                st.success(msg)
            else:
                st.error(msg)

# --------------------------------------------------------------------------- #
# End of app
# --------------------------------------------------------------------------- #