# Gnome Codes
Visualizations of Real-Value Representations Using Discrete Population Encoding


## Manim Animations

We use `manim` for animations.  Test scripts can be found in `animation/`.

The simplest can be executed with:

```shell
cd animation
manim test_square.py
```

The most complex would be:

```shell
cd animation
manim test_shuffle.py
```


## Matplotlib Plots
We use `matplotlib` for most of our quantitative plots.  The main plotting script can be executed from the root directory:

```shell
python test_encoders.py
```

Many function calls can be uncommented and executed to plot various types of visualizations.  


## Python Module

Much of the reusable code has been ported to a local python module `encoders`.  It has three constituent files.

- `helpers.py`:  utility functions
- `visuals.py`:  Axes-level visualization code for `matplotlib`
- `encoders.py`:  Implementation of many types of encoders with extra instrumentation for analysis.  Not optimized.
