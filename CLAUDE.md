# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains visualization tools for Gnome Codes - a system for scalar encoding using binary population codes. The project provides visualization capabilities across three main technologies:

1. **Manim animations**: For creating animated educational content about encoder behavior
2. **Matplotlib plots**: For quantitative analysis and static visualizations
3. **Dash web apps**: Interactive web-based exploration of encoder configurations

## Key Dependencies

- **gnomecode**: External package (editable install from `/Users/jacobeverist/projects/gnomecode`) containing encoder implementations. This is a required dependency.
- **manim**: Animation engine for creating educational videos
- **matplotlib/seaborn**: Static plotting and analysis
- **dash/plotly**: Interactive web visualizations
- **numpy**: Core numerical operations
- **colorcet**: Color palettes for visualizations

## Repository Structure

The repository is organized by **technology** (for reusable code) and **topic** (for experiments):

```
gnome_visuals/
├── gnomevisual/                    # Core reusable package
│   ├── matplotlib/                 # Matplotlib visualization components
│   │   ├── axesplots.py           # Axes-level plotting primitives
│   │   └── layouts.py             # Figure-level compositions
│   ├── manim/                      # Manim reusable components
│   │   ├── gnome.py               # GnomeCode, Synapse, Cell classes
│   │   └── arrange_bins.py        # Bin arrangement utilities
│   ├── plotly/                     # Plotly/Dash components (future)
│   └── utils.py                    # General utilities
│
├── experiments/                    # Topic-organized experiments
│   ├── encoder_basics/            # Basic encoder behavior
│   │   ├── manim/                 # Manim scripts for this topic
│   │   └── plotly/                # Plotly experiments
│   ├── encoders/                  # Encoder component experiments
│   ├── discrete_neurons/          # Discrete neuron visualizations
│   ├── neural_networks/           # Neural network visualizations
│   ├── hypergrid_transform/       # Hypergrid transform visualizations
│   └── manim/                     # Standalone manim experiments
│
├── apps/                          # Standalone applications
│   └── dash_encoder/              # Interactive encoder dashboard
│
├── publications/                  # Publication-specific projects
│   └── 2025_09_dcc_blog_post/    # YYYY_MM format
│
├── scripts/                       # Utility scripts
│   ├── plot_encoders.py
│   ├── arrange_bins.py
│   ├── stitch_images.py
│   └── resize_images.py
│
├── examples/                      # Gallery and templates
│   └── templates/                 # Copy-paste starter templates
│
└── outputs/                       # Generated content (gitignored)
    ├── figures/
    ├── videos/
    └── exports/
```

## Common Commands

### Development Setup

This project uses modern Python packaging with `pyproject.toml`. All dependencies are specified there.

```bash
# Standard installation - install gnomevisual in editable mode
pip install -e .

# Development installation - includes testing, linting, and profiling tools
pip install -e ".[dev]"

# Install the gnomecode dependency in editable mode for active development
# (Required - adjust path to your gnomecode location)
pip install -e /path/to/gnomecode

# Verify installation
python -c "from gnomevisual.matplotlib import draw_multi_encoder_bins; print('Success!')"
python -c "from gnomevisual.manim import GnomeCode; print('Success!')"
```

**Note**: The `gnomecode` package is a separate dependency. If you're actively developing both packages, install gnomecode in editable mode before installing gnomevisual.

### Running Visualizations

```bash
# Generate matplotlib plots (outputs to outputs/figures/)
python scripts/plot_encoders.py

# Run manim animations - low quality preview (fast, outputs to media/)
manim -pql experiments/encoder_basics/manim/encoder_collapse.py SceneName

# High quality render
manim -pqh experiments/encoder_basics/manim/render_bins.py AnimationScene

# List all scenes in a file
manim --list_scenes experiments/encoder_basics/manim/render_bins.py

# Launch interactive Dash web app
cd apps/dash_encoder
python run_app.py
# Then open http://localhost:8050

# Run with custom port or debug mode
python run_app.py --port 8080 --debug
```

### Starting New Experiments

```bash
# Copy a template to start
cp examples/templates/manim_template.py experiments/encoder_basics/manim/my_experiment.py

# Edit and run (low quality preview)
manim -pql experiments/encoder_basics/manim/my_experiment.py MyScene
```

### Development Tools

Development dependencies are installed with `pip install -e ".[dev]"`.

```bash
# Format code (automatically fixes formatting)
black gnomevisual/

# Sort imports (automatically fixes import order)
isort gnomevisual/

# Check code style (reports issues, doesn't auto-fix)
flake8 gnomevisual/

# Profile code performance
python -m line_profiler_pycharm scripts/plot_encoders.py
```

**Tool Configuration**: All tools are configured in `pyproject.toml`:
- Black: 100 character line length, excludes media/outputs
- isort: Compatible with Black, skips generated directories

## Architecture Notes

### Technology-Based Organization

The `gnomevisual/` package is organized by visualization technology:

- **gnomevisual.matplotlib**: Axes-level primitives (`axesplots.py`) and figure-level layouts (`layouts.py`)
- **gnomevisual.manim**: Reusable Manim objects (GnomeCode, Synapse, etc.) and animation utilities
- **gnomevisual.plotly**: Plotly/Dash components (under development)

This ensures code reuse across experiments.

### Topic-Based Experiments

The `experiments/` directory organizes by **visualization topic**, with subdirectories for each technology:

- Find all encoder folding experiments: `experiments/encoder_basics/`
- Within each topic: `manim/`, `matplotlib/`, `plotly/` subdirectories
- Each topic can have a README.md explaining the research question

This makes it easy to find "all experiments about X" regardless of technology used.

### Import Patterns

**New code should use:**
```python
from gnomevisual.manim import GnomeCode, Synapse
from gnomevisual.matplotlib import draw_multi_encoder_bins, plot_code_heatmap
from gnomecode.encoders import PeriodicScalarEncoder
```

**For backwards compatibility, these also work:**
```python
from gnomevisual import draw_multi_encoder_bins  # matplotlib components at top level
```

### Encoder Visualization Pipeline

1. **Encoders** (from gnomecode package): Core encoding logic including `PeriodicScalarEncoder`, `PeriodicCellEncoder`, `MultiEncoder`, `FixedWeightEncoder`
2. **Axes-level plots** (`gnomevisual.matplotlib.axesplots`): Low-level drawing functions like `draw_bits_by_data()`, `draw_multi_encoder_bins()`, `draw_similarity_heatmap()`
3. **Figure layouts** (`gnomevisual.matplotlib.layouts`): Compose multiple axes into complete figures using functions like `plot_code_heatmap()`, `plot_interval_multi_encoder()`
4. **Animation scenes** (experiments/*/manim/): Manim Scene classes that animate encoder behavior using `gnomevisual.manim` components

### Publication Projects

Publications are self-contained in `publications/YYYY_MM_name/`:
- Scripts import from `gnomevisual` (no code duplication)
- Final outputs stored within the project
- README links to published content
- Chronological naming (YYYY_MM format)

## Output Locations

- `outputs/`: All generated content (gitignored)
  - `outputs/figures/`: Matplotlib plots
  - `outputs/videos/`: Manim videos
  - `outputs/exports/`: Dash/other exports
- `media/`: Manim-generated assets (gitignored)
- Each experiment can also generate local `media/` subdirectories (gitignored)

## Important Patterns

### Manim Scene Structure

Manim scripts define Scene classes. Use the consolidated Manim utilities:

```python
from manim import *
from gnomevisual.manim import GnomeCode, Synapse, Cell

class MyScene(Scene):
    def construct(self):
        gnome = GnomeCode(n=32, w=8, shape="square")
        self.play(Create(gnome))
```

### Matplotlib Integration

When working with matplotlib visualizations:
- Use `draw_*` functions from `gnomevisual.matplotlib.axesplots` for axes-level operations
- Use `plot_*` functions from `gnomevisual.matplotlib.layouts` for complete figures
- The `save_fig()` function handles standardized file naming and output

### Templates

Use the templates in `examples/templates/` as starting points:
- `manim_template.py`: Basic Manim scene structure
- `matplotlib_template.py`: Matplotlib figure layout
- `dash_template.py`: Interactive Dash application

## Development Notes

### Build System

- **Modern Python packaging**: Uses `pyproject.toml` exclusively (no `setup.py` or `requirements.txt`)
- **Editable installs**: Development uses `pip install -e .` for live code changes
- **Dependency management**: All dependencies specified in `[project.dependencies]` section
- **Dev tools**: Testing, linting, and profiling tools in `[project.optional-dependencies.dev]`
- **Tool configuration**: Black, isort, pytest configured in `pyproject.toml`

### Dependencies

The project has three main dependency groups:

1. **Matplotlib ecosystem**: matplotlib, seaborn, colorcet, pillow
2. **Manim ecosystem**: manim, colour, pygments
3. **Dash/Plotly ecosystem**: dash, plotly, dash-bootstrap-components

The external `gnomecode` package provides encoder implementations and must be installed separately.

### Coding Conventions

- Line profiling with `line_profiler_pycharm` for performance analysis
- Debug printing with `icecream` (`ic()`)
- Common encoder parameters: `n` (bins), `w` (width), `period`, `offset`, `xmin`/`xmax`
- Import from technology-specific modules: `from gnomevisual.manim import ...`
- 100 character line length (Black/isort configuration)

### Git Configuration

- Git hooks may be configured - check `.claude/settings.local.json`
- Main branch is not explicitly set in git config
- Use conventional commits for clear history
