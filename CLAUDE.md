# LLM Assistant Guide for Python Projects

This guide outlines the core rules for development in this repository. Adherence is mandatory.

## 1. Language & Formatting

- **Language**: English only, for all code, comments, and documents.
- **Indentation**: Always use 2 spaces.
- **Identifiers**: Use full English words. No abbreviations (e.g., `index` not `idx`).
- **Strings**: All user-facing strings and log messages must be in English.

## 2. Toolchain

- **Package Management**: Use `uv` (modern python package manager) exclusively. (e.g., `uv pip install requests`).
- **Linting & Formatting**: All code must comply with `ruff` (modern python linter). Format all code before finalizing responses.

## 3. Modern Python Practices

- **Type Hints**: All function signatures must have type hints.
- **f-strings**: Use for all string formatting.
- **`pathlib`**: Use for all filesystem path operations.
- **`dataclasses`**: Use for simple data-holding classes.

## 4. Commenting Philosophy

Comments should prioritize explaining the **"why"** over the "what." However, for particularly complex logic where the implementation is not self-evident, comments should also clarify the "what" and provide examples where helpful.

-   **Explain Rationale (The "Why")**: Focus on the purpose behind non-obvious code, business logic, or complex algorithmic choices. This is the most important role of comments.
-   **Clarify Complexity (The "What")**: For intricate algorithms or dense lines of code whose function isn't immediately obvious, add comments to describe what the code is doing.
-   **Provide Examples**: When it helps clarify, include simple examples within comments to illustrate usage or edge cases.
-   **Syntax**: Use plain English. No numbered lists or complex Markdown.
-   **Strictly Prohibited Content**:
    -   **DO NOT** describe the modification process or edit history. Git history serves this purpose.
    -   **DO NOT** write comments for simple, self-explanatory code.

-   **Examples**:
    -   **Wrong ❌**
        ```python
        # Wrong: Describes edit history. This is the most critical rule to follow.
        # Changed timeout from 5s to 10s
        TIMEOUT = 10

        # Wrong: Useless comment for simple code.
        # Defines a function that adds two numbers
        def add(a, b):
            return a + b
        ```
    -   **Correct ✅**
        ```python
        # Correct: Explains the "why" behind this magic number.
        # The upstream gateway has a hard limit of 10 seconds
        TIMEOUT = 10

        # Correct: Explains complex logic ("what") and provides an example.
        # This regex matches a comma-separated list of values,
        # ignoring commas inside double quotes.
        # e.g., "a,b,\"c,d\",e" -> ["a", "b", "\"c,d\"", "e"]
        COMPLEX_REGEX = r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)'

        # Correct: Code is self-explanatory, no comment needed.
        def add(a, b):
            return a + b
        ```

## 5. Workflow

- **Plan First**: For complex tasks, propose a step-by-step plan before coding.
- **Test Everything**: Cover new functionality with `pytest` tests.
- **Atomic Commits**: Keep commits small and focused. If a solution becomes messy, reset and re-implement cleanly.

## 6. Testing Best Practices

- **Test Files**: Place all tests in the `tests/` directory with names `test_*.py`
- **Test Functions**: Prefix test functions with `test_` (e.g., `def test_svg_parser():`)
- **Test Classes**: Use `TestClassName` for grouping related tests
- **Assertions**: Use Python's built-in `assert` statement, not custom assertion libraries
- **Test Data**: Use standard examples when possible:
  - W3C SVG Test Suite: https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/
  - W3Schools SVG Examples: https://www.w3schools.com/graphics/svg_examples.asp
  - MDN SVG Basic Shapes: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Basic_Shapes
- **Run Tests**: Use `uv run pytest` to run all tests, or `uv run pytest tests/test_specific.py` for specific files
- **Test Dependencies**: pytest is included in the test dependency group, managed by uv
