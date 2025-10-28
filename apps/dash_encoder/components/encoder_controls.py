import dash_bootstrap_components as dbc
from dash import dcc, html

def create_encoder_controls():
    """Create the encoder parameter control panel."""

    controls = [
        # Encoder Type Selection
        dbc.Row([
            dbc.Label("Encoder Type:", width=4),
            dbc.Col([
                dcc.Dropdown(
                    id='encoder-type',
                    options=[
                        {'label': 'Periodic Scalar', 'value': 'periodic_scalar'},
                        {'label': 'Periodic Cell', 'value': 'periodic_cell'},
                        {'label': 'Multi Encoder', 'value': 'multi_encoder'}
                    ],
                    value='periodic_scalar',
                    clearable=False
                )
            ], width=8)
        ], className="mb-3"),

        # Number of bins (n)
        dbc.Row([
            dbc.Label("Number of Bins (n):", width=4),
            dbc.Col([
                dcc.Slider(
                    id='n-bins',
                    min=4,
                    max=32,
                    step=1,
                    value=8,
                    marks={i: str(i) for i in range(4, 33, 4)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=8)
        ], className="mb-3"),

        # Bin width (w)
        dbc.Row([
            dbc.Label("Bin Width (w):", width=4),
            dbc.Col([
                dcc.Slider(
                    id='w-width',
                    min=1,
                    max=8,
                    step=1,
                    value=3,
                    marks={i: str(i) for i in range(1, 9)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=8)
        ], className="mb-3"),

        # Period
        dbc.Row([
            dbc.Label("Period:", width=4),
            dbc.Col([
                dcc.Slider(
                    id='period',
                    min=0.1,
                    max=2.0,
                    step=0.1,
                    value=1.0,
                    marks={i/10: f'{i/10:.1f}' for i in range(2, 21, 4)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=8)
        ], className="mb-3"),

        # Offset
        dbc.Row([
            dbc.Label("Offset:", width=4),
            dbc.Col([
                dcc.Slider(
                    id='offset',
                    min=-1.0,
                    max=1.0,
                    step=0.1,
                    value=0.0,
                    marks={i/10: f'{i/10:.1f}' for i in range(-10, 11, 5)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=8)
        ], className="mb-3"),

        # X range controls
        html.Hr(),
        html.H6("Input Range"),

        dbc.Row([
            dbc.Label("X Min:", width=4),
            dbc.Col([
                dcc.Input(
                    id='xmin',
                    type='number',
                    value=-1.0,
                    step=0.1,
                    className="form-control"
                )
            ], width=8)
        ], className="mb-2"),

        dbc.Row([
            dbc.Label("X Max:", width=4),
            dbc.Col([
                dcc.Input(
                    id='xmax',
                    type='number',
                    value=2.0,
                    step=0.1,
                    className="form-control"
                )
            ], width=8)
        ], className="mb-3"),

        # Preset configurations
        html.Hr(),
        html.H6("Preset Configurations"),

        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("2^n Equal Period", id="preset-2n-period", size="sm", color="secondary"),
                    dbc.Button("Prime Binsize", id="preset-prime", size="sm", color="secondary"),
                    dbc.Button("Random Config", id="preset-random", size="sm", color="secondary")
                ], vertical=True, className="d-grid gap-1")
            ])
        ])
    ]

    return controls