# Gallery

Visual outputs from the [Gnome Visuals](../README.md) toolkit — static plots, similarity matrices, animated sequences, and neural network diagrams.

---

## Contents

<table>
<tr>
  <td align="center" width="200">
    <a href="animation_examples/">
      <img src="animation_examples/GnomeShuffle.gif" width="180"/><br/>
      <b>Manim Animations</b>
    </a><br/>
    GIF + MP4 animated sequences
  </td>
  <td align="center" width="200">
    <a href="manim_examples/">
      <img src="manim_examples/discrete_neurons_example.png" width="180"/><br/>
      <b>Neural Network Visualizations</b>
    </a><br/>
    DPNN structure stills
  </td>
  <td align="center" width="200">
    <a href="periodic_scalar_encoder_examples/">
      <img src="periodic_scalar_encoder_examples/v6/Features_Compact_PeriodicScalar_w3.png" width="180"/><br/>
      <b>Periodic Scalar Encoder</b>
    </a><br/>
    6 style versions + prime config
  </td>
</tr>
<tr>
  <td align="center" width="200">
    <a href="periodic_cell_encoder_examples/">
      <img src="periodic_cell_encoder_examples/020_0001_Features_PeriodicCellEncoder.png" width="180"/><br/>
      <b>Periodic Cell Encoder</b>
    </a><br/>
    Features + similarity matrix
  </td>
  <td align="center" width="200">
    <a href="place_cell_encoder_examples/">
      <img src="place_cell_encoder_examples/100_0001_Features_PlaceCellEncoder.png" width="180"/><br/>
      <b>Place Cell Encoder</b>
    </a><br/>
    100-bin place cell encoder
  </td>
  <td align="center" width="200">
    <a href="fixed_weight_encoder_examples/">
      <img src="fixed_weight_encoder_examples/040_0002_Features_FixedWeightEncoder.png" width="180"/><br/>
      <b>Fixed Weight Encoder</b>
    </a><br/>
    9 n/w parameter combinations
  </td>
</tr>
<tr>
  <td align="center" width="200">
    <a href="plot_examples/">
      <img src="plot_examples/Comparison_010_0115_Similarity_Matrix_Projected_to_Real_Space_PeriodicCellEncoder.png" width="180"/><br/>
      <b>Plot Examples</b>
    </a><br/>
    Dev renders, layout experiments
  </td>
  <td align="center" width="200">
    <a href="samples/">
      <img src="samples/10_PeriodicCellEncoder.png" width="180"/><br/>
      <b>Parameter Sweep Samples</b>
    </a><br/>
    ~240 images + 4 palette subdirs
  </td>
  <td align="center" width="200">
    <a href="randomized_periodic_cells/">
      <img src="randomized_periodic_cells/010_0167_random_offset_PeriodicCellEncoder_Features.png" width="180"/><br/>
      <b>Randomized Periodic Cells</b>
    </a><br/>
    Random-offset cell encoder
  </td>
</tr>
<tr>
  <td align="center" width="200">
    <a href="time_series_examples/">
      <img src="time_series_examples/binary_states2.png" width="180"/><br/>
      <b>Time Series &amp; State Vectors</b>
    </a><br/>
    BrainBlocks / Sparsey experiments
  </td>
  <td align="center" width="200">
    <img src="discrete_cdf_intervals.svg" width="180"/><br/>
    <b>Diagrams</b><br/>
    CDF intervals, neuron anatomy
  </td>
  <td></td>
</tr>
</table>

---

## Naming Convention

Most files follow the pattern `NNN_WWWW_EncoderType_VisualizationType.png`:

| Token | Meaning |
|---|---|
| `NNN` | Number of encoder bins (`n` parameter) |
| `WWWW` | Bin width or sample count |
| `EncoderType` | Encoder class (e.g. `PeriodicCellEncoder`) |
| `Features` | Encoding bin activation plot |
| `Similarity_Matrix_Projected_to_Real_Space` | Pairwise similarity heatmap, axes = input values |
| `Similarity_Matrix_by_Region_Code` | Pairwise similarity heatmap, axes = region codes |
| `_samples_` in name | Number of sample points used |

---

## All Directories

| Directory | Description | Count |
|---|---|---|
| [animation_examples/](animation_examples/) | Manim animated GIFs and MP4s | 8 |
| [manim_examples/](manim_examples/) | Neural network / encoder stills + MP4 | 8 |
| [periodic_scalar_encoder_examples/](periodic_scalar_encoder_examples/) | PeriodicScalarEncoder across 6 style versions | 41 |
| [periodic_cell_encoder_examples/](periodic_cell_encoder_examples/) | PeriodicCellEncoder feature + similarity | 2 |
| [place_cell_encoder_examples/](place_cell_encoder_examples/) | PlaceCellEncoder feature + similarity | 3 |
| [fixed_weight_encoder_examples/](fixed_weight_encoder_examples/) | FixedWeightEncoder across n/w combos | 18 |
| [plot_examples/](plot_examples/) | Development and exploratory renders | 51 |
| [samples/](samples/) | Systematic parameter sweep images | ~240 + subdirs |
| [randomized_periodic_cells/](randomized_periodic_cells/) | Random-offset periodic cell encoder | 1 |
| [time_series_examples/](time_series_examples/) | Temporal state vector visualizations | 12 |
| `discrete_cdf_intervals.svg` | Discrete CDF interval diagram | — |
| `Neuron_Cell_Body.png` | Neuron cell body reference diagram | — |

---

## Experiments (Work in Progress)

| Directory | Description |
|---|---|
| [experiments/discrete_neurons/dpnn_structure_progress_examples/](../experiments/discrete_neurons/dpnn_structure_progress_examples/) | 5-stage DPNN structure development progression |
| [experiments/graphviz/](../experiments/graphviz/) | Graphviz layout experiments |
| [experiments/plotly_dash/](../experiments/plotly_dash/) | Plotly/Dash app screenshot |
