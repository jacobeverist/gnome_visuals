# Experiments

This directory contains visualization experiments organized by **research topic**. Each topic explores a specific aspect of Gnome Code encoders.

## Organization

Within each topic directory, experiments are organized by **technology**:
- `manim/` - Animated visualizations using Manim
- `matplotlib/` - Static plots and analysis using Matplotlib
- `plotly/` - Interactive visualizations using Plotly/Dash

## Topics

### encoder_basics/
Fundamental encoder behavior and properties:
- How bins overlap and encode values
- Encoding/decoding process visualization
- Fold/unfold transformations
- Receptive field analysis

### neural_networks/
Neural network visualizations with encoder integration:
- Discrete neuron structures (DPNN)
- Synapse and connection visualizations
- Network architecture diagrams

### hypergrid_transform/
Hypergrid transformation visualizations:
- Geometric transformations
- Parameter space mappings

### similarity_analysis/ *(placeholder — no experiments yet)*
Similarity and distance analysis between encodings:
- Self-similarity matrices
- Distance metrics
- Comparison visualizations

### parameter_sweeps/ *(placeholder — no experiments yet)*
Exploration of parameter spaces:
- Systematic parameter variation
- Response surface analysis
- Multi-dimensional parameter studies

## Getting Started

1. Browse existing experiments in each topic directory
2. Copy a template from `examples/templates/` to start new experiments
3. Import from `gnomevisual.manim`, `gnomevisual.matplotlib`, or `gnomevisual.plotly`
4. Run experiments:
   ```bash
   # Manim
   manim experiments/<topic>/manim/<script>.py

   # Matplotlib
   python experiments/<topic>/matplotlib/<script>.py

   # Plotly
   python experiments/<topic>/plotly/<script>.py
   ```

## Best Practices

- One experiment per file
- Use descriptive filenames (e.g., `encoder_folding_animation.py`)
- Import reusable code from `gnomevisual` package
- Output to `outputs/` directory (not committed to git)
- Add brief comments explaining what the experiment demonstrates
