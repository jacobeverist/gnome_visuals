# Samples

Large systematic parameter sweeps across encoder configurations. Contains ~240 root-level images plus four subdirectories of similarity matrix palette variants.

---

## Subdirectories — Similarity Matrix Palette Variants

The same set of PeriodicCellEncoder similarity matrices (n=1–17) rendered four different ways:

| Directory | Palette | Notes |
|---|---|---|
| [diverging_palette_similarity_matrix/](diverging_palette_similarity_matrix/) | Diverging (e.g. RdBu) | Emphasizes above/below-median similarity |
| [sequential_pallette_similarity_matrix/](sequential_pallette_similarity_matrix/) | Sequential | Shows absolute similarity magnitude |
| [seq_pallette_similarity_matrix_omit_zero_text/](seq_pallette_similarity_matrix_omit_zero_text/) | Sequential, no zero labels | Cleaner cells for sparse matrices |
| [periodic_similarity_matrix_always_lines/](periodic_similarity_matrix_always_lines/) | Sequential + forced period lines | Always shows period boundaries |

---

## Root-Level Files

### PeriodicCellEncoder — n=1 to 40

Feature plots showing encoding pattern at each bin count:

<table>
<tr>
  <td align="center"><img src="01_PeriodicCellEncoder.png" width="160"/><br/>n=1</td>
  <td align="center"><img src="03_PeriodicCellEncoder.png" width="160"/><br/>n=3</td>
  <td align="center"><img src="05_PeriodicCellEncoder.png" width="160"/><br/>n=5</td>
  <td align="center"><img src="07_PeriodicCellEncoder.png" width="160"/><br/>n=7</td>
  <td align="center"><img src="10_PeriodicCellEncoder.png" width="160"/><br/>n=10</td>
</tr>
<tr>
  <td align="center"><img src="15_PeriodicCellEncoder.png" width="160"/><br/>n=15</td>
  <td align="center"><img src="20_PeriodicCellEncoder.png" width="160"/><br/>n=20</td>
  <td align="center"><img src="25_PeriodicCellEncoder.png" width="160"/><br/>n=25</td>
  <td align="center"><img src="30_PeriodicCellEncoder.png" width="160"/><br/>n=30</td>
  <td align="center"><img src="40_PeriodicCellEncoder.png" width="160"/><br/>n=40</td>
</tr>
</table>

### RandomizedPlaceCellEncoder — n=1 to 40

<table>
<tr>
  <td align="center"><img src="01_RandomizedPlaceCellEncoder.png" width="160"/><br/>n=1</td>
  <td align="center"><img src="05_RandomizedPlaceCellEncoder.png" width="160"/><br/>n=5</td>
  <td align="center"><img src="10_RandomizedPlaceCellEncoder.png" width="160"/><br/>n=10</td>
  <td align="center"><img src="20_RandomizedPlaceCellEncoder.png" width="160"/><br/>n=20</td>
  <td align="center"><img src="40_RandomizedPlaceCellEncoder.png" width="160"/><br/>n=40</td>
</tr>
</table>

### Fixed Weight MultiEncoder — n=7 to 507

Feature plots at increasing bin counts, showing the structure of fixed-weight multi-encoder outputs:

<table>
<tr>
  <td align="center"><img src="07_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=7</td>
  <td align="center"><img src="15_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=15</td>
  <td align="center"><img src="24_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=24</td>
  <td align="center"><img src="45_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=45</td>
  <td align="center"><img src="99_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=99</td>
</tr>
<tr>
  <td align="center"><img src="115_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=115</td>
  <td align="center"><img src="132_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=132</td>
  <td align="center"><img src="232_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=232</td>
  <td align="center"><img src="304_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=304</td>
  <td align="center"><img src="507_Fixed_Weight_MultiEncoder.png" width="160"/><br/>n=507</td>
</tr>
</table>

### Sample-Count Sweeps

Feature and similarity plots at increasing numbers of sample points:

<table>
<tr>
  <td align="center"><img src="001_samples_PeriodicCellEncoder.png" width="200"/><br/>1 sample</td>
  <td align="center"><img src="005_samples_PeriodicCellEncoder.png" width="200"/><br/>5 samples</td>
  <td align="center"><img src="010_samples_PeriodicCellEncoder.png" width="200"/><br/>10 samples</td>
  <td align="center"><img src="015_samples_PeriodicCellEncoder.png" width="200"/><br/>15 samples</td>
</tr>
<tr>
  <td align="center"><img src="007_samples_Fixed_Weight_MultiEncoder.png" width="200"/><br/>7 samples (Fixed Weight)</td>
  <td align="center"><img src="015_samples_Fixed_Weight_MultiEncoder.png" width="200"/><br/>15 samples</td>
  <td align="center"><img src="045_samples_Fixed_Weight_MultiEncoder.png" width="200"/><br/>45 samples</td>
  <td align="center"><img src="115_samples_Fixed_Weight_MultiEncoder.png" width="200"/><br/>115 samples</td>
</tr>
</table>

### n=40, 302-sample Similarity Matrices (Multiple Render Variants)

<table>
<tr>
  <td align="center"><img src="040_0302_PeriodicCellEncoder_Similarity_Matrix_Projected_to_Real_Space.png" width="260"/><br/>Projected (base)</td>
  <td align="center"><img src="040_0302_PeriodicCellEncoder_Similarity_Matrix_by_Region_Code.png" width="260"/><br/>By region (base)</td>
</tr>
</table>
