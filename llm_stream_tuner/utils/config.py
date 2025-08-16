import os
from copy import deepcopy
from typing import Any

import yaml  # type: ignore [import-untyped]

__all__ = [
    "load_config",
    "update_config_with_unparsed_args",
]


def load_yaml_with_imports(
    config_path: str, loaded_files: set[str] | None = None
) -> dict[str, Any]:
    """
    Load a YAML file and process _import_from and _import directives.

    Args:
        config_path (str): Path to the configuration file.
        loaded_files (set): Set of already loaded files to prevent circular imports.

    Returns:
        dict[str, Any]: Loaded configuration with imports processed.
    """
    if loaded_files is None:
        loaded_files = set()

    # Prevent circular imports
    abs_config_path = os.path.abspath(config_path)
    if abs_config_path in loaded_files:
        raise ValueError(f"Circular import detected: {config_path}")
    loaded_files.add(abs_config_path)

    with open(config_path) as file:
        config: dict[str, Any] = yaml.safe_load(file)

    # Get the directory of the current config file
    config_dir = os.path.dirname(os.path.abspath(config_path))

    # Process imports recursively
    config = _process_imports(config, config_dir, loaded_files)

    # Remove import directives
    _remove_import_directives(config)

    loaded_files.remove(abs_config_path)
    return config


def _process_imports(
    config: dict[str, Any], base_dir: str, loaded_files: set[str]
) -> dict[str, Any]:
    """
    Process _import_from and _import directives in the configuration.

    Args:
        config (dict): Configuration dictionary to process.
        base_dir (str): Base directory for resolving relative paths.
        loaded_files (set): Set of already loaded files to prevent circular imports.

    Returns:
        dict: Configuration with imports processed.
    """
    if not isinstance(config, dict):
        return config

    # Check if this dict has import directives
    if "_import_from" in config and "_import" in config:
        import_from = config["_import_from"]
        import_names = config["_import"]

        # Resolve the import file path
        import_file_path = os.path.join(base_dir, import_from)
        # Make sure the path is absolute
        import_file_path = os.path.abspath(import_file_path)

        # Load the import file
        imported_config = load_yaml_with_imports(import_file_path, loaded_files)

        # Merge the imported configurations
        result: dict[str, Any] = {}
        if isinstance(import_names, list):
            for import_name in import_names:
                if import_name in imported_config:
                    _merge_dicts(result, imported_config[import_name])
        elif isinstance(import_names, str) and import_names in imported_config:
            _merge_dicts(result, imported_config[import_names])

        # Merge with any additional keys in the current config
        for key, value in config.items():
            if key not in ["_import_from", "_import"]:
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    _merge_dicts(result[key], value)
                else:
                    result[key] = value

        return result

    # Process nested dictionaries
    for key, value in config.items():
        if isinstance(value, dict):
            config[key] = _process_imports(value, base_dir, loaded_files)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    value[i] = _process_imports(item, base_dir, loaded_files)

    return config


def _remove_import_directives(config: dict[str, Any]) -> None:
    """
    Remove _import_from and _import directives from the configuration.

    Args:
        config (dict): Configuration dictionary to clean.
    """
    if not isinstance(config, dict):
        return

    config.pop("_import_from", None)
    config.pop("_import", None)

    for value in config.values():
        if isinstance(value, dict):
            _remove_import_directives(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _remove_import_directives(item)


def _merge_dicts(target: dict[str, Any], source: dict[str, Any]) -> None:
    """
    Merge source dictionary into target dictionary recursively.

    Args:
        target (dict): Target dictionary to merge into.
        source (dict): Source dictionary to merge from.
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _merge_dicts(target[key], value)
        else:
            target[key] = value


def load_config(config_path: str) -> dict[str, Any]:
    """
    Load the configuration file with import support.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict[str, Any]: Loaded configuration.
    """
    return load_yaml_with_imports(config_path)


def update_dict(
    total_dict: dict[str, Any], item_dict: dict[str, Any]
) -> dict[str, Any]:

    def _is_list_dict(obj: Any) -> bool:
        return isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], dict)

    def _update_dict_from_top(
        total_dict: dict[str, Any], item_dict: dict[str, Any]
    ) -> dict[str, Any]:
        for key in total_dict.keys():
            if key in item_dict:
                if isinstance(item_dict[key], dict) and isinstance(
                    total_dict[key], dict
                ):
                    _update_dict_from_top(total_dict[key], item_dict[key])
                elif isinstance(item_dict[key], list) and _is_list_dict(
                    total_dict[key]
                ):
                    for element in total_dict[key]:
                        _update_dict(element, item_dict[key])
                else:
                    total_dict[key] = item_dict[key]
        return total_dict

    def _update_dict(
        total_dict: dict[str, Any], item_dict: dict[str, Any]
    ) -> dict[str, Any]:

        for key, value in total_dict.items():
            if key in item_dict:
                if isinstance(item_dict[key], dict) and isinstance(
                    total_dict[key], dict
                ):
                    _update_dict(total_dict[key], item_dict[key])
                elif isinstance(item_dict[key], dict) and _is_list_dict(
                    total_dict[key]
                ):
                    for element in total_dict[key]:
                        _update_dict(element, item_dict[key])
                else:
                    total_dict[key] = item_dict[key]
            if isinstance(value, dict):
                _update_dict(value, item_dict)
            elif _is_list_dict(total_dict[key]):
                for element in value:
                    _update_dict(element, item_dict)
        return total_dict

    if "" in item_dict:
        item_dict_from_top = item_dict.pop("")
        if isinstance(item_dict_from_top, dict):
            total_dict = _update_dict_from_top(total_dict, item_dict_from_top)

    return _update_dict(total_dict, item_dict)


def is_convertible_to_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def custom_cfgs_to_dict(key_list: str, value: Any) -> dict[str, Any]:
    """This function is used to convert the custom configurations to dict."""
    if value == "True":
        value = True
    elif value == "False":
        value = False
    elif value == "None" or value == "null":
        value = None
    elif value.isdigit():
        value = int(value)
    elif is_convertible_to_float(value):
        value = float(value)
    elif value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
        value = value.split(",")
        value = list(filter(None, value))
    elif "," in value:
        value = value.split(",")
        value = list(filter(None, value))
    else:
        value = str(value)
    keys_split = key_list.replace("-", "_").split(":")
    return_dict = {keys_split[-1]: value}

    for key in reversed(keys_split[:-1]):
        return_dict = {key.replace("-", "_"): return_dict}
    return return_dict


def update_config_with_unparsed_args(
    unparsed_args: list[str], cfgs: dict[str, Any]
) -> None:
    keys = [k[2:] for k in unparsed_args[::2]]
    values = list(unparsed_args[1::2])
    unparsed_args_dict = dict(zip(keys, values))

    for k, v in unparsed_args_dict.items():
        cfgs = update_dict(cfgs, custom_cfgs_to_dict(k, v))


def deepcopy_config(cfgs: dict[str, Any]) -> dict[str, Any]:

    def _deepcopy_config(obj: object) -> object:
        if isinstance(obj, dict):
            return {k: _deepcopy_config(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_deepcopy_config(e) for e in obj]
        return deepcopy(obj)

    return _deepcopy_config(cfgs)  # type: ignore [return-value]
