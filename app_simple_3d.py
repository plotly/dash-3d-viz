import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash_canvas.utils import array_to_data_url
from nilearn import image

img = image.load_img('assets/radiopaedia_org_covid-19-pneumonia-7_85703_0-dcm.nii')
mat = img.affine
img = img.get_data()
img_1 = np.copy(np.moveaxis(img, -1, 0))
img_2 = np.copy(np.moveaxis(img, -1, 1))

l_h = img.shape[-1]
l_lat = img.shape[0]

size_factor = abs(mat[2, 2] / mat[0, 0])

slices_1 = [array_to_data_url(img_1[i], img_format='jpeg') for i in range(img_1.shape[0])]
slices_2 = [array_to_data_url(img_2[i], img_format='jpeg') for i in range(img_2.shape[0])] # vertical


def make_figure(filename_uri, width, height, row=None, col=None, size_factor=1):
    fig = go.Figure()
    # Add trace
    fig.add_trace(
        go.Scatter(x=[], y=[])
    )
    # Add images
    fig.add_layout_image(
        dict(
            source=filename_uri,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=width,
            sizey=height * size_factor,
            sizing="stretch",
            layer="below"
        )
    )
    fig.update_layout(template=None, margin=dict(t=10, b=0))
    fig.update_xaxes(
            showgrid=False, range=(0, width),
            showticklabels=False,
            zeroline=False)
    fig.update_yaxes(
            showgrid=False, scaleanchor='x', range=(height, 0),
            showticklabels=False,
            zeroline=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    if row is None:
        row = height // 2
    if col is None:
        col = width // 2
    fig.add_shape(
            type='line',
            x0=width // 2 - 50,
            x1=width // 2 + 50,
            y0=row,
            y1=row,
            line=dict(width=5, color='red'),
            fillcolor='pink')
    fig.update_layout(dragmode='drawclosedpath', newshape_line_color='cyan')
    return fig



app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='graph', figure=make_figure(slices_1[len(img_1) // 2], width=630, height=630)),
        dcc.Slider(id='slider', min=0, max=len(img_1) - 1, step=1,
               value=len(img_1) // 2,
               updatemode='drag'),
        html.H6(id='slider-display'),
        html.Button('interpolate', id='interp-button'),
        ],
        style={'width':'50%', 'display':'inline-block'}),
    html.Div([
    dcc.Graph(id='graph-2', figure=make_figure(slices_2[len(img_2) // 2], width=630, height=45*size_factor)),
    dcc.Slider(id='slider-2', min=0, max=len(img_2) - 1, step=1,
               value= len(img_2) // 2,
               updatemode='drag'),
        html.H6(id='slider-2-display'),
        ],
        style={'width':'50%', 'display':'inline-block'}),
    dcc.Store(id='small-slices', data=slices_1),
    dcc.Store(id='small-slices-2', data=slices_2),
    dcc.Store(id='z-pos', data=l_h // 2),
    dcc.Store(id='x-pos', data=l_lat // 2),
    dcc.Store(id='annotations', data={})
        ])


@app.callback(
    [Output('graph', 'figure'),
     Output('slider-display', 'children'),
     Output('graph-2', 'figure'),
     Output('slider-2-display', 'children'),
     Output('z-pos', 'data'),
     Output('x-pos', 'data'),
     Output('annotations', 'data')
     ],
    [Input('slider', 'value'),
     Input('slider-2', 'value'),
     Input('graph', 'relayoutData')
     ],
    [State('small-slices', 'data'),
     State('small-slices-2', 'data'),
     State('z-pos', 'data'),
     State('x-pos', 'data'),
     State('annotations', 'data')
    ])
def update_figure(n_slider, n_slider_2, relayout, slices, slices_2, z_pos, x_pos, annotations):
    if not any(event for event in (n_slider, n_slider_2, relayout)):
        return (dash.no_update,) * 7
    ctx = dash.callback_context
    event = ctx.triggered[0]['prop_id']
    print(annotations)
    if event == 'graph.relayoutData' and 'shapes' in relayout:
        shape = relayout['shapes'][-1]
        annotations[z_pos] = shape
        return (dash.no_update,)*6 + (annotations,)
    elif event == 'slider-2.value':
        slice_index_2 = int(n_slider_2)
        x_pos = slice_index_2
        fig_2 = make_figure(slices_2[slice_index_2], width=l_lat, height=l_h * size_factor, row=int(z_pos * size_factor))
        fig_1 = make_figure(slices_1[z_pos], width=l_lat, height=l_lat, row=x_pos)
        slice_index_1 = dash.no_update
    else: # slider 1
        slice_index_1 = int(n_slider)
        z_pos = slice_index_1
        fig_1 = make_figure(slices[slice_index_1], width=l_lat, height=l_lat, row=x_pos)
        if str(z_pos) in annotations:
            fig_1.add_shape(annotations[str(z_pos)])
        fig_2 = make_figure(slices_2[x_pos], width=l_lat, height=l_h * size_factor, row=int(z_pos * size_factor))
        slice_index_2 = dash.no_update
    return fig_1, slice_index_1, fig_2, slice_index_2, z_pos, x_pos, annotations


if __name__ == '__main__':
    app.run_server(debug=True)
