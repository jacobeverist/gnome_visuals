# Gnome Codes
Visualization of Scalar Encoding Using Binary Population Codes


## Manim Animations

We use `manim` for animations.  Test scripts can be found in `manim_visuals/`.

To run, first change into the `manim_visuals` directory.

```shell
cd manim_visuals
```

The simplest script can be run by:

```shell
manim render_square.py
```

The most complex script can be run by:

```shell
manim render_shuffle.py
```


## Matplotlib Plots
We use `matplotlib` for most of our quantitative plots.  The main plotting script can be executed from the root directory:

```shell
python plot_encoders.py
```

The resulting plotted images can be found in `out/`.  This test script creates and modifies an encoder and calls 
several plotting methods in `gnomecode/layouts.py` that create different types of visualizations.

## Python Module

Much of the reusable code has been ported to a local python module `gnomecodes`.  It has three constituent files.

- `utils.py`:  utility functions
- `layouts.py`:  Figure-level layouts of axes, configs, and plots
- `axesplots.py`:  Axes-level visualization code for `matplotlib`
- `encoders.py`:  Implementation of many types of encoders with extra instrumentation for analysis.  Not optimized.

## Examples Gallery

Example Manim animations can be found in [docs/animation_examples/](docs/animation_examples/).

Example Matplotlib images can be found in [docs/plot_examples/](docs/plot_examples/).

