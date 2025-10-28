import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from components.encoder_controls import create_encoder_controls
from components.plotly_plots import create_encoder_visualization, create_heatmap_visualization
from utils.encoder_factory import create_encoder_from_params

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GNOME Encoder Interactive Visualizer"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("GNOME Encoder Interactive Visualizer", className="text-center mb-4"),
            html.Hr()
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Encoder Parameters")),
                dbc.CardBody([
                    create_encoder_controls()
                ])
            ], className="mb-4")
        ], width=3),

        dbc.Col([
            dbc.Tabs([
                dbc.Tab(
                    label="Encoder Visualization",
                    tab_id="encoder-viz",
                    children=[
                        dcc.Loading([
                            dcc.Graph(id="encoder-plot", style={'height': '600px'})
                        ])
                    ]
                ),
                dbc.Tab(
                    label="Similarity Heatmap",
                    tab_id="heatmap-viz",
                    children=[
                        dcc.Loading([
                            dcc.Graph(id="heatmap-plot", style={'height': '600px'})
                        ])
                    ]
                ),
                dbc.Tab(
                    label="3D Analysis",
                    tab_id="3d-viz",
                    children=[
                        dcc.Loading([
                            dcc.Graph(id="3d-plot", style={'height': '600px'})
                        ])
                    ]
                )
            ], id="tabs", active_tab="encoder-viz")
        ], width=9)
    ])
], fluid=True)

@callback(
    [Output('encoder-plot', 'figure'),
     Output('heatmap-plot', 'figure'),
     Output('3d-plot', 'figure')],
    [Input('n-bins', 'value'),
     Input('w-width', 'value'),
     Input('period', 'value'),
     Input('offset', 'value'),
     Input('xmin', 'value'),
     Input('xmax', 'value'),
     Input('encoder-type', 'value')]
)
def update_visualizations(n_bins, w_width, period, offset, xmin, xmax, encoder_type):
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

        # Create a simple 3D surface for now
        x_vals = np.linspace(xmin, xmax, 50)
        y_vals = np.linspace(xmin, xmax, 50)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = np.sin(X * period * 2 * np.pi) * np.cos(Y * period * 2 * np.pi)

        fig_3d = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
        fig_3d.update_layout(
            title=f"Parameter Response Surface (n={n_bins}, w={w_width})",
            scene=dict(
                xaxis_title="X Parameter",
                yaxis_title="Y Parameter",
                zaxis_title="Response"
            ),
            margin=dict(t=40, b=40, l=40, r=40)
        )

        return encoder_fig, heatmap_fig, fig_3d

    except Exception as e:
        # Return empty figures on error
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper"
        )
        return empty_fig, empty_fig, empty_fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)