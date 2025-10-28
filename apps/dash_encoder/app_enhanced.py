import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json

from components.encoder_controls import create_encoder_controls
from components.plotly_plots import create_encoder_visualization, create_heatmap_visualization
from components.comparison_dashboard import (create_comparison_controls, create_encoder_config_panel,
                                           create_comparison_visualization)
from utils.encoder_factory import create_encoder_from_params, get_encoder_info
from utils.export_utils import (export_encoder_config, export_plot_html, export_plot_image,
                              generate_analysis_report, calculate_encoder_metrics)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GNOME Encoder Interactive Visualizer - Enhanced"

# Enhanced layout with comparison and export features
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("GNOME Encoder Interactive Visualizer", className="text-center mb-2"),
            html.P("Enhanced with comparison and export capabilities", className="text-center text-muted mb-4"),
            html.Hr()
        ])
    ]),

    # Mode selector
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Single Encoder", id="mode-single", color="primary", outline=True),
                dbc.Button("Comparison", id="mode-comparison", color="secondary", outline=True),
                dbc.Button("Analysis", id="mode-analysis", color="info", outline=True)
            ], className="mb-3")
        ])
    ], justify="center"),

    # Main content area (dynamically populated based on mode)
    html.Div(id="main-content"),

    # Hidden divs for storing state
    dcc.Store(id="app-mode", data="single"),
    dcc.Store(id="encoder-configs", data={}),
    dcc.Store(id="export-status", data={}),

    # Download components
    dcc.Download(id="download-config"),
    dcc.Download(id="download-plot"),
    dcc.Download(id="download-report")

], fluid=True)

# Mode switching callback
@callback(
    [Output('main-content', 'children'),
     Output('app-mode', 'data'),
     Output('mode-single', 'outline'),
     Output('mode-comparison', 'outline'),
     Output('mode-analysis', 'outline')],
    [Input('mode-single', 'n_clicks'),
     Input('mode-comparison', 'n_clicks'),
     Input('mode-analysis', 'n_clicks')],
    prevent_initial_call=False
)
def switch_mode(single_clicks, comparison_clicks, analysis_clicks):
    if ctx.triggered_id == 'mode-comparison':
        return create_comparison_layout(), "comparison", True, False, True
    elif ctx.triggered_id == 'mode-analysis':
        return create_analysis_layout(), "analysis", True, True, False
    else:
        return create_single_encoder_layout(), "single", False, True, True

def create_single_encoder_layout():
    """Create layout for single encoder mode."""
    return dbc.Row([
        # Controls
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Encoder Parameters")),
                dbc.CardBody([
                    create_encoder_controls()
                ])
            ], className="mb-4"),

            # Export controls
            dbc.Card([
                dbc.CardHeader(html.H5("Export Options")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Save Config", id="save-single-config", color="primary", size="sm", className="me-2"),
                            dbc.Button("Export Plot", id="export-single-plot", color="success", size="sm")
                        ])
                    ])
                ])
            ])
        ], width=3),

        # Visualizations
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(
                    label="Encoder Visualization",
                    tab_id="encoder-viz",
                    children=[
                        dcc.Loading([
                            dcc.Graph(id="single-encoder-plot", style={'height': '600px'})
                        ])
                    ]
                ),
                dbc.Tab(
                    label="Similarity Heatmap",
                    tab_id="heatmap-viz",
                    children=[
                        dcc.Loading([
                            dcc.Graph(id="single-heatmap-plot", style={'height': '600px'})
                        ])
                    ]
                ),
                dbc.Tab(
                    label="Performance Metrics",
                    tab_id="metrics-viz",
                    children=[
                        dcc.Loading([
                            html.Div(id="single-metrics-display")
                        ])
                    ]
                )
            ], id="single-tabs", active_tab="encoder-viz")
        ], width=9)
    ])

def create_comparison_layout():
    """Create layout for comparison mode."""
    return dbc.Row([
        # Comparison controls
        dbc.Col([
            create_comparison_controls(),

            # Individual encoder configs
            html.Div(id="encoder-config-panels")

        ], width=3),

        # Comparison visualizations
        dbc.Col([
            dcc.Loading([
                dcc.Graph(id="comparison-plot", style={'height': '700px'})
            ])
        ], width=9)
    ])

def create_analysis_layout():
    """Create layout for analysis mode."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Analysis Dashboard")),
                dbc.CardBody([
                    html.P("Comprehensive encoder analysis and reporting tools."),
                    dbc.Button("Generate Full Report", id="generate-full-report", color="info", className="mb-3"),
                    html.Div(id="analysis-summary")
                ])
            ])
        ], width=12)
    ])

# Single encoder mode callbacks
@callback(
    [Output('single-encoder-plot', 'figure'),
     Output('single-heatmap-plot', 'figure'),
     Output('single-metrics-display', 'children')],
    [Input('n-bins', 'value'),
     Input('w-width', 'value'),
     Input('period', 'value'),
     Input('offset', 'value'),
     Input('xmin', 'value'),
     Input('xmax', 'value'),
     Input('encoder-type', 'value')]
)
def update_single_encoder_visualizations(n_bins, w_width, period, offset, xmin, xmax, encoder_type):
    try:
        # Create encoder with current parameters
        encoder_params = {
            'n': n_bins,
            'w': w_width,
            'period': period,
            'offset': offset,
            'xmin': xmin,
            'xmax': xmax,
            'encoder_type': encoder_type
        }

        encoder = create_encoder_from_params(encoder_params)

        # Generate visualizations
        encoder_fig = create_encoder_visualization(encoder, encoder_params)
        heatmap_fig = create_heatmap_visualization(encoder, encoder_params)

        # Calculate metrics
        metrics = calculate_encoder_metrics(encoder, encoder_params)

        # Create metrics display
        metrics_display = dbc.Card([
            dbc.CardHeader(html.H5("Performance Metrics")),
            dbc.CardBody([
                html.P(f"Encoding Speed: {metrics.get('encoding_speed', 'N/A'):.2f} enc/sec"),
                html.P(f"Sparsity: {metrics.get('sparsity', 0):.2%}"),
                html.P(f"Memory Usage: {metrics.get('memory_usage', 0):.3f} MB"),
                html.P(f"Mean Overlap: {metrics.get('mean_overlap', 0):.4f}"),
                html.P(f"Overlap Std: {metrics.get('overlap_std', 0):.4f}")
            ])
        ])

        return encoder_fig, heatmap_fig, metrics_display

    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper"
        )
        error_display = dbc.Alert(f"Error calculating metrics: {str(e)}", color="danger")
        return empty_fig, empty_fig, error_display

# Comparison mode callbacks
@callback(
    Output('encoder-config-panels', 'children'),
    Input('num-encoders', 'value')
)
def update_encoder_panels(num_encoders):
    panels = []
    encoder_ids = ['a', 'b', 'c', 'd'][:num_encoders]

    for encoder_id in encoder_ids:
        panels.append(create_encoder_config_panel(encoder_id))

    return panels

@callback(
    Output('comparison-plot', 'figure'),
    [Input('comparison-mode', 'value'),
     Input('num-encoders', 'value')] +
    [Input(f'encoder-type-{encoder_id}', 'value') for encoder_id in ['a', 'b', 'c', 'd']] +
    [Input(f'n-bins-{encoder_id}', 'value') for encoder_id in ['a', 'b', 'c', 'd']] +
    [Input(f'w-width-{encoder_id}', 'value') for encoder_id in ['a', 'b', 'c', 'd']] +
    [Input(f'period-{encoder_id}', 'value') for encoder_id in ['a', 'b', 'c', 'd']]
)
def update_comparison_plot(comparison_mode, num_encoders, *args):
    try:
        # Extract parameters for each encoder
        encoder_ids = ['a', 'b', 'c', 'd'][:num_encoders]
        encoders = []
        params_list = []

        arg_idx = 0
        for i in range(num_encoders):
            encoder_type = args[arg_idx + i] if arg_idx + i < len(args) else 'periodic_scalar'

        arg_idx = 4  # Skip encoder types
        for i in range(num_encoders):
            n_bins = args[arg_idx + i] if arg_idx + i < len(args) else 8

        arg_idx = 8  # Skip n_bins
        for i in range(num_encoders):
            w_width = args[arg_idx + i] if arg_idx + i < len(args) else 3

        arg_idx = 12  # Skip w_width
        for i in range(num_encoders):
            period = args[arg_idx + i] if arg_idx + i < len(args) else 1.0

            # Create encoder parameters
            params = {
                'encoder_type': args[i] if i < len(args) else 'periodic_scalar',
                'n': args[4 + i] if 4 + i < len(args) else 8,
                'w': args[8 + i] if 8 + i < len(args) else 3,
                'period': args[12 + i] if 12 + i < len(args) else 1.0,
                'offset': 0.0,
                'xmin': -1.0,
                'xmax': 2.0
            }

            encoder = create_encoder_from_params(params)
            encoders.append(encoder)
            params_list.append(params)

        # Create comparison visualization
        fig = create_comparison_visualization(encoders, comparison_mode, params_list)
        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Comparison Error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper"
        )
        return fig

# Export callbacks
@callback(
    Output('download-config', 'data'),
    Input('save-single-config', 'n_clicks'),
    [State('n-bins', 'value'),
     State('w-width', 'value'),
     State('period', 'value'),
     State('offset', 'value'),
     State('xmin', 'value'),
     State('xmax', 'value'),
     State('encoder-type', 'value')],
    prevent_initial_call=True
)
def save_config(n_clicks, n_bins, w_width, period, offset, xmin, xmax, encoder_type):
    if n_clicks:
        config = {
            'n': n_bins,
            'w': w_width,
            'period': period,
            'offset': offset,
            'xmin': xmin,
            'xmax': xmax,
            'encoder_type': encoder_type
        }

        filename = export_encoder_config(config)

        return dcc.send_file(filename)

@callback(
    Output('download-plot', 'data'),
    Input('export-single-plot', 'n_clicks'),
    State('single-encoder-plot', 'figure'),
    prevent_initial_call=True
)
def export_plot(n_clicks, figure):
    if n_clicks and figure:
        filename = export_plot_html(go.Figure(figure))
        return dcc.send_file(filename)

if __name__ == '__main__':
    app.run(debug=True, port=8051)