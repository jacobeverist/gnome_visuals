"""
Complete GNOME Encoder Interactive Dashboard
Includes all features: comparison, export, presets, animation, and 3D analysis
"""

import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json

# Import all components
from components.encoder_controls import create_encoder_controls
from components.plotly_plots import create_encoder_visualization, create_heatmap_visualization
from components.comparison_dashboard import (create_comparison_controls, create_encoder_config_panel,
                                           create_comparison_visualization)
from components.preset_configs import (get_preset_configurations, create_preset_dropdown_options,
                                     parse_preset_selection, apply_preset_config)
from components.animation_controls import (create_animation_controls, create_animated_plot,
                                         create_parameter_sweep_heatmap, generate_animation_values)
from utils.encoder_factory import create_encoder_from_params, get_encoder_info
from utils.export_utils import (export_encoder_config, export_plot_html, generate_analysis_report,
                              calculate_encoder_metrics)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GNOME Encoder Complete Interactive Dashboard"

# Complete layout with all features
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🧠 GNOME Encoder Complete Dashboard", className="text-center mb-2"),
            html.P("Interactive visualization, comparison, animation, and analysis tool",
                  className="text-center text-muted mb-4"),
            html.Hr()
        ])
    ]),

    # Mode selector with all features
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("🔧 Single", id="mode-single", color="primary", outline=True, className="me-1"),
                dbc.Button("🔄 Compare", id="mode-comparison", color="secondary", outline=True, className="me-1"),
                dbc.Button("🎬 Animate", id="mode-animation", color="info", outline=True, className="me-1"),
                dbc.Button("📊 3D Analysis", id="mode-3d", color="success", outline=True, className="me-1"),
                dbc.Button("📈 Dashboard", id="mode-dashboard", color="warning", outline=True)
            ], className="mb-3")
        ])
    ], justify="center"),

    # Main content area
    html.Div(id="main-content"),

    # Hidden stores
    dcc.Store(id="app-mode", data="single"),
    dcc.Store(id="animation-state", data={"playing": False, "frame": 0}),
    dcc.Interval(id="animation-timer", interval=500, disabled=True),

    # Downloads
    dcc.Download(id="download-config"),
    dcc.Download(id="download-report"),

], fluid=True, className="px-4")

# Mode switching
@callback(
    [Output('main-content', 'children'),
     Output('app-mode', 'data')] +
    [Output(f'mode-{mode}', 'outline') for mode in ['single', 'comparison', 'animation', '3d', 'dashboard']],
    [Input(f'mode-{mode}', 'n_clicks') for mode in ['single', 'comparison', 'animation', '3d', 'dashboard']],
    prevent_initial_call=False
)
def switch_mode(*clicks):
    ctx_id = ctx.triggered_id

    # Default outline states (True = outlined/inactive, False = filled/active)
    outlines = [True, True, True, True, True]

    if ctx_id == 'mode-comparison':
        return create_comparison_layout(), "comparison", True, False, True, True, True
    elif ctx_id == 'mode-animation':
        return create_animation_layout(), "animation", True, True, False, True, True
    elif ctx_id == 'mode-3d':
        return create_3d_layout(), "3d", True, True, True, False, True
    elif ctx_id == 'mode-dashboard':
        return create_dashboard_layout(), "dashboard", True, True, True, True, False
    else:
        return create_single_layout(), "single", False, True, True, True, True

def create_single_layout():
    """Enhanced single encoder layout with presets."""
    return dbc.Row([
        # Enhanced controls
        dbc.Col([
            # Main controls
            dbc.Card([
                dbc.CardHeader(html.H4("🔧 Encoder Parameters")),
                dbc.CardBody(create_encoder_controls())
            ], className="mb-3"),

            # Preset selector
            dbc.Card([
                dbc.CardHeader(html.H5("🎯 Presets")),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='preset-selector',
                        options=create_preset_dropdown_options(),
                        placeholder="Select a preset configuration...",
                        className="mb-2"
                    ),
                    dbc.Button("Apply Preset", id="apply-preset", color="info", size="sm")
                ])
            ], className="mb-3"),

            # Export controls
            dbc.Card([
                dbc.CardHeader(html.H5("💾 Export")),
                dbc.CardBody([
                    dbc.ButtonGroup([
                        dbc.Button("Config", id="export-config", color="primary", size="sm"),
                        dbc.Button("Plot", id="export-plot", color="success", size="sm"),
                        dbc.Button("Report", id="export-report", color="info", size="sm")
                    ], className="d-grid gap-1")
                ])
            ])
        ], width=3),

        # Enhanced visualizations
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="🎨 Encoder", tab_id="single-encoder", children=[
                    dcc.Loading([dcc.Graph(id="single-plot", style={'height': '600px'})])
                ]),
                dbc.Tab(label="🔥 Heatmap", tab_id="single-heatmap", children=[
                    dcc.Loading([dcc.Graph(id="single-heatmap", style={'height': '600px'})])
                ]),
                dbc.Tab(label="📊 Metrics", tab_id="single-metrics", children=[
                    dcc.Loading([html.Div(id="single-metrics")])
                ]),
                dbc.Tab(label="🌊 3D Surface", tab_id="single-3d", children=[
                    dcc.Loading([dcc.Graph(id="single-3d-plot", style={'height': '600px'})])
                ])
            ], active_tab="single-encoder")
        ], width=9)
    ])

def create_comparison_layout():
    """Enhanced comparison layout."""
    return dbc.Row([
        dbc.Col([
            create_comparison_controls(),
            html.Div(id="comparison-configs")
        ], width=3),
        dbc.Col([
            dcc.Loading([dcc.Graph(id="comparison-plot", style={'height': '700px'})])
        ], width=9)
    ])

def create_animation_layout():
    """Animation layout with controls."""
    return dbc.Row([
        dbc.Col([
            create_animation_controls(),
            html.Div(id="animation-timeline")
        ], width=3),
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="🎬 Animation", tab_id="animation-plot", children=[
                    dcc.Loading([dcc.Graph(id="animated-plot", style={'height': '600px'})])
                ]),
                dbc.Tab(label="🔥 Parameter Sweep", tab_id="sweep-plot", children=[
                    dcc.Loading([dcc.Graph(id="sweep-heatmap", style={'height': '600px'})])
                ])
            ])
        ], width=9)
    ])

def create_3d_layout():
    """3D analysis layout."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🎛️ 3D Controls")),
                dbc.CardBody([
                    # X parameter
                    dbc.Row([
                        dbc.Label("X-Axis:", width=4),
                        dbc.Col([
                            dcc.Dropdown(
                                id='3d-x-param',
                                options=[
                                    {'label': 'Number of Bins', 'value': 'n'},
                                    {'label': 'Width', 'value': 'w'},
                                    {'label': 'Period', 'value': 'period'},
                                    {'label': 'Offset', 'value': 'offset'}
                                ],
                                value='n'
                            )
                        ], width=8)
                    ], className="mb-2"),

                    # Y parameter
                    dbc.Row([
                        dbc.Label("Y-Axis:", width=4),
                        dbc.Col([
                            dcc.Dropdown(
                                id='3d-y-param',
                                options=[
                                    {'label': 'Number of Bins', 'value': 'n'},
                                    {'label': 'Width', 'value': 'w'},
                                    {'label': 'Period', 'value': 'period'},
                                    {'label': 'Offset', 'value': 'offset'}
                                ],
                                value='w'
                            )
                        ], width=8)
                    ], className="mb-2"),

                    # Resolution
                    dbc.Row([
                        dbc.Label("Resolution:", width=4),
                        dbc.Col([
                            dcc.Slider(id='3d-resolution', min=10, max=50, step=5, value=20,
                                     marks={i: str(i) for i in range(10, 51, 10)})
                        ], width=8)
                    ], className="mb-2"),

                    dbc.Button("Generate 3D Surface", id="generate-3d", color="success")
                ])
            ])
        ], width=3),

        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="🌊 Surface", tab_id="3d-surface", children=[
                    dcc.Loading([dcc.Graph(id="3d-surface-plot", style={'height': '700px'})])
                ]),
                dbc.Tab(label="🗺️ Contour", tab_id="3d-contour", children=[
                    dcc.Loading([dcc.Graph(id="3d-contour-plot", style={'height': '700px'})])
                ])
            ])
        ], width=9)
    ])

def create_dashboard_layout():
    """Analytics dashboard layout."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("📊 Analytics Dashboard")),
                dbc.CardBody([
                    html.P("Comprehensive encoder analysis and insights."),
                    dbc.Button("Generate Analysis", id="run-analysis", color="primary"),
                    html.Hr(),
                    html.Div(id="dashboard-content")
                ])
            ])
        ], width=12)
    ])

# Enhanced single encoder callbacks
@callback(
    [Output('single-plot', 'figure'),
     Output('single-heatmap', 'figure'),
     Output('single-metrics', 'children'),
     Output('single-3d-plot', 'figure')],
    [Input('n-bins', 'value'),
     Input('w-width', 'value'),
     Input('period', 'value'),
     Input('offset', 'value'),
     Input('xmin', 'value'),
     Input('xmax', 'value'),
     Input('encoder-type', 'value')]
)
def update_single_visualizations(n_bins, w_width, period, offset, xmin, xmax, encoder_type):
    try:
        params = {
            'n': n_bins, 'w': w_width, 'period': period, 'offset': offset,
            'xmin': xmin, 'xmax': xmax, 'encoder_type': encoder_type
        }
        encoder = create_encoder_from_params(params)

        # Standard plots
        encoder_fig = create_encoder_visualization(encoder, params)
        heatmap_fig = create_heatmap_visualization(encoder, params)

        # Metrics
        metrics = calculate_encoder_metrics(encoder, params)
        metrics_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{metrics.get('encoding_speed', 0):.1f}", className="card-title"),
                        html.P("Encodings/sec", className="card-text")
                    ])
                ], color="primary", outline=True)
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{metrics.get('sparsity', 0):.1%}", className="card-title"),
                        html.P("Sparsity", className="card-text")
                    ])
                ], color="success", outline=True)
            ], width=6)
        ])

        # 3D surface (parameter response)
        surface_fig = create_advanced_3d_surface(params)

        return encoder_fig, heatmap_fig, metrics_cards, surface_fig

    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig, dbc.Alert(f"Error: {e}", color="danger"), empty_fig

def create_advanced_3d_surface(params):
    """Create advanced 3D parameter response surface."""
    try:
        # Create parameter meshes
        n_vals = np.arange(4, 17, 2)
        w_vals = np.arange(1, 9)

        N, W = np.meshgrid(n_vals, w_vals)
        Z = np.zeros_like(N, dtype=float)

        # Calculate response surface
        for i, n in enumerate(n_vals):
            for j, w in enumerate(w_vals):
                try:
                    temp_params = params.copy()
                    temp_params['n'] = int(n)
                    temp_params['w'] = int(w)

                    encoder = create_encoder_from_params(temp_params)
                    encoded = encoder.encode(0.0)  # Test at center
                    Z[j, i] = np.sum(encoded)
                except:
                    Z[j, i] = 0

        fig = go.Figure(data=[go.Surface(
            z=Z, x=N, y=W,
            colorscale='Viridis',
            hovertemplate='n=%{x}<br>w=%{y}<br>Activation=%{z}<extra></extra>'
        )])

        fig.update_layout(
            title="3D Parameter Response Surface",
            scene=dict(
                xaxis_title="Number of Bins (n)",
                yaxis_title="Width (w)",
                zaxis_title="Total Activation"
            ),
            height=600
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"3D Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        return fig

# Preset handler
@callback(
    [Output('n-bins', 'value'),
     Output('w-width', 'value'),
     Output('period', 'value'),
     Output('offset', 'value'),
     Output('encoder-type', 'value')],
    Input('apply-preset', 'n_clicks'),
    State('preset-selector', 'value'),
    prevent_initial_call=True
)
def apply_preset(n_clicks, preset_selection):
    if n_clicks and preset_selection:
        try:
            preset_name, config_index = parse_preset_selection(preset_selection)
            config = apply_preset_config(preset_name, config_index)

            return (
                config.get('n', 8),
                config.get('w', 3),
                config.get('period', 1.0),
                config.get('offset', 0.0),
                config.get('encoder_type', 'periodic_scalar')
            )
        except:
            pass

    # Return current values (no change)
    return 8, 3, 1.0, 0.0, 'periodic_scalar'

if __name__ == '__main__':
    app.run(debug=True, port=8052)