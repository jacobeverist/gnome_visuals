# Plot Examples

Development and exploratory renders: similarity matrices, feature plots, multi-encoder comparisons, and layout experiments across various encoder configurations.

---

## Similarity Matrix Layout Experiments (n=10, 115 samples)

Multiple layout approaches for the same PeriodicCellEncoder similarity matrix, used to evaluate visualization options.

<table>
<tr>
  <td align="center"><img src="010_0115_GridSpec_Inset_PeriodicCellEncoder_Similarity_Matrix_Projected_to_Real_Space.png" width="260"/><br/><b>GridSpec + inset</b></td>
  <td align="center"><img src="010_samples_1D_heatmap_PeriodicCellEncoder.png" width="260"/><br/><b>1D heatmap (10 samples)</b></td>
  <td align="center"><img src="Comparison_010_0115_Similarity_Matrix_Projected_to_Real_Space_PeriodicCellEncoder.png" width="260"/><br/><b>Projected vs. by-region comparison</b></td>
</tr>
</table>

---

## PeriodicCellEncoder — Individual Similarity Matrices

Selected n/w combinations:

<table>
<tr>
  <td align="center"><img src="001_0008_PeriodicCellEncoderSimilarity_Matrix_Projected_to_Real_Space.png" width="220"/><br/><b>n=1, w=8</b><br/>Projected</td>
  <td align="center"><img src="005_0034_PeriodicCellEncoderSimilarity_Matrix_Projected_to_Real_Space.png" width="220"/><br/><b>n=5, w=34</b><br/>Projected</td>
  <td align="center"><img src="007_0051_PeriodicCellEncoderSimilarity_Matrix_Projected_to_Real_Space.png" width="220"/><br/><b>n=7, w=51</b><br/>Projected</td>
  <td align="center"><img src="009_0073_PeriodicCellEncoderSimilarity_Matrix_Projected_to_Real_Space.png" width="220"/><br/><b>n=9, w=73</b><br/>Projected</td>
</tr>
<tr>
  <td align="center"><img src="001_0008_PeriodicCellEncoderSimilarity_Matrix_by_Region_Code.png" width="220"/><br/><b>n=1, w=8</b><br/>By region</td>
  <td align="center"><img src="005_0034_PeriodicCellEncoderSimilarity_Matrix_by_Region_Code.png" width="220"/><br/><b>n=5, w=34</b><br/>By region</td>
  <td align="center"><img src="007_0051_PeriodicCellEncoderSimilarity_Matrix_by_Region_Code.png" width="220"/><br/><b>n=7, w=51</b><br/>By region</td>
  <td align="center"><img src="009_0073_PeriodicCellEncoderSimilarity_Matrix_by_Region_Code.png" width="220"/><br/><b>n=9, w=73</b><br/>By region</td>
</tr>
</table>

Large encoder (n=40):

<table>
<tr>
  <td align="center"><img src="040_0234_PeriodicCellEncoderSimilarity_Matrix_Projected_to_Real_Space.png" width="300"/><br/><b>n=40, 234 samples</b> — Projected</td>
  <td align="center"><img src="040_0234_PeriodicCellEncoderSimilarity_Matrix_by_Region_Code.png" width="300"/><br/><b>n=40, 234 samples</b> — By region</td>
</tr>
</table>

---

## Multi-Encoder Combinations

3-period multi-encoders at various total bin counts:

<table>
<tr>
  <td align="center"><img src="03_20_MultiEncoder.png" width="220"/><br/><b>3-period, n=20</b></td>
  <td align="center"><img src="03_23_MultiEncoder.png" width="220"/><br/><b>3-period, n=23</b></td>
  <td align="center"><img src="03_27_MultiEncoder.png" width="220"/><br/><b>3-period, n=27</b></td>
  <td align="center"><img src="03_40_MultiEncoder.png" width="220"/><br/><b>3-period, n=40</b></td>
</tr>
</table>

| Original | Permuted |
|---|---|
| ![](03_41_MultiEncoder_save1.png) | ![](03_41_MultiEncoder_permutated.png) |

---

## Fixed Weight MultiEncoder — Similarity Matrices

<table>
<tr>
  <td align="center"><img src="015_0013_Fixed_Weight_MultiEncoder_Similarity_Matrix_Projected_to_Real_Space.png" width="280"/><br/><b>n=15, 13 samples</b></td>
  <td align="center"><img src="040_0302_PeriodicCellEncoder_Similarity_Matrix_Projected_to_Real_Space.png" width="280"/><br/><b>n=40, 302 samples</b></td>
</tr>
</table>

---

## Encoder Comparisons

<table>
<tr>
  <td align="center"><img src="02_parallel_encoders_n_w__08_03__16_03.png" width="300"/><br/><b>Parallel encoders</b><br/>(n=8,w=3) vs (n=16,w=3)</td>
  <td align="center"><img src="bin_interval_graph_03_grids_bins_04_06_07.png" width="300"/><br/><b>Bin interval graph</b><br/>3 grids, bins 4/6/7</td>
</tr>
<tr>
  <td align="center"><img src="35_heatmap_by_region.png" width="300"/><br/><b>n=35 — by region</b></td>
  <td align="center"><img src="35_heatmap_by_value.png" width="300"/><br/><b>n=35 — by value</b></td>
</tr>
</table>

---

## Feature / Bin Plots by n

<table>
<tr>
  <td align="center"><img src="04_PeriodicCellEncoder.png" width="200"/><br/>n=4</td>
  <td align="center"><img src="10_PeriodicCellEncoder.png" width="200"/><br/>n=10</td>
  <td align="center"><img src="20_PeriodicCellEncoder.png" width="200"/><br/>n=20</td>
  <td align="center"><img src="40_PeriodicCellEncoder.png" width="200"/><br/>n=40</td>
</tr>
<tr>
  <td align="center"><img src="10_RandomizedPlaceCellEncoder.png" width="200"/><br/>n=10 RandomizedPlace</td>
  <td align="center"><img src="40_RandomizedPlaceCellEncoder.png" width="200"/><br/>n=40 RandomizedPlace</td>
  <td align="center"><img src="20_FixedWeightEncoder.png" width="200"/><br/>n=20 FixedWeight</td>
  <td align="center"><img src="20_TaperingWeightEncoder.png" width="200"/><br/>n=20 TaperingWeight</td>
</tr>
</table>

---

## Sample-Count Sweeps

<table>
<tr>
  <td align="center"><img src="016_samples_PeriodicCellEncoder.png" width="260"/><br/>16 samples</td>
  <td align="center"><img src="040_samples_1d_heatmap_PeriodicCellEncoder.png" width="260"/><br/>40 samples — 1D heatmap</td>
  <td align="center"><img src="200_samples_1d_heatmap_PeriodicCellEncoder.png" width="260"/><br/>200 samples — 1D heatmap</td>
</tr>
</table>
