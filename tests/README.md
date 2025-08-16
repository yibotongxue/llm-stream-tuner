# Tests

This directory contains tests for the llm-stream-tuner project.

## Running Tests

To run the tests, use:

```bash
uv run pytest
```

To run a specific test file:

```bash
uv run pytest tests/test_config.py
```

To run tests with verbose output:

```bash
uv run pytest -v
```

## Test Structure

- `test_config.py` - Tests for the configuration loading functionality
- `conftest.py` - pytest configuration and fixtures

## Configuration Tests

The configuration tests verify that:

1. Simple config files can be loaded correctly
2. Config files with imports work properly
3. Import directives are removed from the final loaded configuration
4. Circular imports are detected and raise appropriate errors
5. All DeepSeek model configurations are loaded correctly
