"""
Preset configuration handlers for common encoder setups.
Based on the experiments in the original plot_encoders.py
"""

import numpy as np
from typing import Dict, List, Any

def get_preset_configurations() -> Dict[str, Dict[str, Any]]:
    """Get all available preset configurations."""

    presets = {
        "2n_equal_period_w1": {
            "name": "2^n Equal Period (w=1)",
            "description": "Power of 2 bins with equal periods, width=1",
            "configs": get_2n_equal_period_configs(w=1)
        },
        "2n_equal_period_w3": {
            "name": "2^n Equal Period (w=3)",
            "description": "Power of 2 bins with equal periods, width=3",
            "configs": get_2n_equal_period_configs(w=3)
        },
        "2n_equal_binsize": {
            "name": "2^n Equal Bin Size",
            "description": "Power of 2 bins with proportional bin sizes",
            "configs": get_2n_equal_binsize_configs()
        },
        "prime_equal_period": {
            "name": "Prime Equal Period",
            "description": "Prime number bins with equal periods",
            "configs": get_prime_equal_period_configs()
        },
        "prime_equal_binsize": {
            "name": "Prime Equal Bin Size",
            "description": "Prime number bins with proportional bin sizes",
            "configs": get_prime_equal_binsize_configs()
        },
        "multi_scale": {
            "name": "Multi-Scale Encoding",
            "description": "Multiple scales for hierarchical encoding",
            "configs": get_multi_scale_configs()
        },
        "periodic_cell_varied": {
            "name": "Varied Periodic Cells",
            "description": "Different periodic cell configurations",
            "configs": get_periodic_cell_configs()
        },
        "random_exploration": {
            "name": "Random Exploration",
            "description": "Random configurations for parameter exploration",
            "configs": get_random_configs()
        }
    }

    return presets

def get_2n_equal_period_configs(w: int = 3) -> List[Dict[str, Any]]:
    """
    Generate 2^n equal period configurations.
    Based on run_experiment1() in original code.
    """
    configs = []

    for n in [4, 8, 12, 16]:
        config = {
            "encoder_type": "periodic_scalar",
            "n": n,
            "w": w,
            "period": 1.0,  # Equal period
            "offset": -w / (2 * n),  # Zero-centered
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"2^n n={n} w={w}",
            "description": f"Power of 2 encoder with {n} bins, width {w}"
        }
        configs.append(config)

    return configs

def get_2n_equal_binsize_configs(w: int = 3) -> List[Dict[str, Any]]:
    """
    Generate 2^n equal bin size configurations.
    """
    configs = []

    for n in [4, 8, 12, 16]:
        period = n / 16.0  # Proportional period
        config = {
            "encoder_type": "periodic_scalar",
            "n": n,
            "w": w,
            "period": period,
            "offset": -w * period / (2 * n),
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"2^n binsize n={n}",
            "description": f"Equal bin size with {n} bins, period {period:.3f}"
        }
        configs.append(config)

    return configs

def get_prime_equal_period_configs(w: int = 3) -> List[Dict[str, Any]]:
    """
    Generate prime number equal period configurations.
    """
    configs = []

    for n in [5, 7, 11, 13]:
        config = {
            "encoder_type": "periodic_scalar",
            "n": n,
            "w": w,
            "period": 1.0,
            "offset": -w / (2 * n),
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"Prime n={n} w={w}",
            "description": f"Prime encoder with {n} bins, width {w}"
        }
        configs.append(config)

    return configs

def get_prime_equal_binsize_configs(w: int = 3) -> List[Dict[str, Any]]:
    """
    Generate prime number equal bin size configurations.
    """
    configs = []

    for n in [5, 7, 11, 13]:
        period = n / 13.0  # Proportional to largest prime
        config = {
            "encoder_type": "periodic_scalar",
            "n": n,
            "w": w,
            "period": period,
            "offset": -w * period / (2 * n),
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"Prime binsize n={n}",
            "description": f"Prime equal binsize with {n} bins, period {period:.3f}"
        }
        configs.append(config)

    return configs

def get_multi_scale_configs() -> List[Dict[str, Any]]:
    """
    Generate multi-scale encoding configurations.
    """
    configs = []

    scales = [0.5, 1.0, 1.5, 2.0]
    for i, scale in enumerate(scales):
        config = {
            "encoder_type": "periodic_scalar",
            "n": 8,
            "w": 3,
            "period": scale,
            "offset": 0.0,
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"Scale {scale}x",
            "description": f"Multi-scale encoding at {scale}x scale"
        }
        configs.append(config)

    return configs

def get_periodic_cell_configs() -> List[Dict[str, Any]]:
    """
    Generate periodic cell configurations.
    Based on run_experiment2() in original code.
    """
    configs = []

    # Different cell sizes
    l_params = [0.05, 0.10, 0.15]

    for l_param in l_params:
        config = {
            "encoder_type": "periodic_cell",
            "n": 8,
            "period": 1.0,
            "l": l_param,  # Cell length
            "offset": -l_param / 2,
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"Cell l={l_param}",
            "description": f"Periodic cell with length {l_param}"
        }
        configs.append(config)

    # Fractional lengths
    l_fracs = [0.25, 0.5, 0.75]
    for l_frac in l_fracs:
        config = {
            "encoder_type": "periodic_cell",
            "n": 8,
            "period": 1.0,
            "l_frac": l_frac,
            "offset": 0.0,
            "xmin": -1.0,
            "xmax": 2.0,
            "name": f"Cell frac={l_frac}",
            "description": f"Periodic cell with fraction {l_frac}"
        }
        configs.append(config)

    return configs

def get_random_configs(num_configs: int = 6) -> List[Dict[str, Any]]:
    """
    Generate random configurations for exploration.
    """
    configs = []
    np.random.seed(42)  # For reproducible random configs

    encoder_types = ["periodic_scalar", "periodic_cell"]

    for i in range(num_configs):
        encoder_type = np.random.choice(encoder_types)

        if encoder_type == "periodic_scalar":
            config = {
                "encoder_type": encoder_type,
                "n": int(np.random.choice([4, 6, 8, 10, 12, 16])),
                "w": int(np.random.choice([1, 2, 3, 4, 5])),
                "period": np.random.uniform(0.3, 2.0),
                "offset": np.random.uniform(-0.5, 0.5),
                "xmin": -1.0,
                "xmax": 2.0,
                "name": f"Random {i+1}",
                "description": f"Random scalar encoder configuration {i+1}"
            }
        else:
            config = {
                "encoder_type": encoder_type,
                "n": int(np.random.choice([6, 8, 10, 12])),
                "period": np.random.uniform(0.5, 1.5),
                "l_frac": np.random.uniform(0.2, 0.8),
                "offset": np.random.uniform(-0.3, 0.3),
                "xmin": -1.0,
                "xmax": 2.0,
                "name": f"Random Cell {i+1}",
                "description": f"Random cell encoder configuration {i+1}"
            }

        configs.append(config)

    return configs

def get_comparison_presets() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get preset configurations specifically for comparison studies.
    """

    comparison_sets = {
        "width_comparison": [
            {"encoder_type": "periodic_scalar", "n": 8, "w": 1, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Width 1", "description": "Narrow bins"},
            {"encoder_type": "periodic_scalar", "n": 8, "w": 3, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Width 3", "description": "Medium bins"},
            {"encoder_type": "periodic_scalar", "n": 8, "w": 5, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Width 5", "description": "Wide bins"}
        ],

        "resolution_comparison": [
            {"encoder_type": "periodic_scalar", "n": 4, "w": 2, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Low Res", "description": "4 bins"},
            {"encoder_type": "periodic_scalar", "n": 8, "w": 2, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Med Res", "description": "8 bins"},
            {"encoder_type": "periodic_scalar", "n": 16, "w": 2, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "High Res", "description": "16 bins"}
        ],

        "type_comparison": [
            {"encoder_type": "periodic_scalar", "n": 8, "w": 3, "period": 1.0, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Scalar", "description": "Periodic scalar"},
            {"encoder_type": "periodic_cell", "n": 8, "period": 1.0, "l_frac": 0.375, "offset": 0.0,
             "xmin": -1.0, "xmax": 2.0, "name": "Cell", "description": "Periodic cell"}
        ]
    }

    return comparison_sets

def apply_preset_config(preset_name: str, config_index: int = 0) -> Dict[str, Any]:
    """
    Apply a specific preset configuration.

    Args:
        preset_name: Name of the preset
        config_index: Index of the specific configuration within the preset

    Returns:
        Configuration dictionary
    """
    presets = get_preset_configurations()

    if preset_name not in presets:
        raise ValueError(f"Unknown preset: {preset_name}")

    configs = presets[preset_name]["configs"]

    if config_index >= len(configs):
        config_index = 0  # Default to first config

    return configs[config_index]

def get_preset_names() -> List[str]:
    """Get list of all available preset names."""
    return list(get_preset_configurations().keys())

def get_preset_description(preset_name: str) -> str:
    """Get description for a specific preset."""
    presets = get_preset_configurations()
    return presets.get(preset_name, {}).get("description", "No description available")

def create_preset_dropdown_options():
    """Create options for Dash dropdown from available presets."""
    presets = get_preset_configurations()

    options = []
    for preset_key, preset_data in presets.items():
        for i, config in enumerate(preset_data["configs"]):
            options.append({
                "label": f"{preset_data['name']} - {config['name']}",
                "value": f"{preset_key}:{i}"
            })

    return options

def parse_preset_selection(selection: str) -> tuple:
    """
    Parse preset selection string into preset name and config index.

    Args:
        selection: String in format "preset_name:config_index"

    Returns:
        Tuple of (preset_name, config_index)
    """
    if ":" in selection:
        preset_name, config_index = selection.split(":", 1)
        return preset_name, int(config_index)
    else:
        return selection, 0