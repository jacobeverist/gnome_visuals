# Encoder Basics

Visualizations exploring fundamental encoder behavior and properties.

## Research Questions

- How do encoder bins overlap and tile the input space?
- What happens during encoding/decoding?
- How do fold/unfold transformations work?
- What are the receptive fields of individual bins?

## Experiments

### Manim Animations (`manim/`)
- `encoder_collapse.py` - Animation of encoder collapsing/folding
- `encoder_folded.py` - Folded encoder visualization
- `encoder_transform.py` - Transformation visualizations
- `receptive_field.py` - Receptive field animations
- `render_bins.py` - Basic bin rendering and arrangement
- `render_encoder_view.py` - Encoder view animations
- `render_shuffle.py` - Bin shuffling and reordering
- `test_opacity.py` - Testing opacity and layering effects

### Plotly/Dash Interactive (`plotly/`)
- `advanced_visualizations.py` - Advanced interactive plots
- `anim_example.py` - Animation examples with Plotly
- `unequal_blocks_plotly.py` - Visualization of unequal bin sizes

## Key Concepts

- **Bin overlap**: Controlled by parameter `w` (width)
- **Periodicity**: Parameter `period` determines wrapping behavior
- **Folding**: Transforms between different encoder representations
- **Receptive fields**: Region of input space that activates each bin
