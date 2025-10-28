import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json

def create_comparison_controls():
    """Create controls for encoder comparison mode."""

    return dbc.Card([
        dbc.CardHeader(html.H5("Encoder Comparison Controls")),
        dbc.CardBody([

            # Comparison mode selector
            dbc.Row([
                dbc.Label("Comparison Mode:", width=4),
                dbc.Col([
                    dcc.Dropdown(
                        id='comparison-mode',
                        options=[
                            {'label': 'Side-by-side', 'value': 'side_by_side'},
                            {'label': 'Overlay', 'value': 'overlay'},
                            {'label': 'Difference', 'value': 'difference'}
                        ],
                        value='side_by_side',
                        clearable=False
                    )
                ], width=8)
            ], className="mb-3"),

            # Number of encoders to compare
            dbc.Row([
                dbc.Label("Number of Encoders:", width=4),
                dbc.Col([
                    dcc.Slider(
                        id='num-encoders',
                        min=2,
                        max=4,
                        step=1,
                        value=2,
                        marks={i: str(i) for i in range(2, 5)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=8)
            ], className="mb-3"),

            # Save/Load configurations
            html.Hr(),
            html.H6("Configuration Management"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Save Config A", id="save-config-a", size="sm", color="primary", className="me-1"),
                    dbc.Button("Save Config B", id="save-config-b", size="sm", color="primary", className="me-1"),
                ], width=12)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Load Config A", id="load-config-a", size="sm", color="secondary", className="me-1"),
                    dbc.Button("Load Config B", id="load-config-b", size="sm", color="secondary", className="me-1"),
                ], width=12)
            ], className="mb-2"),

            # Export comparison
            html.Hr(),
            html.H6("Export Options"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Export Comparison", id="export-comparison", size="sm", color="success", className="me-1"),
                    dbc.Button("Generate Report", id="generate-report", size="sm", color="info"),
                ], width=12)
            ])
        ])
    ], className="mb-4")

def create_encoder_config_panel(encoder_id):
    """Create individual encoder configuration panel for comparison."""

    return dbc.Card([
        dbc.CardHeader(html.H6(f"Encoder {encoder_id.upper()}")),
        dbc.CardBody([
            # Encoder type
            dbc.Row([
                dbc.Label("Type:", width=3),
                dbc.Col([
                    dcc.Dropdown(
                        id=f'encoder-type-{encoder_id}',
                        options=[
                            {'label': 'Periodic Scalar', 'value': 'periodic_scalar'},
                            {'label': 'Periodic Cell', 'value': 'periodic_cell'},
                            {'label': 'Multi Encoder', 'value': 'multi_encoder'}
                        ],
                        value='periodic_scalar',
                        clearable=False
                    )
                ], width=9)
            ], className="mb-2"),

            # Bins
            dbc.Row([
                dbc.Label("n:", width=3),
                dbc.Col([
                    dcc.Slider(
                        id=f'n-bins-{encoder_id}',
                        min=4, max=32, step=1, value=8,
                        marks={i: str(i) for i in [4, 8, 16, 24, 32]},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=9)
            ], className="mb-2"),

            # Width
            dbc.Row([
                dbc.Label("w:", width=3),
                dbc.Col([
                    dcc.Slider(
                        id=f'w-width-{encoder_id}',
                        min=1, max=8, step=1, value=3,
                        marks={i: str(i) for i in [1, 2, 4, 6, 8]},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=9)
            ], className="mb-2"),

            # Period
            dbc.Row([
                dbc.Label("Period:", width=3),
                dbc.Col([
                    dcc.Slider(
                        id=f'period-{encoder_id}',
                        min=0.1, max=2.0, step=0.1, value=1.0,
                        marks={i/10: f'{i/10:.1f}' for i in [2, 10, 20]},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=9)
            ], className="mb-2"),

            # Color for visualization
            dbc.Row([
                dbc.Label("Color:", width=3),
                dbc.Col([
                    dcc.Dropdown(
                        id=f'color-{encoder_id}',
                        options=[
                            {'label': 'Blue', 'value': 'blue'},
                            {'label': 'Red', 'value': 'red'},
                            {'label': 'Green', 'value': 'green'},
                            {'label': 'Orange', 'value': 'orange'}
                        ],
                        value='blue' if encoder_id == 'a' else 'red',
                        clearable=False
                    )
                ], width=9)
            ])
        ])
    ], className="mb-3")

def create_comparison_visualization(encoders, mode, params):
    """Create comparison visualization for multiple encoders."""

    if mode == 'side_by_side':
        return create_side_by_side_comparison(encoders, params)
    elif mode == 'overlay':
        return create_overlay_comparison(encoders, params)
    elif mode == 'difference':
        return create_difference_comparison(encoders, params)
    else:
        return create_side_by_side_comparison(encoders, params)

def create_side_by_side_comparison(encoders, params):
    """Create side-by-side comparison plots."""

    n_encoders = len(encoders)
    fig = make_subplots(
        rows=2, cols=n_encoders,
        subplot_titles=[f"Encoder {chr(65+i)}" for i in range(n_encoders)] +
                       [f"Similarity {chr(65+i)}" for i in range(n_encoders)],
        vertical_spacing=0.15
    )

    colors = ['blue', 'red', 'green', 'orange']

    for i, (encoder, param_set) in enumerate(zip(encoders, params)):
        try:
            # Plot encoder bins
            xmin, xmax = param_set.get('xmin', -1.0), param_set.get('xmax', 2.0)
            boundaries = getattr(encoder, 'region_boundaries', np.linspace(xmin, xmax, param_set.get('n', 8)+1))

            for j, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
                fig.add_trace(
                    go.Scatter(
                        x=[start, end, end, start, start],
                        y=[j, j, j+1, j+1, j],
                        fill='toself',
                        fillcolor=colors[i % len(colors)],
                        line=dict(color=colors[i % len(colors)], width=1),
                        showlegend=False,
                        name=f'Bin {j}',
                        opacity=0.7
                    ),
                    row=1, col=i+1
                )

            # Plot similarity heatmap
            sample_points = np.linspace(xmin, xmax, 20)
            similarity_matrix = np.zeros((20, 20))

            for x_idx, x1 in enumerate(sample_points):
                for y_idx, x2 in enumerate(sample_points):
                    try:
                        enc1 = encoder.encode(x1)
                        enc2 = encoder.encode(x2)
                        similarity_matrix[x_idx, y_idx] = np.dot(enc1, enc2)
                    except:
                        similarity_matrix[x_idx, y_idx] = 0

            fig.add_trace(
                go.Heatmap(
                    z=similarity_matrix,
                    x=sample_points,
                    y=sample_points,
                    colorscale='Viridis',
                    showscale=i == 0,  # Only show colorbar for first plot
                    name=f'Similarity {chr(65+i)}'
                ),
                row=2, col=i+1
            )

        except Exception as e:
            # Add error annotation
            fig.add_annotation(
                text=f"Error: {str(e)[:50]}...",
                x=0.5, y=0.5,
                xref=f"x{i+1}", yref=f"y{i+1}",
                showarrow=False
            )

    fig.update_layout(
        title="Side-by-Side Encoder Comparison",
        height=800,
        showlegend=False
    )

    return fig

def create_overlay_comparison(encoders, params):
    """Create overlay comparison plot."""

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=['Overlaid Encoder Bins', 'Combined Similarity Analysis'],
        vertical_spacing=0.15
    )

    colors = ['blue', 'red', 'green', 'orange']

    for i, (encoder, param_set) in enumerate(zip(encoders, params)):
        try:
            # Plot encoder bins with transparency
            xmin, xmax = param_set.get('xmin', -1.0), param_set.get('xmax', 2.0)
            boundaries = getattr(encoder, 'region_boundaries', np.linspace(xmin, xmax, param_set.get('n', 8)+1))

            for j, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
                fig.add_trace(
                    go.Scatter(
                        x=[start, end, end, start, start],
                        y=[j + i*0.1, j + i*0.1, j+1 + i*0.1, j+1 + i*0.1, j + i*0.1],
                        fill='toself',
                        fillcolor=colors[i % len(colors)],
                        line=dict(color=colors[i % len(colors)], width=2),
                        name=f'Encoder {chr(65+i)} Bin {j}',
                        opacity=0.5,
                        legendgroup=f'encoder_{i}',
                        showlegend=(j == 0)
                    ),
                    row=1, col=1
                )

            # Add combined analysis in second subplot
            sample_points = np.linspace(xmin, xmax, 30)
            activations = []

            for x in sample_points:
                try:
                    encoded = encoder.encode(x)
                    activations.append(np.sum(encoded))
                except:
                    activations.append(0)

            fig.add_trace(
                go.Scatter(
                    x=sample_points,
                    y=activations,
                    mode='lines+markers',
                    name=f'Encoder {chr(65+i)} Activation',
                    line=dict(color=colors[i % len(colors)], width=3),
                    legendgroup=f'encoder_{i}'
                ),
                row=2, col=1
            )

        except Exception as e:
            fig.add_annotation(
                text=f"Error in Encoder {chr(65+i)}: {str(e)[:30]}...",
                x=0.5, y=0.5,
                showarrow=False
            )

    fig.update_layout(
        title="Overlay Encoder Comparison",
        height=800
    )

    return fig

def create_difference_comparison(encoders, params):
    """Create difference analysis between encoders."""

    if len(encoders) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Need at least 2 encoders for difference analysis",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Similarity Difference (A-B)', 'Activation Difference',
                       'Parameter Comparison', 'Overlap Analysis'],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    try:
        encoder_a, encoder_b = encoders[0], encoders[1]
        params_a, params_b = params[0], params[1]

        xmin = min(params_a.get('xmin', -1.0), params_b.get('xmin', -1.0))
        xmax = max(params_a.get('xmax', 2.0), params_b.get('xmax', 2.0))

        # Similarity difference
        sample_points = np.linspace(xmin, xmax, 20)
        sim_a = np.zeros((20, 20))
        sim_b = np.zeros((20, 20))

        for i, x1 in enumerate(sample_points):
            for j, x2 in enumerate(sample_points):
                try:
                    enc_a1, enc_a2 = encoder_a.encode(x1), encoder_a.encode(x2)
                    enc_b1, enc_b2 = encoder_b.encode(x1), encoder_b.encode(x2)
                    sim_a[i, j] = np.dot(enc_a1, enc_a2)
                    sim_b[i, j] = np.dot(enc_b1, enc_b2)
                except:
                    sim_a[i, j] = sim_b[i, j] = 0

        diff_matrix = sim_a - sim_b

        fig.add_trace(
            go.Heatmap(
                z=diff_matrix,
                x=sample_points,
                y=sample_points,
                colorscale='RdBu',
                zmid=0,
                name='Similarity Difference'
            ),
            row=1, col=1
        )

        # Activation difference
        activations_a = []
        activations_b = []

        for x in sample_points:
            try:
                enc_a = encoder_a.encode(x)
                enc_b = encoder_b.encode(x)
                activations_a.append(np.sum(enc_a))
                activations_b.append(np.sum(enc_b))
            except:
                activations_a.append(0)
                activations_b.append(0)

        fig.add_trace(
            go.Scatter(
                x=sample_points,
                y=np.array(activations_a) - np.array(activations_b),
                mode='lines+markers',
                name='Activation Difference (A-B)',
                line=dict(color='purple', width=3)
            ),
            row=1, col=2
        )

        # Parameter comparison
        param_names = ['n', 'w', 'period']
        values_a = [params_a.get(p, 0) for p in param_names]
        values_b = [params_b.get(p, 0) for p in param_names]

        fig.add_trace(
            go.Bar(
                x=param_names,
                y=values_a,
                name='Encoder A',
                marker_color='blue',
                opacity=0.7
            ),
            row=2, col=1
        )

        fig.add_trace(
            go.Bar(
                x=param_names,
                y=values_b,
                name='Encoder B',
                marker_color='red',
                opacity=0.7
            ),
            row=2, col=1
        )

        # Overlap analysis
        overlap_scores = []
        for x in np.linspace(xmin, xmax, 50):
            try:
                enc_a = encoder_a.encode(x)
                enc_b = encoder_b.encode(x)
                # Jaccard similarity
                intersection = np.sum(enc_a * enc_b)
                union = np.sum((enc_a + enc_b) > 0)
                overlap = intersection / union if union > 0 else 0
                overlap_scores.append(overlap)
            except:
                overlap_scores.append(0)

        fig.add_trace(
            go.Scatter(
                x=np.linspace(xmin, xmax, 50),
                y=overlap_scores,
                mode='lines',
                name='Overlap Score',
                line=dict(color='green', width=3),
                fill='tonexty'
            ),
            row=2, col=2
        )

    except Exception as e:
        fig.add_annotation(
            text=f"Difference analysis error: {str(e)}",
            x=0.5, y=0.5,
            showarrow=False
        )

    fig.update_layout(
        title="Encoder Difference Analysis",
        height=800,
        showlegend=True
    )

    return fig