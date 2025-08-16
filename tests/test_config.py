"""Tests for the config loading functionality."""

import os
import tempfile

import pytest

from llm_stream_tuner.utils.config import load_config, load_yaml_with_imports


class TestConfigLoading:
    """Test cases for config loading functionality."""

    def test_load_simple_config(self):
        """Test loading a simple config file without imports."""
        # Create a temporary simple config file
        test_config_content = """
test_key: test_value
nested:
  nested_key: nested_value
        """

        # Write to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(test_config_content)
            temp_path = f.name

        try:
            # Load the config
            config = load_config(temp_path)

            # Verify the loaded config
            assert config["test_key"] == "test_value"
            assert config["nested"]["nested_key"] == "nested_value"
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_load_config_with_imports(self):
        """Test loading a config file with imports."""
        # Create temporary directories and files for testing
        temp_dir = tempfile.mkdtemp()

        try:
            # Create common config file
            common_config_content = """
# Common configuration sections
_common_model_cfgs: &common_model_cfgs
  inference_backend: api
  model_sdk_type: openai
  api_key_name: TEST_API_KEY

_common_inference_cfgs: &common_inference_cfgs
  max_tokens: 1024
  max_retry: 2
  max_workers: 4

_common_cache_cfgs: &common_cache_cfgs
  cache_type: memory
  cache_dir: /tmp

# Complete configuration for test-model
test-model:
  model_cfgs:
    <<: *common_model_cfgs
    model_name_or_path: test-model
  inference_cfgs:
    <<: *common_inference_cfgs
  cache_cfgs:
    <<: *common_cache_cfgs
            """

            common_config_path = os.path.join(temp_dir, "common_test.yaml")
            with open(common_config_path, "w") as f:
                f.write(common_config_content)

            # Create main config file that imports from common
            main_config_content = f"""
type: llm
llm_cfgs:
  _import_from: {os.path.basename(common_config_path)}
  _import: [test-model]
prompt_builder_cfgs: SimpleTest
            """

            main_config_path = os.path.join(temp_dir, "main_test.yaml")
            with open(main_config_path, "w") as f:
                f.write(main_config_content)

            # Load the config
            config = load_config(main_config_path)

            # Verify the loaded config has the expected structure
            assert config["type"] == "llm"
            assert "llm_cfgs" in config
            assert "prompt_builder_cfgs" in config
            assert config["prompt_builder_cfgs"] == "SimpleTest"

            # Verify the imported configurations
            llm_cfgs = config["llm_cfgs"]
            assert "model_cfgs" in llm_cfgs
            assert "inference_cfgs" in llm_cfgs
            assert "cache_cfgs" in llm_cfgs

            # Verify model-specific config
            model_cfgs = llm_cfgs["model_cfgs"]
            assert model_cfgs["model_name_or_path"] == "test-model"
            assert model_cfgs["inference_backend"] == "api"
            assert model_cfgs["model_sdk_type"] == "openai"
            assert model_cfgs["api_key_name"] == "TEST_API_KEY"

            # Verify inference config
            inference_cfgs = llm_cfgs["inference_cfgs"]
            assert inference_cfgs["max_tokens"] == 1024
            assert inference_cfgs["max_retry"] == 2
            assert inference_cfgs["max_workers"] == 4

            # Verify cache config
            cache_cfgs = llm_cfgs["cache_cfgs"]
            assert cache_cfgs["cache_type"] == "memory"
            assert cache_cfgs["cache_dir"] == "/tmp"

        finally:
            # Clean up
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_load_config_with_multiple_imports(self):
        """Test loading a config file that imports multiple configurations."""
        # Create temporary directories and files for testing
        temp_dir = tempfile.mkdtemp()

        try:
            # Create common config file with multiple models
            common_config_content = """
# Common configuration sections
_common_model_cfgs: &common_model_cfgs
  inference_backend: api
  model_sdk_type: openai
  api_key_name: TEST_API_KEY

_common_inference_cfgs: &common_inference_cfgs
  max_tokens: 1024
  max_retry: 2

# Complete configuration for model-a
model-a:
  model_cfgs:
    <<: *common_model_cfgs
    model_name_or_path: model-a
  inference_cfgs:
    <<: *common_inference_cfgs

# Complete configuration for model-b
model-b:
  model_cfgs:
    <<: *common_model_cfgs
    model_name_or_path: model-b
  inference_cfgs:
    <<: *common_inference_cfgs
            """

            common_config_path = os.path.join(temp_dir, "common_test.yaml")
            with open(common_config_path, "w") as f:
                f.write(common_config_content)

            # Create main config file that imports model-a
            main_config_content = f"""
type: llm
llm_cfgs:
  _import_from: {os.path.basename(common_config_path)}
  _import: [model-a]
prompt_builder_cfgs: TestBuilderA
            """

            main_config_path = os.path.join(temp_dir, "main_test_a.yaml")
            with open(main_config_path, "w") as f:
                f.write(main_config_content)

            # Load the config
            config = load_config(main_config_path)

            # Verify the loaded config has the expected structure
            assert config["type"] == "llm"
            assert config["prompt_builder_cfgs"] == "TestBuilderA"

            # Verify model-specific config
            model_cfgs = config["llm_cfgs"]["model_cfgs"]
            assert model_cfgs["model_name_or_path"] == "model-a"

        finally:
            # Clean up
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_load_yaml_with_imports_directly(self):
        """Test the load_yaml_with_imports function directly."""
        # Create temporary directories and files for testing
        temp_dir = tempfile.mkdtemp()

        try:
            # Create a simple config file
            config_content = """
test_section:
  key1: value1
  key2: value2
nested:
  inner:
    deep_key: deep_value
            """

            config_path = os.path.join(temp_dir, "direct_test.yaml")
            with open(config_path, "w") as f:
                f.write(config_content)

            # Load the config directly
            config = load_yaml_with_imports(config_path)

            # Verify the loaded config
            assert "test_section" in config
            assert config["test_section"]["key1"] == "value1"
            assert config["test_section"]["key2"] == "value2"
            assert config["nested"]["inner"]["deep_key"] == "deep_value"

        finally:
            # Clean up
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_import_directives_removed(self):
        """Test that import directives are removed from loaded configs."""
        # Create temporary directories and files for testing
        temp_dir = tempfile.mkdtemp()

        try:
            # Create common config file
            common_config_content = """
test-model:
  model_cfgs:
    test_key: test_value
            """

            common_config_path = os.path.join(temp_dir, "common_test.yaml")
            with open(common_config_path, "w") as f:
                f.write(common_config_content)

            # Create main config file that imports from common
            main_config_content = f"""
llm_cfgs:
  _import_from: {os.path.basename(common_config_path)}
  _import: [test-model]
  local_key: local_value
            """

            main_config_path = os.path.join(temp_dir, "main_test.yaml")
            with open(main_config_path, "w") as f:
                f.write(main_config_content)

            # Load the config
            config = load_config(main_config_path)

            # Verify that import directives are not present in the final config
            llm_cfgs = config["llm_cfgs"]
            assert "_import_from" not in llm_cfgs
            assert "_import" not in llm_cfgs
            assert "local_key" in llm_cfgs  # Ensure local keys are preserved

        finally:
            # Clean up
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_circular_import_detection(self):
        """Test that circular imports are detected and raise an error."""
        # Create temporary config files with circular imports
        temp_dir = tempfile.mkdtemp()

        try:
            # Create first config file that imports second
            config1_content = f"""
_import_from: config2.yaml
_import: [test_config]
test_key: value1
            """

            # Create second config file that imports first (circular)
            config2_content = f"""
_import_from: config1.yaml
_import: [test_config]
test_key: value2
            """

            # Create test config
            test_config_content = """
test_config:
  shared_key: shared_value
            """

            # Write the config files
            config1_path = os.path.join(temp_dir, "config1.yaml")
            config2_path = os.path.join(temp_dir, "config2.yaml")
            test_config_path = os.path.join(temp_dir, "test_config.yaml")

            with open(config1_path, "w") as f:
                f.write(config1_content)

            with open(config2_path, "w") as f:
                f.write(config2_content)

            with open(test_config_path, "w") as f:
                f.write(test_config_content)

            # Try to load the first config, which should raise a ValueError for circular import
            with pytest.raises(ValueError, match="Circular import detected"):
                load_config(config1_path)

        finally:
            # Clean up
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
