import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import numpy.ma as ma
from icecream import ic
from dash import html
import seaborn as sns
from typing import Dict, List, Tuple, Any
import pandas as pd
import pprint

# Import gnomecode modules
from gnomecode.encoders import *
from gnomecode.utils import *

from jinja2 import Template

# Initialize Dash app
app = dash.Dash(__name__)

jinja_template = """
<!DOCTYPE html>
<html>
<head>
<!--It is necessary to use the UTF-8 encoding with plotly graphics to get e.g. negative signs to render correctly -->
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
</head>

<body>
<h1>Encoder Self-Similarity over Scalar Interval</h1>
{{ fig }}
</body>
</html>
"""


def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0 / (pl_entries - 1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = np.array(cmap(k * h)[:3]) * 255
        C = list(C.astype(np.uint8).astype(np.uint8))
        pl_colorscale.append([k * h, 'rgb' + str((int(C[0]), int(C[1]), int(C[2])))])

    return pl_colorscale


# Callbacks
@callback(
        [Output('anim-display', 'figure'),
         Input('region-options', 'value'),
         ]
)
def update_visualizations(region_options):
    """Update all visualizations based on current parameters."""

    anim_fig = create_animation()

    # Calculate metrics
    # metrics = calculate_encoder_metrics(multi_encoder, X_gnomes1, x_centers)

    # Create metrics display
    # metrics_display = [
    #         html.P(f"Total Bits: {metrics['total_bits']}"),
    #         html.P(f"Active Bits: {metrics['active_bits']}"),
    #         html.P(f"Interval Length: {metrics['interval_length']}"),
    #         html.P(f"Number of Encoders: {metrics['num_encoders']}"),
    # ]

    # return  metrics_display, anim_fig
    return (anim_fig,)


def create_animation() -> go.Figure:
    frames = []
    data_traces = []

    sliders_dict = {
            "active": 0, "yanchor": "top", "xanchor": "left",
            "currentvalue": { "font": {"size": 20}, "prefix": "Weight (w):", "visible": True, "xanchor": "right" },
            "transition": {"duration": 300, "easing": "linear"},
            "pad": {"b": 10, "t": 50}, "len": 0.9, "x": 0.1, "y": 0, "steps": []
    }

    for w_param in range(1, 5):
        multi_encoder = MultiEncoder(xmin=0.0, xmax=1.0)
        for i in [8, 11, 15]:
            multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=w_param))

        X_gnomes1 = multi_encoder.region_codes
        x_vals = multi_encoder.region_boundaries
        y_vals = multi_encoder.region_boundaries
        scores = count_similarity(X_gnomes1, X_gnomes1)
        y_indices = list(range(X_gnomes1.shape[1]))
        x_centers = multi_encoder.region_centers

        # Encode inputs
        encoded_transpose = X_gnomes1.T

        # Create heatmap
        go_encoder_bins = go.Heatmap(
                # go_encoder_bins = go.Contour(
                z=encoded_transpose,
                x=x_vals,
                y=y_indices,
                colorscale="greys",
                showscale=False,
                # hoverongaps=False,
                # name=str(w_param)
        )

        if len(data_traces) == 0:
            data_traces.append(go_encoder_bins)

        frames.append(go.Frame(data=[go_encoder_bins], traces=[0], name=str(w_param)))

        slider_step = {"args": [
                [str(w_param)],
                {"frame": {"duration": 0, "redraw": True}, "mode": "immediate",
                 "fromcurrent": True, "transition": {"duration": 100, "easing": "linear"}}],
                "label": str(w_param),
                # "method": "update"
                "method": "animate"
        }

        sliders_dict["steps"].append(slider_step)

    play_button_dict = dict(label="Play", method="animate",
                            args=[None, {"frame": {"duration": 600, "redraw": True}, "mode": "immediate",
                                         "fromcurrent": True, "transition": {"duration": 200, "easing": "linear"}}]
                            )
    pause_button_dict = dict(label="Pause", method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": True},
                                            "mode": "immediate", "fromcurrent": True,
                                            "transition": {"duration": 0, "easing": "linear"}}])

    updatemenus = [dict(type="buttons", buttons=[play_button_dict, pause_button_dict], direction="left",
                        pad={"r": 10, "t": 87}, showactive=False, x=0.1, xanchor="right", y=0, yanchor="top"),]

    anim_fig = go.Figure(
            data=data_traces,
            frames=frames,
            layout=go.Layout(updatemenus=updatemenus),
    )
    anim_fig.update_layout(
            sliders=[sliders_dict]
    )

    # X axes properties
    x_axis_properties = dict(range=[0.0, 1.0], autorange=False, showgrid=False, zeroline=False, linecolor='black',
                             showticklabels=True, ticks='', showline=False, tickmode='array',
                             tickvals=[0.0, 0.25, 0.5, 0.75, 1],
                             ticktext=["0", 0.25, 0.5, 0.75, "1.0"],
                             )

    anim_fig.update_layout(
            margin=dict(t=50, r=0, b=0, l=50),
            title="Active Bits over Scalar Interval", yaxis_title='Bit Index', xaxis_title='Scalar Value',
            xaxis=x_axis_properties, # yaxis=axis_template,
            width=500, height=500, plot_bgcolor='gray', showlegend=False, autosize=False,
    )

    # for i in y_indices:
    #     anim_fig.add_hline(y=i + 0.5, line_color='#2a3f5f', line_width=1.0)

    return anim_fig


def calculate_encoder_metrics(encoder, X_gnomes, x_vals) -> Dict[str, Any]:
    # weight w
    # total bits n
    # list of encoders and their 'w', 'n', 'offset', 'bounds'
    num_bits = encoder.n
    interval_length = encoder.L

    metrics = {
            'active_bits': np.count_nonzero(X_gnomes.T, axis=0)[0],
            'total_bits': int(num_bits),
            'interval_length': int(interval_length),
            'num_encoders': len(encoder.encoders),
    }

    return metrics


def setup():
    # fig = create_self_similarity_figure(params={"w": 1})
    # metrics_display, anim_fig = update_visualizations()
    anim_fig, = update_visualizations([])

    app.layout = html.Div([
            html.H1("Visualization of Multiple Scalar Encoders over Unit Interval"),

            # Control panel
            html.Div([
                    # Customize Visualization
                    html.Div([
                            html.H3("Visualization Options"),
                            dcc.Checklist(
                                    options=['Show Regions', 'Show Similarity Counts'],
                                    value=[], id='region-options', # inline=True
                            ),
                    ], style={'width': '30%', 'display': 'inline-block', 'margin-left': '1%'}),

                    # Metrics display
                    # html.Div([
                    #         html.H3("Encoder Metrics"),
                    #         html.Div(id='metrics-display')
                    # ], style={'width': '30%', 'display': 'inline-block', 'margin-left': '4%'}),

            ], style={'margin-bottom': '0px', 'padding': '20px', 'border': '1px solid #000'}),

            # Main visualization area
            html.Div([
                    html.Div([
                            dcc.Graph(id='anim-display')
                    ], style={'width': '50%', 'display': 'inline-block'}),

            ], style={'margin-bottom': '30px', 'padding': '20px', 'border': '1px solid #000'}),
    ])


if __name__ == '__main__':
    setup()
    app.run(debug=True, port=8010)

    # anim_fig = create_animation()
    # anim_fig.show()
