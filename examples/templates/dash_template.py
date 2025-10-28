"""
Template for creating Dash/Plotly interactive visualizations with gnomevisual.

Usage:
    python gallery/templates/dash_template.py
    Then open http://localhost:8050 in your browser
"""
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

from gnomecode.encoders import PeriodicScalarEncoder


# Initialize the Dash app
app = dash.Dash(__name__)

# Create layout
app.layout = html.Div([
    html.H1("Gnome Code Interactive Visualization"),

    html.Div([
        html.Label("Number of Bins (n):"),
        dcc.Slider(
            id='n-slider',
            min=4, max=64, step=4, value=32,
            marks={i: str(i) for i in range(4, 65, 8)}
        ),
    ], style={'margin': '20px'}),

    html.Div([
        html.Label("Bin Width (w):"),
        dcc.Slider(
            id='w-slider',
            min=1, max=16, step=1, value=8,
            marks={i: str(i) for i in range(1, 17, 2)}
        ),
    ], style={'margin': '20px'}),

    dcc.Graph(id='encoder-plot'),
])


@app.callback(
    Output('encoder-plot', 'figure'),
    [Input('n-slider', 'value'),
     Input('w-slider', 'value')]
)
def update_plot(n, w):
    """Update the plot based on parameter changes."""
    # Create encoder
    encoder = PeriodicScalarEncoder(n=n, w=w, period=1.0, xmin=0.0, xmax=1.0)

    # Create visualization (example: encode several values)
    x_values = np.linspace(0, 1, 100)
    encodings = np.array([encoder.encode(x) for x in x_values])

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=encodings.T,
        x=x_values,
        y=np.arange(n),
        colorscale='Viridis',
    ))

    fig.update_layout(
        title=f'Encoder Response (n={n}, w={w})',
        xaxis_title='Input Value',
        yaxis_title='Bin Index',
        height=600,
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
