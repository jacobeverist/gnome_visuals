# Encoder Basics

Manim visualizations exploring fundamental encoder behavior and properties.

## Manim Animations
- `encoder_collapse.py` - Animation of encoder collapsing/folding
- `encoder_folded.py` - Folded encoder visualization
- `encoder_transform.py` - Transformation visualizations
- `receptive_field.py` - Receptive field animations
- `render_bins.py` - Basic bin rendering and arrangement
- `render_encoder_view.py` - Encoder view animations
- `render_shuffle.py` - Bin shuffling and reordering
- `test_opacity.py` - Testing opacity and layering effects

## Getting Started

Create a 480x480 gif of the shuffle animation with a transparent background
```shell
manim render_shuffle.py -ql -t --format=gif -r 480,480
```

### Options

- `-ql` - Low quality preset
- `-t` - Transparent background
- `--format=gif` - GIF output format
- `-r 480,480` - Resolution

```
  -q, --quality [l|m|h|p|k]      Render quality at the follow resolution
                                 framerates, respectively: 854x480 15FPS,
                                 1280x720 30FPS, 1920x1080 60FPS, 2560x1440
                                 60FPS, 3840x2160 60FPS
```

```
  -p, --preview                  Preview the Scene's animation. OpenGL does a
                                 live preview in a popup window. Cairo opens the
                                 rendered video file in the system default media
                                 player.
```