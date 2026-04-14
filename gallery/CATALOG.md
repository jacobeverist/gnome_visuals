# Gallery Image Catalog

Catalog of all rendered images, animations, and diagrams in this repository.
Generated: 2026-04-14. Total assets: ~694 files (684 PNG, 5 MP4, 4 GIF, 1 SVG).

## Naming Convention Key

Most files follow the pattern `NNN_WWWW_EncoderType_VisualizationType.png`:

- `NNN` — number of encoder bins (`n` parameter)
- `WWWW` — bin width or number of samples (`w` or sample count)
- `EncoderType` — encoder class (e.g. `PeriodicCellEncoder`, `FixedWeightEncoder`)
- `VisualizationType` — plot type (e.g. `Features`, `Similarity_Matrix_Projected_to_Real_Space`, `Similarity_Matrix_by_Region_Code`)
- `_samples_` in name — number of sample points used in the visualization sweep

---

## 1. Manim Animations

Animated sequences rendered with Manim. Available as both GIF (looping preview) and MP4 (full quality).

**Directory:** `gallery/animation_examples/`

| File | Format | Description |
|------|--------|-------------|
| `ArrayScene.gif` / `ArrayScene.mp4` | GIF + MP4 | 1D array of gnome bins arranged in a row; shows bin layout and structure |
| `SquareScene.gif` / `SquareScene.mp4` | GIF + MP4 | Single gnome code rendered as a 2D square grid |
| `SquareArrayScene.gif` / `SquareArrayScene.mp4` | GIF + MP4 | Multiple square gnome codes arranged in an array |
| `GnomeShuffle.gif` / `GnomeShuffle.mp4` | GIF + MP4 | Animation of gnome bins being shuffled and reordered |

**Directory:** `gallery/manim_examples/`

| File | Format | Description |
|------|--------|-------------|
| `Gnome_1024_bits.mp4` | MP4 | Large 1024-bit gnome code visualization animation |

---

## 2. Neural Network / Discrete Neuron Visualizations

Manim-rendered stills and animations showing DPNN (Discrete Population Neural Network) structure and related neuron/synapse diagrams.

**Directory:** `gallery/manim_examples/`

| File | Description |
|------|-------------|
| `NaiveNeuronScene_ManimCE_v0.17.2.png` | Simple neuron cell diagram, baseline before discrete operations |
| `DiscreteSynapseScene_ManimCE_v0.17.2.png` | Discrete synapse structure connecting encoder outputs to a neuron |
| `NeuronsOperationsScene_ManimCE_v0.17.2.png` | Multiple neurons showing discrete operations |
| `GnomeInputNeuronScene_ManimCE_v0.17.2.png` | Gnome code encoder feeding into a neuron layer |
| `NetworkScene_ManimCE_v0.17.2.png` | Full multi-layer network structure with gnome encoder input (v0.17.2) |
| `NetworkScene_ManimCE_v0.17.3.png` | Full multi-layer network structure (updated v0.17.3 render) |
| `discrete_neurons_example.png` | Standalone example of discrete neuron visualization |

**Directory:** `experiments/discrete_neurons/dpnn_structure_progress_examples/`

Numbered sequence showing iterative development of the DPNN structure visualization.

| File | Description |
|------|-------------|
| `1_NaiveNeuronScene_ManimCE_v0.17.2.png` | Stage 1: naive/simple neuron representation |
| `2_DiscreteSynapseScene_ManimCE_v0.17.2.png` | Stage 2: discrete synapse added |
| `3_DiscreteOperationsScene_ManimCE_v0.17.2.png` | Stage 3: discrete operations layer added |
| `4_SynapticBusScene_ManimCE_v0.17.2.png` | Stage 4: synaptic bus connecting encoder to neurons |
| `5_WindowedNetworkScene_ManimCE_v0.17.2.png` | Stage 5: full windowed network with all components |

---

## 3. Encoder Feature Plots

Visualizations of encoder bin activations (the "features") — which bins fire for which input values.

### 3.1 Periodic Scalar Encoder

Six rendering style iterations (`v1`–`v6`) of the same encoder configurations, plus a prime-integer configuration. Each version shows the same `w1`/`w2`/`w3` bin-width variants. Later versions introduce compact layout and zero-alignment variants.

**Directory:** `gallery/periodic_scalar_encoder_examples/`

**Parameter variants per version:** `w1` (width=1), `w2` (width=2), `w3` (width=3)

| Subdirectory | Plot Types | Notes |
|---|---|---|
| `v1/` | `Features_PeriodicScalar_wW.png`, `Similarity_Heatmap_PeriodicScalar_wW.png` | Original style; 3 bin-width variants each |
| `v2/` | Same as v1 | Style iteration 2 |
| `v3/` | Same as v1 | Style iteration 3 |
| `v4/` | `Features_Compact_PeriodicScalar_wW.png`, `Features_Compact_zero_PeriodicScalar_wW.png`, `Heatmap_PeriodicScalar_wW.png`, `Heatmap_zero_PeriodicScalar_wW.png` | Compact layout introduced; zero-offset variants added |
| `v5/` | Same as v4 | Style iteration 5 |
| `v6/` | Same as v4 + `zero_aligned_PeriodicScalar_w3.png`, `zero_centered_PeriodicScalar_w3.png` | Adds explicit zero-aligned and zero-centered comparison renders |

**Directory:** `gallery/periodic_scalar_encoder_examples/prime_integers/`

| File | Description |
|------|-------------|
| `028_0001_prime_modulo_encoder_Features.png` | Feature plot for a 28-bin prime-modulo encoder (w=1) |
| `028_0001_prime_modulo_encoder_Similarity_Matrix_Projected_to_Real_Space.png` | Similarity matrix for the 28-bin prime-modulo encoder |

### 3.2 Periodic Cell Encoder

**Directory:** `gallery/periodic_cell_encoder_examples/`

| File | Description |
|------|-------------|
| `020_0001_Features_PeriodicCellEncoder.png` | Feature plot for 20-bin periodic cell encoder (w=1) |
| `020_0001_Similarity_Matrix_Projected_to_Real_Space_PeriodicCellEncoder.png` | Similarity matrix for 20-bin periodic cell encoder projected to real-space axis |

### 3.3 Place Cell Encoders

**Directory:** `gallery/place_cell_encoder_examples/`

| File | Description |
|------|-------------|
| `100_0001_Features_PlaceCellEncoder.png` | Feature plot for 100-bin place cell encoder (w=1) |
| `100_0001_Similarity_Matrix_Projected_to_Real_Space_PlaceCellEncoder.png` | Similarity matrix for 100-bin place cell encoder |
| `place_cell_100.png` | Alternative rendering of 100-bin place cell encoder |

**Directory:** `gallery/randomized_periodic_cells/`

| File | Description |
|------|-------------|
| `010_0167_random_offset_PeriodicCellEncoder_Features.png` | Feature plot for 10-bin periodic cell encoder with 167 randomized offsets |

### 3.4 Fixed Weight Encoder

**Directory:** `gallery/fixed_weight_encoder_examples/`

Pairs of `Features` + `Similarity_Matrix_Projected_to_Real_Space` plots for various `n`/`w` parameter combinations.

**Naming pattern:** `NNN_WWWW_Features_FixedWeightEncoder.png` and `NNN_WWWW_Similarity_Matrix_Projected_to_Real_Space_FixedWeightEncoder.png`

| n (bins) | w (width) | Files |
|---|---|---|
| 8 | 1 | `008_0001_Features_*`, `008_0001_Similarity_*` |
| 8 | 4 | `008_0004_Features_*`, `008_0004_Similarity_*` |
| 12 | 4 | `012_0004_Features_*`, `012_0004_Similarity_*` |
| 16 | 1 | `016_0001_Features_*`, `016_0001_Similarity_*` |
| 16 | 4 | `016_0004_Features_*`, `016_0004_Similarity_*` |
| 36 | 1 | `036_0001_Features_*`, `036_0001_Similarity_*` |
| 36 | 2 | `036_0002_Features_*`, `036_0002_Similarity_*` |
| 40 | 1 | `040_0001_Features_*`, `040_0001_Similarity_*` |
| 40 | 2 | `040_0002_Features_*`, `040_0002_Similarity_*` |

---

## 4. Similarity Matrices

Heatmaps showing pairwise similarity between encoded values.

Two visualization modes:
- **Projected to Real Space** — matrix rows/columns ordered by input value
- **By Region Code** — matrix rows/columns grouped by region/code identity

### 4.1 Plot Examples (Individual/Development)

**Directory:** `gallery/plot_examples/`

Exploratory and development renders including multi-layout experiments and comparison plots for PeriodicCellEncoder and MultiEncoder configurations. Notable files:

| File | Description |
|------|-------------|
| `010_0115_GridSpec_Inset_PeriodicCellEncoder_Similarity_Matrix_Projected_to_Real_Space.png` | GridSpec layout with inset for 10-bin, 115-sample PeriodicCellEncoder |
| `010_0115_Gridspec_xshare_PeriodicCellEncoder_*.png` | Shared x-axis GridSpec layout variant |
| `010_0115_Inset_Constrained_PeriodicCellEncoder_*.png` | Constrained-layout inset variant |
| `010_0115_JointGrid_PeriodicCellEncoder_*.png` | Seaborn JointGrid layout variant |
| `010_0115_gridspec_multi_PeriodicCellEncoder_*.png` | Multi-panel GridSpec layout |
| `010_0115_PeriodicCellEncoder_Similarity_Matrix_*_no_Boundaries.png` | Without region boundary lines |
| `010_0115_PeriodicCellEncoder_Similarity_Matrix_*_with_Boundaries.png` | With region boundary lines |
| `Comparison_010_0115_Similarity_Matrix_*_PeriodicCellEncoder.png` | Side-by-side comparison of projected vs. by-region views |
| `015_0013_Fixed_Weight_MultiEncoder_Similarity_Matrix_*.png` | Fixed weight multi-encoder similarity matrix |
| `015_0013_JointtGrid_tightolayout_Fixed_Weight_MultiEncoder_*.png` | JointGrid tight-layout variant |
| `016_0014_Fixed_Weight_MultiEncoder_Similarity_Matrix_*.png` | 16-bin, 14-sample fixed weight multi-encoder |
| `045_0036_Fixed_Weight_MultiEncoder_Similarity_Matrix_*.png` | 45-bin, 36-sample fixed weight multi-encoder |
| `010_samples_1D_heatmap_PeriodicCellEncoder.png` | 1D heatmap layout showing 10 samples |
| `040_samples_1d_heatmap_PeriodicCellEncoder.png` | 1D heatmap layout showing 40 samples |
| `200_samples_1d_heatmap_PeriodicCellEncoder.png` | 1D heatmap layout showing 200 samples |
| `bin_interval_graph_03_grids_bins_04_06_07.png` | Bin interval graph for 3 grids with bins 4, 6, 7 |
| `02_parallel_encoders_n_w__08_03__16_03.png` | Parallel encoder comparison: (n=8, w=3) vs (n=16, w=3) |
| `error_bits_draww_03_PeriodicCellEncoder.png` | Error/misfire bits visualization for PeriodicCellEncoder |

Also contains a numbered series (`01_`–`17_`) of encoder plots and heatmaps exploring parameter combinations:

**Pattern:** `NN_EncoderType.png` — feature or similarity plot for encoder with `n=NN`

### 4.2 Similarity Matrix Palette Sweep

Four subdirectories containing the same PeriodicCellEncoder similarity matrices rendered with different color palette styles. Each subdirectory holds 40 images (20 `n`/`w` combinations × 2 views: projected + by-region-code).

**Naming pattern:** `NNN_WWWW_PeriodicCellEncoderSimilarity_Matrix_{view}.png`
where `n` ranges from 1–17 and `w` is the corresponding active-bits count.

| Directory | Palette Style | Count |
|---|---|---|
| `samples/diverging_palette_similarity_matrix/` | Diverging colormap (e.g. RdBu); emphasizes above/below median similarity | 80 |
| `samples/sequential_pallette_similarity_matrix/` | Sequential colormap; shows magnitude of similarity | 80 |
| `samples/seq_pallette_similarity_matrix_omit_zero_text/` | Sequential colormap; cell text labels omitted for zero values | 80 |
| `samples/periodic_similarity_matrix_always_lines/` | Sequential colormap with period boundary lines always shown | 40 |

---

## 5. Multi-Encoder and Parameter Sweep Samples

**Directory:** `gallery/samples/` (root level files)

Large systematic sweep exploring encoder configurations across many `n`-bin / sample-count combinations. Three encoder types compared side by side at each setting.

### 5.1 Encoder Configuration Sweeps

**Pattern:** `NNN_EncoderType.png` — feature/bin plot for `n=NNN` bins

Encoder types covered: `PeriodicCellEncoder`, `RandomizedPlaceCellEncoder`, `Fixed_Weight_MultiEncoder`, `TaperingWeightEncoder`/`Tapering_Weight_MultiEncoder`

`n` ranges from 1 to ~40 for cell/place-cell types; larger values for multi-encoder types.

| Notable files | Description |
|---|---|
| `01_PeriodicCellEncoder.png` – `40_PeriodicCellEncoder.png` | Feature plots for n=1..40 periodic cell encoder |
| `01_RandomizedPlaceCellEncoder.png` – `40_RandomizedPlaceCellEncoder.png` | Feature plots for n=1..40 randomized place cell encoder |
| `15_Fixed_Weight_MultiEncoder.png` – `507_Fixed_Weight_MultiEncoder.png` | Fixed weight multi-encoder at various n values |
| `07_PeriodicCellEncoder.png` + `07_Fixed_Weight_MultiEncoder.png` + `07_Tapering_Weight_MultiEncoder.png` | Comparison of encoder types at n=7 |

### 5.2 Sample-Count Sweeps

**Pattern:** `NNN_samples_EncoderType.png` — visualization using `NNN` sample points

Sweeps encoder output across a range of sample counts to show how the encoding pattern looks at different resolutions.

| Sample counts | Encoder types |
|---|---|
| 7, 15, 24, 34, 45, 57, 70, 84, 99, 115, 132, 150, 169, 189, 210, 232, 255, 279, 304, 330, 357, 385, 414, 444, 475, 507, 540, 574, 609, 645, 682, 720, 759, 799, 840, 882 | `Fixed_Weight_MultiEncoder`, `Tapering_Weight_MultiEncoder` |
| 1–17 | `PeriodicCellEncoder` (3 files each: features + 2 similarity views) |

### 5.3 Individual Similarity Matrix Plots (samples root)

Additional one-off similarity matrix plots in `gallery/samples/`:

| File | Description |
|------|-------------|
| `040_0234_PeriodicCellEncoderSimilarity_Matrix_*.png` | 40-bin, 234-sample periodic cell encoder similarity matrices |
| `040_0302_PeriodicCellEncoder_Similarity_Matrix_*.png` | 40-bin, 302-sample periodic cell encoder; multiple rendering variants (1, 2, 3) |
| `08_similarity.png` | Early-stage similarity heatmap for n=8 encoder |
| `35_heatmap_by_region.png` / `35_heatmap_by_value.png` | n=35 encoder; by-region vs. by-value heatmap comparison |
| `40_heatmap_by_region.png` / `40_heatmap_by_value.png` | n=40 encoder; by-region vs. by-value heatmap comparison |

### 5.4 Multi-Encoder Combination Plots

| File | Description |
|------|-------------|
| `03_20_MultiEncoder.png` | 3-period, 20-bin multi-encoder |
| `03_23_MultiEncoder.png` | 3-period, 23-bin multi-encoder |
| `03_27_MultiEncoder.png` | 3-period, 27-bin multi-encoder |
| `03_40_MultiEncoder.png` | 3-period, 40-bin multi-encoder |
| `03_41_MultiEncoder.png` | 3-period, 41-bin multi-encoder |
| `03_41_MultiEncoder_permutated.png` | Same with permuted bin order |
| `03_41_MultiEncoder_save1.png` | Alternative render of 3-period, 41-bin multi-encoder |
| `03_41_MultiEncoder.png` (samples/) | Duplicate in samples directory |

---

## 6. Time Series and State Vector Examples

**Directory:** `gallery/time_series_examples/`

Visualizations of temporal sequences and state vectors, likely from BrainBlocks / Sparsey integration experiments.

| File | Description |
|------|-------------|
| `binary_states2.png` | Binary state vector sequence over time |
| `brainblocks_nominal_eval_1.png` | BrainBlocks nominal evaluation result |
| `sparsey_progressive_persistence.png` | Sparsey progressive persistence visualization |
| `square_wave_time_abnormality_failure_distributed.png` | Square wave input with distributed abnormality detection failure |
| `square_wave_time_abnormality_failure_structured.png` | Square wave input with structured abnormality detection failure |
| `state_vec_1.png` – `state_vec_5.png` | State vector snapshots at 5 time steps |
| `states_vec_learning_distributed_init_1.png` | State vector learning with distributed initialization (step 1) |
| `states_vec_learning_distributed_init_2.png` | State vector learning with distributed initialization (step 2) |

---

## 7. Diagrams and Schematics

Standalone conceptual diagrams not tied to a specific encoder parameter sweep.

**Directory:** `gallery/` (root)

| File | Format | Description |
|------|--------|-------------|
| `Neuron_Cell_Body.png` | PNG | Anatomical-style neuron cell body diagram; used as reference/asset |
| `discrete_cdf_intervals.svg` | SVG | Diagram of discrete CDF (cumulative distribution function) intervals; conceptual illustration of bin interval coverage |

---

## 8. Experiments (Work in Progress)

Rendered outputs from experimental scripts not yet promoted to the main gallery.

### 8.1 Graphviz Diagrams

**Directory:** `experiments/graphviz/`

| File | Description |
|------|-------------|
| `EthaneTest.png` | Ethane molecule test render (graphviz layout experiment) |
| `graph.png` | Basic graph structure diagram |
| `graph2.png` | Graph structure variant 2 |
| `graph3.png` | Graph structure variant 3 |

### 8.2 Plotly/Dash Screenshot

**Directory:** `experiments/plotly_dash/`

| File | Description |
|------|-------------|
| `plotly_realspace_heatmap.png` | Screenshot of a Plotly real-space similarity heatmap rendered in the Dash app |
