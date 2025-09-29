"""
Advanced visualization concepts for gnomecode encoders.

These are additional dashboard components you can integrate into the main dashboard
or use as standalone visualizations for deeper encoder analysis.
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import gnomecode.encoders as encoders
import gnomecode.utils as utils
from typing import Dict, List, Tuple, Any


# Initialize Dash app
app = dash.Dash(__name__)



def create_encoder_comparison_dashboard():
    """Create a side-by-side encoder comparison interface."""
    return html.Div([
        html.H3("Encoder Comparison Tool"),

        html.Div([
            # First encoder controls
            html.Div([
                html.H4("Encoder A"),
                dcc.Dropdown(
                    id='encoder-a-type',
                    options=[
                        {'label': 'Fixed Weight', 'value': 'fixed_weight'},
                        {'label': 'Periodic Cell', 'value': 'periodic_cell'},
                        {'label': 'Place Cell', 'value': 'place_cell'},
                    ],
                    value='fixed_weight'
                ),
                html.Label("n:"),
                dcc.Slider(id='encoder-a-n', min=5, max=50, value=20),
                html.Label("w:"),
                dcc.Slider(id='encoder-a-w', min=1, max=10, value=3),
            ], style={'width': '45%', 'display': 'inline-block'}),

            # Second encoder controls
            html.Div([
                html.H4("Encoder B"),
                dcc.Dropdown(
                    id='encoder-b-type',
                    options=[
                        {'label': 'Fixed Weight', 'value': 'fixed_weight'},
                        {'label': 'Periodic Cell', 'value': 'periodic_cell'},
                        {'label': 'Place Cell', 'value': 'place_cell'},
                    ],
                    value='periodic_cell'
                ),
                html.Label("n:"),
                dcc.Slider(id='encoder-b-n', min=5, max=50, value=20),
                html.Label("w:"),
                dcc.Slider(id='encoder-b-w', min=1, max=10, value=3),
            ], style={'width': '45%', 'display': 'inline-block', 'margin-left': '10%'}),
        ]),

        # Comparison plots
        html.Div([
            dcc.Graph(id='encoder-a-heatmap'),
            dcc.Graph(id='encoder-b-heatmap'),
            dcc.Graph(id='cross-encoder-similarity')
        ])
    ])

def create_temporal_encoding_visualization():
    """Create a visualization for time-series encoding."""

    def generate_signal_and_encode(signal_type='sine', encoder_type='fixed_weight'):
        """Generate a test signal and encode it."""
        t = np.linspace(0, 4*np.pi, 100)

        if signal_type == 'sine':
            signal = np.sin(t) + 0.3*np.sin(3*t)
        elif signal_type == 'chirp':
            signal = np.sin(t + 0.1*t**2)
        elif signal_type == 'step':
            signal = np.where(t < 2*np.pi, -0.5, 0.5)
        elif signal_type == 'noise':
            signal = np.random.normal(0, 0.5, len(t))

        # Normalize to [-1, 1]
        signal = 2 * (signal - signal.min()) / (signal.max() - signal.min()) - 1

        # Encode
        encoder = encoders.create_encoder(encoder_type, n=32, w=4)
        encoded = encoder.encode(signal.reshape(-1, 1))

        return t, signal, encoded

    # Generate example data
    t, signal, encoded = generate_signal_and_encode()

    # Create plots
    signal_fig = px.line(x=t, y=signal, title='Input Signal')
    signal_fig.update_layout(xaxis_title='Time', yaxis_title='Amplitude')

    encoding_fig = go.Figure(data=go.Heatmap(
        z=encoded.T,
        x=t,
        y=list(range(encoded.shape[1])),
        colorscale='Viridis'
    ))
    encoding_fig.update_layout(
        title='Encoded Representation Over Time',
        xaxis_title='Time',
        yaxis_title='Bit Index'
    )

    return html.Div([
        html.H3("Temporal Encoding Analysis"),
        dcc.Dropdown(
            id='signal-type',
            options=[
                {'label': 'Sine Wave', 'value': 'sine'},
                {'label': 'Chirp', 'value': 'chirp'},
                {'label': 'Step Function', 'value': 'step'},
                {'label': 'Random Noise', 'value': 'noise'}
            ],
            value='sine'
        ),
        dcc.Graph(figure=signal_fig, id='signal-plot'),
        dcc.Graph(figure=encoding_fig, id='encoding-plot')
    ])

def create_boundary_handling_demo():
    """Demonstrate different boundary handling strategies."""

    # Test inputs including out-of-bounds values
    test_inputs = np.linspace(-0.5, 1.5, 100)

    boundary_strategies = ['clamp', 'modulo', 'silent']
    figures = []

    for strategy in boundary_strategies:
        try:
            encoder = encoders.create_encoder(
                'fixed_weight',
                n=20, w=3,
                lower_bound=0.0, upper_bound=1.0,
                boundary_handling=strategy
            )

            if strategy != 'exception':  # Skip exception strategy for demo
                encoded = encoder.encode(test_inputs.reshape(-1, 1))

                fig = go.Figure(data=go.Heatmap(
                    z=encoded.T,
                    x=test_inputs,
                    y=list(range(encoded.shape[1])),
                    colorscale='Viridis'
                ))
                fig.update_layout(
                    title=f'Boundary Strategy: {strategy.title()}',
                    xaxis_title='Input Value (bounds: [0, 1])',
                    yaxis_title='Bit Index'
                )

                # Add boundary lines
                fig.add_vline(x=0.0, line_dash="dash", line_color="red",
                            annotation_text="Lower Bound")
                fig.add_vline(x=1.0, line_dash="dash", line_color="red",
                            annotation_text="Upper Bound")

                figures.append(dcc.Graph(figure=fig))

        except Exception as e:
            figures.append(html.P(f"Error with {strategy}: {str(e)}"))

    return html.Div([
        html.H3("Boundary Handling Strategies"),
        html.P("Red dashed lines show encoder bounds [0, 1]. Input range: [-0.5, 1.5]"),
    ] + figures)

def create_multi_encoder_analysis():
    """Analyze composite multi-encoder behavior."""

    # Create individual encoders
    encoder1 = encoders.create_encoder('fixed_weight', n=10, w=2)
    encoder2 = encoders.create_encoder('periodic_cell', n=8)
    # encoder3 = encoders.create_encoder('place_cell', n=12)

    # Create multi-encoder (if available)
    try:
        multi_encoder = encoders.MultiEncoder([encoder1, encoder2, encoder3])

        # Test inputs
        inputs = np.linspace(0, 1, 50)

        # Individual encodings
        enc1 = encoder1.encode(inputs.reshape(-1, 1))
        enc2 = encoder2.encode(inputs.reshape(-1, 1))
        # enc3 = encoder3.encode(inputs.reshape(-1, 1))
        enc_multi = multi_encoder.encode(inputs.reshape(-1, 1))

        figures = []

        # Individual encoder plots
        for i, (name, encoded) in enumerate([
            ('Fixed Weight', enc1),
            ('Periodic Cell', enc2),
            # ('Place Cell', enc3)
        ]):
            fig = go.Figure(data=go.Heatmap(
                z=encoded.T,
                x=inputs,
                colorscale='Viridis'
            ))
            fig.update_layout(
                title=f'{name} Component',
                xaxis_title='Input Value',
                yaxis_title='Bit Index'
            )
            figures.append(dcc.Graph(figure=fig))

        # Combined multi-encoder plot
        fig_multi = go.Figure(data=go.Heatmap(
            z=enc_multi.T,
            x=inputs,
            colorscale='Viridis'
        ))
        fig_multi.update_layout(
            title='Combined Multi-Encoder Output',
            xaxis_title='Input Value',
            yaxis_title='Bit Index'
        )
        figures.append(dcc.Graph(figure=fig_multi))

        return html.Div([
            html.H3("Multi-Encoder Component Analysis"),
        ] + figures)

    except Exception as e:
        return html.Div([
            html.H3("Multi-Encoder Analysis"),
            html.P(f"Error creating multi-encoder: {str(e)}")
        ])

def create_similarity_clustering_analysis():
    """Analyze encoder outputs using similarity-based clustering."""

    # Generate diverse test inputs
    inputs = np.array([
        np.linspace(0, 1, 20),           # Linear progression
        np.sin(np.linspace(0, 2*np.pi, 20)),  # Sinusoidal
        np.random.uniform(-1, 1, 20)     # Random
    ]).flatten()

    # Create encoder and encode
    encoder = encoders.create_encoder('fixed_weight', n=25, w=4)
    encoded = encoder.encode(inputs.reshape(-1, 1))

    # Calculate similarity matrix
    similarity_matrix = utils.count_similarity(encoded, encoded, normalize=True)

    # Create similarity heatmap with clustering
    fig_similarity = px.imshow(
        similarity_matrix,
        title='Encoded Input Similarity Matrix',
        color_continuous_scale='viridis',
        aspect='equal'
    )

    # Create dendrogram-style plot (simplified)
    from scipy.cluster.hierarchy import linkage, dendrogram
    from scipy.spatial.distance import squareform

    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    condensed_distances = squareform(distance_matrix)

    # Perform hierarchical clustering
    linkage_matrix = linkage(condensed_distances, method='average')
    dendro = dendrogram(linkage_matrix, no_plot=True)

    # Create dendrogram plot
    fig_dendro = go.Figure()

    # Add dendrogram lines (simplified representation)
    for i in range(len(dendro['icoord'])):
        x = dendro['icoord'][i]
        y = dendro['dcoord'][i]
        fig_dendro.add_trace(go.Scatter(
            x=x, y=y, mode='lines',
            line=dict(color='black', width=1),
            showlegend=False
        ))

    fig_dendro.update_layout(
        title='Hierarchical Clustering of Encoded Inputs',
        xaxis_title='Input Index',
        yaxis_title='Distance'
    )

    return html.Div([
        html.H3("Similarity and Clustering Analysis"),
        dcc.Graph(figure=fig_similarity),
        dcc.Graph(figure=fig_dendro)
    ])

def create_parameter_sensitivity_analysis():
    """Analyze how encoder parameters affect output characteristics."""

    # Parameter ranges to test
    n_values = range(10, 51, 10)
    w_values = range(1, 6)

    metrics_data = []

    for n in n_values:
        for w in w_values:
            try:
                encoder = encoders.create_encoder('fixed_weight', n=n, w=w)

                # Test with standard inputs
                test_inputs = np.linspace(0, 1, 20)
                encoded = encoder.encode(test_inputs.reshape(-1, 1))

                # Calculate metrics
                sparsity = np.mean(np.sum(encoded, axis=1) / encoded.shape[1])
                coverage = np.mean(np.mean(encoded, axis=0) > 0)  # Fraction of bits used
                overlap = utils.count_similarity(encoded, encoded, normalize=True)
                mean_similarity = np.mean(overlap[np.triu_indices_from(overlap, k=1)])

                metrics_data.append({
                    'n': n, 'w': w, 'sparsity': sparsity,
                    'coverage': coverage, 'similarity': mean_similarity
                })

            except Exception:
                continue

    if metrics_data:
        import pandas as pd
        df = pd.DataFrame(metrics_data)

        figures = []

        # Sparsity heatmap
        sparsity_pivot = df.pivot(index='w', columns='n', values='sparsity')
        fig_spars = px.imshow(
            sparsity_pivot,
            title='Sparsity vs Parameters',
            labels={'x': 'n (bins)', 'y': 'w (weight)', 'color': 'Sparsity'}
        )
        figures.append(dcc.Graph(figure=fig_spars))

        # Coverage heatmap
        coverage_pivot = df.pivot(index='w', columns='n', values='coverage')
        fig_cov = px.imshow(
            coverage_pivot,
            title='Coverage vs Parameters',
            labels={'x': 'n (bins)', 'y': 'w (weight)', 'color': 'Coverage'}
        )
        figures.append(dcc.Graph(figure=fig_cov))

        return html.Div([
            html.H3("Parameter Sensitivity Analysis"),
        ] + figures)

    return html.Div([html.H3("Parameter Sensitivity Analysis"),
                     html.P("No data available")])

def setup():
    fig1 = create_encoder_comparison_dashboard()
    fig2 = create_temporal_encoding_visualization()
    fig3 = create_boundary_handling_demo()
    fig4 = create_multi_encoder_analysis()
    fig5 = create_similarity_clustering_analysis()
    fig6 = create_parameter_sensitivity_analysis()

    app.layout = html.Div([
            html.H1("Visualization of Multiple Scalar Encoders over Unit Interval"),
            html.Div([fig1, fig2, fig3, fig4, fig5, fig6])
    ])



    # Example usage functions
if __name__ == "__main__":
    # These functions can be called individually to create specific visualizations
    print("Advanced visualization components created!")
    print("Integrate these into your main dashboard or use standalone.")

    setup()
    app.run(debug=True, port=8010)


