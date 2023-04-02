# Gnome Codes
Visualizations of Real-Value Representations Using Discrete Population Encoding


## Manim Animations

We use `manim` for animations.  Test scripts can be found in `manim_visuals/`.

To run, first change into the `manim_visuals` directory.

```shell
cd manim_visuals
```

The simplest script can be run by:

```shell
manim test_square.py
```

The most complex script can be run by:

```shell
manim test_shuffle.py
```


## Matplotlib Plots
We use `matplotlib` for most of our quantitative plots.  The main plotting script can be executed from the root directory:

```shell
python test_encoders.py
```

The resulting plotted images can be found in `out/`.

This test script has many function calls that can be uncommented and run to plot various types of visualizations.  


## Python Module

Much of the reusable code has been ported to a local python module `gnomecodes`.  It has three constituent files.

- `helpers.py`:  utility functions
- `visuals.py`:  Axes-level visualization code for `matplotlib`
- `encoders.py`:  Implementation of many types of encoders with extra instrumentation for analysis.  Not optimized.
