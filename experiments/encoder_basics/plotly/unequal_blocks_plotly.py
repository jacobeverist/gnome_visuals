import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import numpy.ma as ma
from icecream import ic
from dash import html
import seaborn as sns
from typing import Dict, List, Tuple, Any

# Import gnomecode modules
from gnomecode.encoders import *
from gnomecode.utils import *

from jinja2 import Template

# Initialize Dash app
app = dash.Dash(__name__)

# DONE: create a custom colorscale that matches original matplotlib
# DONE: set font to black
# DONE: create static HTML version
# DONE: add encoder parameter controls from original dashboard app
# DONE: added toggle plain heatmap version of self-similarity heatmap or with boxes to show region boundaries
# DONE: create separate toggles to show region boundaries and similarity counts
# DONE: create an animation
# DONE: remove original generated dashboard code after understanding
# DONE: check the included count_similarity function in utils and see if it performs the same
# TODO: draw latex-like graph axes
# TODO: build deployable github repo for app
#  - https://github.com/bradley-erickson/dash-app-structure
# TODO: deploy to digitialocean as app
#  - https://community.plotly.com/t/deploying-to-digital-oceans-app-platform/65669
#  - https://dash.plotly.com/deployment
#  - alternative platforms: heroku, Render, pythonanywhere, AWS, GCP, Azure
#  - digital ocean: 1 container, 1GB ram, 1 vcpu, $10/month
# TODO: customize the hover text labels
# TODO: adjust vertical layout so that side-by-side text and controls are aligned
# DONE: add display of encoder metrics (total bits, active bits, interval length, number of encoders)
# DONE: add description text below each figure
# DONE: add extra figure with encoder bins over interval
# DONE: did some refactoring of the layout, needs vertical alignment work


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
        [Output('self-similarity', 'figure'),
         Output('encoder-bins', 'figure'),
         Output('metrics-display', 'children'),
         Input('w-slider', 'value'),
         Input('region-options', 'value'),
         ]
)
def update_visualizations(w, region_options):
    """Update all visualizations based on current parameters."""

    multi_encoder = MultiEncoder(xmin=0.0, xmax=1.0)
    for i in [5, 7, 11, 13]:
        multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=w))

    X_gnomes1 = multi_encoder.region_codes
    x_vals = multi_encoder.region_boundaries
    y_vals = multi_encoder.region_boundaries
    scores = count_similarity(X_gnomes1, X_gnomes1)
    y_indices = list(range(X_gnomes1.shape[1]))
    x_centers = multi_encoder.region_centers

    ic("update_visualizations called", w, region_options)
    similarity_fig = create_self_similarity_figure(X_gnomes1, x_vals, y_vals, scores, {'w': w,
                                                    'show_regions': 'Show Regions' in region_options,
                                                    'show_counts': 'Show Similarity Counts' in region_options})


    encoder_bins_fig = create_encoder_heatmap(X_gnomes1, x_vals, y_indices, {'show_regions': 'Show Regions' in region_options})

    # Calculate metrics
    metrics = calculate_encoder_metrics(multi_encoder, X_gnomes1, x_centers)



    # Create metrics display
    metrics_display = [
            html.P(f"Total Bits: {metrics['total_bits']}"),
            html.P(f"Active Bits: {metrics['active_bits']}"),
            html.P(f"Interval Length: {metrics['interval_length']}"),
            html.P(f"Number of Encoders: {metrics['num_encoders']}"),
    ]



    return similarity_fig, encoder_bins_fig, metrics_display


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

def create_encoder_heatmap(X_gnomes, x_vals, y_indices, params: Dict[str, Any]) -> go.Figure:

    show_regions = params.get('show_regions', False)

    # Encode inputs
    encoded_transpose = X_gnomes.T

    # Create heatmap
    go_encoder_bins = go.Heatmap(
            z=encoded_transpose,
            x=x_vals,
            y=y_indices,
            colorscale="greys",
            showscale=False,
            hoverongaps=False,
    )

    fig = go.Figure(data=go_encoder_bins)

    if show_regions:
        fig.update_traces(xgap=0.5)

    # X axes properties
    x_axis_properties = dict(range=[0.0, 1.0], autorange=False,
                         showgrid=False, zeroline=False,
                         linecolor='black', showticklabels=True,
                         ticks='', showline=False,
                         tickmode='array',
                         tickvals=[0.0, 0.25, 0.5, 0.75, 1],
                         ticktext=["0", 0.25, 0.5, 0.75, "1.0"],
                         )

    fig.update_layout(
            margin=dict(t=50, r=0, b=0, l=50),
            title="Active Bits over Scalar Interval",
            yaxis_title='Bit Index',
            xaxis_title='Scalar Value',
            xaxis=x_axis_properties,
            # yaxis=axis_template,
            width=500, height=500,
            plot_bgcolor='gray',
            showlegend=False,
            autosize=False,
    )

    for i in y_indices:
        fig.add_hline(y=i + 0.5, line_color='#2a3f5f', line_width=1.0)

    return fig



def create_self_similarity_figure(X_gnomes, x_vals, y_vals, scores, params: Dict[str, Any]) -> go.Figure:
    w = params.get('w', 1)
    show_regions = params.get('show_regions', False)
    show_counts = params.get('show_counts', False)

    score_text = [[str(val) for val in score_row] for score_row in scores]

    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)

    plotly_colorscale = matplotlib_to_plotly(cmap, 255)

    go_heatmap = go.Heatmap(x=x_vals, y=y_vals, z=scores, colorscale=plotly_colorscale, zmax=4, zmin=0,
                            # xgap=0.5,
                            # ygap=0.5,
                            showscale=False)
    fig = go.Figure(data=go_heatmap)

    fig.update_layout(title="Self-Similarity of Codes over the Unit Interval",
                      yaxis_title='Scalar Value',
                      xaxis_title='Scalar Value',
                      )

    # specify the text to be displayed in each cell and the size optionally
    # by default will autosize to fit cell, but Heatmap cannot specify a max or min
    # fig.update_traces(text=score_text, texttemplate="%{z}", textfont_color="black")

    if show_regions:
        fig.update_traces(xgap=0.5, ygap=0.5)

    if show_counts:
        fig.update_traces(text=score_text, texttemplate="%{z}", textfont_color="black")

    # manually specify the ticks and tick labels of the heatmap
    fig.update_layout(
            xaxis=dict(
                    tickmode='array',
                    tickvals=[0.0, 0.25, 0.5, 0.75, 1],
                    ticktext=["0", 0.25, 0.5, 0.75, "1.0"],
                    # ticktext = ['0', 'Three', 'Five']
            ),
            yaxis=dict(
                    tickmode='array',
                    tickvals=[0, 0.25, 0.5, 0.75, 1],
                    ticktext=["0", 0.25, 0.5, 0.75, "1.0"],
                    # ticktext = ['One', 'Three', 'Five']
            )
    )

    # symmetric axes properties
    axis_template = dict(range=[0.0, 1.0], autorange=False,
                         showgrid=False, zeroline=False,
                         linecolor='black', showticklabels=True,
                         ticks='', showline=False)

    fig.update_layout(margin=dict(t=50, r=0, b=0, l=50),
                      xaxis=axis_template,
                      yaxis=axis_template,
                      showlegend=False,
                      width=500, height=500,
                      plot_bgcolor='gray',
                      autosize=False)

    return fig


def setup():
    # fig = create_self_similarity_figure(params={"w": 1})
    similarity_fig, encoder_bins_fig, metrics_display = update_visualizations(1, [])

    self_similarity_md_desc= dcc.Markdown('''
#### Description
- Several encoders are used to produce a combined gnome code for each scalar value.
- The self-similarity of the codes over the interval $[0, 1]$ is computed and displayed as a heatmap.
- Each cell indicates the number of bits in common between the codes for the corresponding scalar values indicated on the x and y axis.
- High similarity values along the diagonal over the matrix show the sensitivity of the encoding to representing nearness.

''', mathjax=True)
    encoder_bins_md_desc = dcc.Markdown('''
#### Description
- This figure shows the active bits along the unit interval

''', mathjax=True)

    app.layout = html.Div([
            html.H1("Visualization of Multiple Scalar Encoders over Unit Interval"),

            # Control panel
            html.Div([

                    # Customize Visualization
                    html.Div([
                            html.H3("Visualization Options"),
                            dcc.Checklist(
                                    options=['Show Regions', 'Show Similarity Counts'],
                                    value=[],
                                    # inline=True
                                    id='region-options',
                            ),
                    ], style={'width': '30%', 'display': 'inline-block', 'margin-left': '4%'}),

                    html.Div([
                            html.H3("Encoder Configuration"),
                            html.Label("Weight (w):"),
                            dcc.Slider(
                                    id='w-slider',
                                    min=1,
                                    max=2,
                                    value=1,
                                    step=1,
                                    marks={i: str(i) for i in [1, 2]},
                                    tooltip={"placement": "bottom", "always_visible": True}
                            )

                    ], style={'width': '30%', 'display': 'inline-block'}),

                    # Metrics display
                    html.Div([
                            html.H3("Encoder Metrics"),
                            html.Div(id='metrics-display')
                    ], style={'width': '30%', 'display': 'inline-block', 'margin-left': '4%'}),


            ], style={'margin-bottom': '30px', 'padding': '20px', 'border': '1px solid #ddd'}),
            # Main visualization area
            html.Div([
                    # Encoder activity heatmap
                    html.Div([
                            dcc.Graph(id='self-similarity'),
                    ], style={'width': '50%', 'display': 'inline-block'}),

                    html.Div([
                            dcc.Graph(id='encoder-bins'),
                    ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            html.Div([
                    html.Div([
                            self_similarity_md_desc
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div([
                            encoder_bins_md_desc
                    ], style={'width': '50%', 'display': 'inline-block'}),
            ]),

    ])

    output_html_path = r"self_similarity.html"
    # input_template_path = r"/path/to/template.html"

    plotly_jinja_data = {"fig": similarity_fig.to_html(full_html=False, include_plotlyjs='cdn', include_mathjax='cdn')}
    # consider also defining the include_plotlyjs parameter to point to an external Plotly.js as described above

    # with open(output_html_path, "w", encoding="utf-8") as output_file:
    #     j2_template = Template(jinja_template)
    #     output_file.write(j2_template.render(plotly_jinja_data))

    # fig.write_html("self_similarity.html")


if __name__ == '__main__':
    setup()
    app.run(debug=True, port=8010)

# NOTES and EXAMPLES
"""
# Converting Matplotlib figures to Plotly
# from plotly.tools import mpl_to_plotly

# from plotly.matplotlylib import mplexporter, PlotlyRenderer
# from plotly.matplotlylib import *

# create an mpl figure and store it under a varialble 'fig'
# renderer = PlotlyRenderer()
# exporter = mplexporter.Exporter(renderer)
# exporter.run(fig)

from plotly.tools import mpl_to_plotly
from matplotlib import pyplot as plt
import dash
import dash_html_components as html
import dash_core_components as dcc

app= dash.Dash()

fig= plt.figure()
ax= fig.add_subplot(111)
ax.plot(range(10), [i**2 for i in range(10)])
ax.grid(True)
plotly_fig = mpl_to_plotly(fig)

app.layout= html.Div([
    dcc.Graph(id= 'matplotlib-graph', figure=plotly_fig)
])
app.run_server(debug=True, port=8010, host='localhost')

['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
             'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
             'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
             'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
             'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
             'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
             'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
             'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
             'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
             'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
             'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
             'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
             'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
             'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
             'ylorrd'].

# Gnome similarity
# fig1 = px.imshow(
#     gnome_sim,
#     title='Gnome Similarity Matrix (Asymmetric)',
#     color_continuous_scale='viridis',
#     aspect='equal'
# )

# Define encoder options for dropdowns
# ENCODER_OPTIONS = [
#     {'label': 'Fixed Weight Encoder', 'value': 'fixed_weight'},
#     {'label': 'Tapering Weight Encoder', 'value': 'tapering_weight'},
# ]

# html.Div([
#     html.Label("Encoder Type:"),
#     dcc.Dropdown(
#         id='signal-type',
#         clearable=False,
#         options=[
#             {'label': 'Sine Wave', 'value': 'sine'},
#             {'label': 'Chirp', 'value': 'chirp'},
#             {'label': 'Step Function', 'value': 'step'},
#             {'label': 'Random Noise', 'value': 'noise'}
#         ],
#         value='sine'
#     ),
# ], style={'width': '30%', 'display': 'inline-block', 'margin-right': '5%'}),

# Default empty figures if failure to create plot somehow
# except Exception:
#     return [go.Figure() for _ in range(3)]




# plot a single line
# px.line(y=[1, 0])

# options that don't work in Heatmap
# fig.update_traces(textposition='inside')
# fig.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
# fig.update_layout(uniformtext={"minsize":20, "mode":'hide'})

# function that will update the axes directly instead of update_layout
fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
fig.update_xaxes(range=[0, 7])
fig.update_yaxes(range=[0, 2.5])

# absolutely-positioned annotation
# fig.add_annotation(text="Absolutely-positioned annotation",
#                    xref="x", yref="y",
#                    x=0.3, y=0.3)

# set coordinate references with xref= and yref=
#
# (x,y) or (x1,y1), or (x2,y2) coordinates are in line with values along each axis
# paper-coordinates are fractions of the entire figure which may sprawl between subplots
# container coordinates are fractions but ignore the margins (don't know how to specify)
# axis domain coordinates e.g., "x1 domain", specify a subplot and use fractions from 0 to 1 as coordinates

# Export to HTML
# https://plotly.com/python/interactive-html-export/

# Manually placing text scores in each rectangle

#     # add text box to center of each rectangle indicating count similarity
#     if annot:
#
#         # code to change the color of the text depending on cell color
#         # lum = relative_luminance(color)
#         # text_color = ".15" if lum > .408 else "w"
#         text_color = ".15"
#         # text_color = "w"
#
#         for i in range(len(x_centers)):
#             x = x_centers[i]
#             x_size = x_sizes[i]
#
#             for j in range(len(y_centers)):
#                 y = y_centers[j]
#                 y_size = y_sizes[j]
#                 score = masked_scores[j, i]
#
#                 min_size = min(x_size, y_size)
#
#                 draw_text = True
#                 if num_points < 80:
#                     fontsize = min_size * 4. * 32. / 0.2
#                 else:
#                     fontsize = 0
#                     draw_text = False
#
#                 if draw_text and score is not np.ma.masked and score > 0:
#                     ax.text(x, y, str(score), horizontalalignment='center', verticalalignment='center',
#                             fontsize=fontsize, color=text_color)


# Shape defined programatically
fig.add_shape(
        type='rect',
        x0=0.25, x1=0.75, y0=0.25, y1=0.75,
        xref='x', yref='y',
        line_color='cyan'
)
# filled rectangle
fig.add_shape(type="rect",
    x0=3, y0=1, x1=6, y1=2,
    line=dict(
        color="RoyalBlue",
        width=2,
    ),
    fillcolor="LightSkyBlue",
)
# Add a shape whose x and y coordinates refer to the domains of the x and y axes, placed relative to axis position and length
fig.add_shape(type="rect",
    xref="x domain", yref="y domain",
    x0=0.6, x1=0.7, y0=0.8, y1=0.9,
)

# Add line
fig.add_shape(type="line",
    x0=0, y0=0, x1=0.5, y1=0.5,
    xref='paper', yref='paper',
    line=dict(color="RoyalBlue",width=3)
)
fig.update_shapes(dict(xref='x', yref='y'))

# add a shape with a text label
fig.add_shape(
    type="rect",
    fillcolor='turquoise',
    x0=1,
    y0=1,
    x1=2,
    y1=3,
    label=dict(text="Text in rectangle")
)
# add a text label along the line
fig.add_shape(
    type="line",
    x0=3,
    y0=0.5,
    x1=5,
    y1=0.8,
    line_width=3,
    label=dict(text="Text above line")
)

# change position with textposition argument in label dict
# set the label angle with textangle=45


# horizontal line and rectangle
fig.add_hline(y=0.9)
fig.add_hrect(y0=0.9, y1=2.6, line_width=0, fillcolor="red", opacity=0.2)

# vertical line and rectangle
fig.add_vline(x=2.5, line_width=3, line_dash="dash", line_color="green")
fig.add_vrect(x0=0.9, x1=2)

# text annotation with line and rectangle
fig.add_hline(y=1, line_dash="dot",
              annotation_text="Jan 1, 2018 baseline", 
              annotation_position="bottom right",
              annotation_font_size=20,
              annotation_font_color="blue")
fig.add_vrect(x0="2018-09-24", x1="2018-12-18", 
              annotation_text="decline", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
              
# set across multiple subplots with "row" and "col" arguments
fig.add_hline(y=1, line_dash="dot", row=3, col="all",
              annotation_text="Jan 1, 2018 baseline", 
              annotation_position="bottom right")
fig.add_vrect(x0="2018-09-24", x1="2018-12-18", row="all", col=1,
              annotation_text="decline", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)

# enable drawing of new shape on layout
fig.update_layout(
    dragmode="drawrect",
    newshape=dict(
        label=dict(texttemplate="Change: %{dy:.2f}")
    ),
    # newshape=dict(line_color="cyan")
)

# adding a texst annotation within the boundary of the layout
fig.add_annotation(
        text=f"Error creating encoder",
        xref="paper", yref="paper",
        x=0.5, y=0.1, xanchor='center', yanchor='middle',
        showarrow=False, font=dict(size=16, color="red")
)



# variables in shape label texttemplate
# xcenter: (x0 + x1) / 2
# ycenter: (y0 + y1) / 2
# dx: x1 - x0
# dy: y1 - y0
# width: abs(x1 - x0)
# height: abs(y1 - y0)
# length (for lines only): sqrt(dx^2 + dy^2)
# slope: (y1 - y0) / (x1 - x0)

"""
