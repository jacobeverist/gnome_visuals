"""
Animation controls for parameter sweeps and dynamic visualizations.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import numpy as np
from typing import List, Dict, Any

def create_animation_controls():
    """Create animation control panel."""

    return dbc.Card([
        dbc.CardHeader(html.H5("Animation Controls")),
        dbc.CardBody([

            # Parameter to animate
            dbc.Row([
                dbc.Label("Animate Parameter:", width=4),
                dbc.Col([
                    dcc.Dropdown(
                        id='animate-parameter',
                        options=[
                            {'label': 'Number of Bins (n)', 'value': 'n'},
                            {'label': 'Bin Width (w)', 'value': 'w'},
                            {'label': 'Period', 'value': 'period'},
                            {'label': 'Offset', 'value': 'offset'}
                        ],
                        value='w',
                        clearable=False
                    )
                ], width=8)
            ], className="mb-3"),

            # Animation range
            dbc.Row([
                dbc.Label("Start Value:", width=4),
                dbc.Col([
                    dcc.Input(
                        id='animate-start',
                        type='number',
                        value=1,
                        step=0.1,
                        className="form-control"
                    )
                ], width=8)
            ], className="mb-2"),

            dbc.Row([
                dbc.Label("End Value:", width=4),
                dbc.Col([
                    dcc.Input(
                        id='animate-end',
                        type='number',
                        value=8,
                        step=0.1,
                        className="form-control"
                    )
                ], width=8)
            ], className="mb-2"),

            dbc.Row([
                dbc.Label("Steps:", width=4),
                dbc.Col([
                    dcc.Input(
                        id='animate-steps',
                        type='number',
                        value=8,
                        min=3,
                        max=50,
                        step=1,
                        className="form-control"
                    )
                ], width=8)
            ], className="mb-3"),

            # Animation speed
            dbc.Row([
                dbc.Label("Speed (ms/frame):", width=4),
                dbc.Col([
                    dcc.Slider(
                        id='animate-speed',
                        min=100,
                        max=2000,
                        step=100,
                        value=500,
                        marks={i: f'{i}ms' for i in range(200, 2001, 400)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=8)
            ], className="mb-3"),

            # Animation controls
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("▶️ Play", id="play-animation", color="success", size="sm"),
                        dbc.Button("⏸️ Pause", id="pause-animation", color="warning", size="sm"),
                        dbc.Button("⏹️ Stop", id="stop-animation", color="danger", size="sm"),
                        dbc.Button("🔄 Reset", id="reset-animation", color="secondary", size="sm")
                    ])
                ])
            ], className="mb-3"),

            # Animation mode
            dbc.Row([
                dbc.Label("Mode:", width=4),
                dbc.Col([
                    dcc.RadioItems(
                        id='animate-mode',
                        options=[
                            {'label': 'Loop', 'value': 'loop'},
                            {'label': 'Bounce', 'value': 'bounce'},
                            {'label': 'Once', 'value': 'once'}
                        ],
                        value='loop',
                        inline=True
                    )
                ], width=8)
            ], className="mb-3"),

            # Current frame display
            html.Hr(),
            html.Div([
                html.P("Current Frame:", className="mb-1"),
                html.Div(id="current-frame-display", className="text-center")
            ])
        ])
    ], className="mb-4")

def create_animated_plot(base_params: Dict[str, Any],
                        animate_param: str,
                        animate_values: List[float],
                        current_frame: int = 0) -> go.Figure:
    """
    Create animated plot with parameter sweep.

    Args:
        base_params: Base encoder parameters
        animate_param: Parameter to animate ('n', 'w', 'period', 'offset')
        animate_values: List of values for the animated parameter
        current_frame: Current animation frame

    Returns:
        Plotly figure with animation frames
    """

    frames = []
    frame_data = []

    for i, value in enumerate(animate_values):
        # Create parameters for this frame
        frame_params = base_params.copy()
        frame_params[animate_param] = value

        try:
            from utils.encoder_factory import create_encoder_from_params
            encoder = create_encoder_from_params(frame_params)

            # Generate visualization data for this frame
            xmin, xmax = frame_params.get('xmin', -1.0), frame_params.get('xmax', 2.0)
            sample_points = np.linspace(xmin, xmax, 50)

            # Calculate encoding activations
            activations = []
            for x in sample_points:
                try:
                    encoded = encoder.encode(x)
                    activations.append(np.sum(encoded))
                except:
                    activations.append(0)

            # Create frame data
            frame_trace = go.Scatter(
                x=sample_points,
                y=activations,
                mode='lines+markers',
                name=f'{animate_param}={value}',
                line=dict(width=3)
            )

            frame_data.append({
                'data': [frame_trace],
                'name': str(i),
                'layout': {
                    'title': f'Animated Parameter Sweep: {animate_param}={value:.2f}',
                    'xaxis': {'title': 'Input Value', 'range': [xmin, xmax]},
                    'yaxis': {'title': 'Total Activation'},
                }
            })

        except Exception as e:
            # Error frame
            frame_trace = go.Scatter(
                x=[0], y=[0],
                mode='markers+text',
                text=[f'Error: {str(e)[:30]}...'],
                textposition='middle center'
            )
            frame_data.append({
                'data': [frame_trace],
                'name': str(i),
                'layout': {'title': f'Error in frame {i}'}
            })

    # Create figure with frames
    if frame_data:
        initial_data = frame_data[current_frame % len(frame_data)]

        fig = go.Figure(
            data=initial_data['data'],
            layout=initial_data['layout']
        )

        # Add frames for animation
        frames = []
        for frame in frame_data:
            frames.append(go.Frame(
                data=frame['data'],
                layout=frame['layout'],
                name=frame['name']
            ))

        fig.frames = frames

        # Add animation configuration
        fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶️',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 300, 'easing': 'quadratic-in-out'}
                        }]
                    },
                    {
                        'label': '⏸️',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ],
                'x': 0.1,
                'y': 0,
                'xanchor': 'right',
                'yanchor': 'top'
            }],
            sliders=[{
                'steps': [
                    {
                        'args': [[frame['name']], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': f'{animate_values[int(frame["name"])]:g}',
                        'method': 'animate'
                    }
                    for frame in frame_data
                ],
                'active': current_frame,
                'currentvalue': {'prefix': f'{animate_param}: '},
                'len': 0.8,
                'x': 0.1,
                'xanchor': 'left',
                'y': 0,
                'yanchor': 'top'
            }]
        )

    else:
        # Empty figure if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No animation data available",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper"
        )

    return fig

def create_parameter_sweep_heatmap(base_params: Dict[str, Any],
                                  param1: str, param1_values: List[float],
                                  param2: str, param2_values: List[float]) -> go.Figure:
    """
    Create 2D parameter sweep heatmap.

    Args:
        base_params: Base encoder parameters
        param1: First parameter to sweep
        param1_values: Values for first parameter
        param2: Second parameter to sweep
        param2_values: Values for second parameter

    Returns:
        Plotly heatmap figure
    """

    try:
        from utils.encoder_factory import create_encoder_from_params

        # Create response surface
        response_matrix = np.zeros((len(param2_values), len(param1_values)))

        for i, p2_val in enumerate(param2_values):
            for j, p1_val in enumerate(param1_values):
                try:
                    # Create parameters for this combination
                    sweep_params = base_params.copy()
                    sweep_params[param1] = p1_val
                    sweep_params[param2] = p2_val

                    encoder = create_encoder_from_params(sweep_params)

                    # Calculate response metric (e.g., total activation at x=0)
                    encoded = encoder.encode(0.0)
                    response_matrix[i, j] = np.sum(encoded)

                except Exception:
                    response_matrix[i, j] = 0

        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=response_matrix,
            x=param1_values,
            y=param2_values,
            colorscale='Viridis',
            hovertemplate=f'{param1}: %{{x}}<br>{param2}: %{{y}}<br>Response: %{{z}}<extra></extra>'
        ))

        fig.update_layout(
            title=f'Parameter Sweep: {param1} vs {param2}',
            xaxis_title=param1,
            yaxis_title=param2,
            height=500
        )

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Parameter sweep error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper"
        )

    return fig

def generate_animation_values(start: float, end: float, steps: int, param_name: str) -> List[float]:
    """
    Generate appropriate animation values for a parameter.

    Args:
        start: Start value
        end: End value
        steps: Number of steps
        param_name: Parameter name for type-specific handling

    Returns:
        List of animation values
    """

    if param_name == 'n':
        # For n (number of bins), use integers only
        start_int = max(1, int(start))
        end_int = max(start_int + 1, int(end))
        return list(range(start_int, end_int + 1))

    elif param_name == 'w':
        # For w (width), use integers only
        start_int = max(1, int(start))
        end_int = max(start_int + 1, int(end))
        return list(range(start_int, end_int + 1))

    else:
        # For continuous parameters, use linear spacing
        return list(np.linspace(start, end, steps))

def create_animation_timeline(animate_values: List[float],
                            current_frame: int,
                            param_name: str) -> html.Div:
    """
    Create timeline visualization for animation.

    Args:
        animate_values: List of animation values
        current_frame: Current frame index
        param_name: Parameter name

    Returns:
        HTML div with timeline
    """

    timeline_items = []

    for i, value in enumerate(animate_values):
        is_current = i == current_frame
        is_past = i < current_frame

        item_class = "timeline-item"
        if is_current:
            item_class += " current"
        elif is_past:
            item_class += " past"

        timeline_items.append(
            html.Div([
                html.Div(f"{value:g}", className="timeline-value"),
                html.Div("●", className="timeline-dot")
            ], className=item_class)
        )

    return html.Div([
        html.P(f"Animation Timeline - {param_name}"),
        html.Div(timeline_items, className="timeline-container")
    ], className="animation-timeline")