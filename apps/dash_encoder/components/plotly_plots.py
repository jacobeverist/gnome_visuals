import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import sys
import os

# Add utils to path for encoder_factory import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

def create_encoder_visualization(encoder, params):
    """Create interactive encoder visualization using Plotly."""

    try:
        # Get encoder properties
        xmin, xmax = params['xmin'], params['xmax']
        n_bins = params['n']

        # Create sample points for visualization
        x_vals = np.linspace(xmin, xmax, 200)

        # Get encoder boundaries and regions
        boundaries = encoder.region_boundaries
        regions = encoder.region_centers

        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Encoder Bins', 'Encoded Features'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4],
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": True}]]
        )

        # Plot 1: Encoder bins visualization
        colors = px.colors.qualitative.Set1

        # Draw encoding bins
        for i, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
            if i < len(colors):
                color = colors[i % len(colors)]
            else:
                color = f'hsl({(i * 137) % 360}, 70%, 50%)'

            fig.add_trace(
                go.Scatter(
                    x=[start, end, end, start, start],
                    y=[i, i, i+1, i+1, i],
                    fill='toself',
                    fillcolor=color,
                    line=dict(color=color, width=2),
                    name=f'Bin {i}',
                    showlegend=False,
                    hovertemplate=f'Bin {i}<br>Range: [{start:.3f}, {end:.3f}]<extra></extra>',
                    mode='lines'
                ),
                row=1, col=1
            )

        # Plot 2: Sample encoding visualization
        sample_points = np.linspace(xmin, xmax, 20)
        encoded_vals = []

        for x in sample_points:
            try:
                encoded = encoder.encode(x)
                encoded_vals.append(encoded)
            except:
                encoded_vals.append(np.zeros(n_bins))

        encoded_vals = np.array(encoded_vals)

        # Create heatmap of encoded values
        fig.add_trace(
            go.Heatmap(
                z=encoded_vals.T,
                x=sample_points,
                y=list(range(n_bins)),
                colorscale='Viridis',
                showscale=True,
                hovertemplate='Input: %{x:.3f}<br>Bit %{y}: %{z}<extra></extra>'
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_xaxes(title_text="Input Value", row=1, col=1)
        fig.update_yaxes(title_text="Bin Index", row=1, col=1)
        fig.update_xaxes(title_text="Input Value", row=2, col=1)
        fig.update_yaxes(title_text="Bit Index", row=2, col=1)

        fig.update_layout(
            title=f"Interactive Encoder Visualization (Type: {params['encoder_type']}, n={n_bins}, w={params['w']})",
            height=600,
            margin=dict(t=60, b=40, l=60, r=40)
        )

        return fig

    except Exception as e:
        # Return error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Visualization Error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=16, color="red")
        )
        fig.update_layout(title="Encoder Visualization Error")
        return fig

def create_heatmap_visualization(encoder, params):
    """Create interactive similarity heatmap using Plotly."""

    try:
        xmin, xmax = params['xmin'], params['xmax']

        # Generate sample points for similarity matrix
        n_samples = 30
        sample_points = np.linspace(xmin, xmax, n_samples)

        # Compute similarity matrix
        similarity_matrix = np.zeros((n_samples, n_samples))
        encoded_samples = []

        for i, x1 in enumerate(sample_points):
            try:
                enc1 = encoder.encode(x1)
                encoded_samples.append(enc1)
            except:
                encoded_samples.append(np.zeros(params['n']))

        encoded_samples = np.array(encoded_samples)

        # Calculate pairwise similarities (using dot product)
        for i in range(n_samples):
            for j in range(n_samples):
                similarity_matrix[i, j] = np.dot(encoded_samples[i], encoded_samples[j])

        # Create interactive heatmap
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=sample_points,
            y=sample_points,
            colorscale='RdBu_r',
            colorbar=dict(title="Similarity"),
            hovertemplate='X1: %{x:.3f}<br>X2: %{y:.3f}<br>Similarity: %{z:.3f}<extra></extra>'
        ))

        fig.update_layout(
            title=f"Interactive Similarity Heatmap (n={params['n']}, w={params['w']})",
            xaxis_title="Input Value 1",
            yaxis_title="Input Value 2",
            height=500,
            margin=dict(t=60, b=40, l=60, r=40)
        )

        return fig

    except Exception as e:
        # Return error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Heatmap Error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=16, color="red")
        )
        fig.update_layout(title="Heatmap Visualization Error")
        return fig

def create_3d_surface_visualization(encoder, params):
    """Create 3D parameter response surface visualization."""

    try:
        from encoder_factory import create_encoder_from_params

        # Create parameter meshgrid
        x_vals = np.linspace(params['xmin'], params['xmax'], 30)
        w_vals = np.linspace(1, 8, 20)

        X, W = np.meshgrid(x_vals, w_vals)
        Z = np.zeros_like(X)

        # Calculate response surface (encoding density)
        for i, w in enumerate(w_vals):
            for j, x in enumerate(x_vals):
                try:
                    # Create temporary encoder with different w
                    temp_params = params.copy()
                    temp_params['w'] = int(w)
                    temp_encoder = create_encoder_from_params(temp_params)
                    encoded = temp_encoder.encode(x)
                    Z[i, j] = np.sum(encoded)  # Total activation
                except:
                    Z[i, j] = 0

        fig = go.Figure(data=[go.Surface(
            z=Z, x=X, y=W,
            colorscale='Viridis',
            hovertemplate='Input: %{x:.3f}<br>Width: %{y:.0f}<br>Activation: %{z:.3f}<extra></extra>'
        )])

        fig.update_layout(
            title="3D Parameter Response Surface",
            scene=dict(
                xaxis_title="Input Value",
                yaxis_title="Bin Width (w)",
                zaxis_title="Total Activation"
            ),
            height=500
        )

        return fig

    except Exception as e:
        # Return error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"3D Surface Error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=16, color="red")
        )
        fig.update_layout(title="3D Surface Visualization Error")
        return fig