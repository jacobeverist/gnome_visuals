# GNOME Encoder Interactive Dashboard

An interactive web-based visualization tool for exploring GNOME encoder configurations using Dash and Plotly.

## Features

- **Interactive Parameter Controls**: Real-time adjustment of encoder parameters (n, w, period, offset)
- **Multiple Visualization Types**:
  - Encoder bin visualization with hover details
  - Interactive similarity heatmaps
  - 3D parameter response surfaces
- **Multiple Encoder Types**: Support for PeriodicScalarEncoder, PeriodicCellEncoder, and MultiEncoder
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Immediate visual feedback as parameters change

## Installation

1. Install dependencies from the repo root:
```bash
pip install -e .
```

2. Ensure gnomecode is available:
```bash
# Install gnomecode in editable mode if developing both packages
pip install -e /path/to/gnomecode
```

## Usage

### Quick Start

1. Launch the application:
```bash
cd apps/dash_encoder
python run_app.py
```

2. Open your browser to `http://localhost:8050`

3. Use the parameter controls on the left to adjust encoder settings

4. Explore different tabs for various visualizations

### Command Line Options

```bash
python run_app.py --help
```

Options:
- `--port PORT`: Specify port (default: 8050)
- `--debug`: Enable debug mode

### Using the Interface

#### Parameter Controls
- **Encoder Type**: Choose between Periodic Scalar, Periodic Cell, or Multi Encoder
- **Number of Bins (n)**: Adjust using the slider (4-32)
- **Bin Width (w)**: Control overlap with slider (1-8)
- **Period**: Set periodicity (0.1-2.0)
- **Offset**: Adjust phase offset (-1.0 to 1.0)
- **Input Range**: Set xmin and xmax values

#### Visualization Tabs
1. **Encoder Visualization**: Shows encoding bins and feature heatmap
2. **Similarity Heatmap**: Interactive similarity matrix between input values
3. **3D Analysis**: Parameter response surfaces *(aspirational — not yet implemented)*

#### Preset Configurations
- **2^n Equal Period**: Classic power-of-2 configuration
- **Prime Binsize**: Prime number configurations
- **Random Config**: Randomized parameters for exploration

## Architecture

```
dash_encoder_app/
├── app.py                     # Main Dash application
├── run_app.py                # Launch script
├── components/
│   ├── encoder_controls.py   # Parameter control widgets
│   └── plotly_plots.py       # Interactive plot components
├── utils/
│   └── encoder_factory.py    # Encoder creation utilities
├── assets/
│   └── styles.css           # Custom styling
└── README.md                # This file
```

## Development

### Adding New Encoder Types

1. Add the encoder type to `encoder_factory.py`
2. Update the dropdown options in `encoder_controls.py`
3. Add specific visualization logic in `plotly_plots.py`

### Adding New Visualizations

1. Create new plot functions in `plotly_plots.py`
2. Add new tabs to the main app layout in `app.py`
3. Create corresponding callbacks for real-time updates

### Customizing Styling

Edit `assets/styles.css` for custom styling. The CSS is automatically loaded by Dash.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and gnomecode is available
2. **Port Already in Use**: Use `--port` option to specify a different port
3. **Visualization Errors**: Check browser console for JavaScript errors

### Debug Mode

Run with `--debug` flag to enable:
- Automatic reload on code changes
- Detailed error messages
- Debug toolbar in browser

## Performance Notes

- The application generates visualizations in real-time
- Complex parameter sweeps may take a few seconds
- Consider reducing sample sizes for faster response times

## Aspirational / Future Enhancements

> These features are planned but not yet implemented.

- [ ] Export functionality for plots and configurations
- [ ] Comparison mode for multiple encoder configurations
- [ ] Animation controls for parameter sweeps
- [ ] Advanced analytics dashboard
- [ ] Session save/load functionality

## Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Update this README for new features
4. Test with both real and mock encoders

## License

Same license as the parent gnome_visuals project.