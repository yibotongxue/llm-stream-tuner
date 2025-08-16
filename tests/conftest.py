"""pytest configuration file."""

import os
import tempfile

import pytest


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""

    def _create_config(content, filename="temp_config.yaml"):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        # Clean up after the test
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return _create_config
