import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from skimage import data
from skimage import img_as_ubyte
from dash_canvas.utils import array_to_data_url
from joblib import Memory

memory = Memory('.', verbose=0)
binary_blobs = memory.cache(data.binary_blobs)

img = img_as_ubyte(binary_blobs(length=512, n_dim=3, seed=0))
downsample = 5
small_slices = [array_to_data_url(img[i, ::downsample, ::downsample]) for i in range(img.shape[0])]


def make_figure(filename_uri, width, height):
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
            sizey=height,
            sizing="contain",
            layer="below"
        )
    )
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, range=(0, width),
    #showticklabels=False,
    zeroline=False)
    fig.update_yaxes(showgrid=False, scaleanchor='x', range=(height, 0),
    #showticklabels=False,
    zeroline=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig



app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph'),
    dcc.Slider(id='slider', min=0, max=len(img), step=1, 
               # updatemode can be drag or mouseup, interesting to test with both
               updatemode='drag'),
    dcc.Store(id='small-slices', data=small_slices),
    dcc.Store(id='full-slice'),
    dcc.Store(id='resolution-state', data='coarse'),
    dcc.Interval(id='interval', interval=200)
        ])

@app.callback(
    [Output('graph', 'figure'),
     Output('resolution-state', 'data')],
    [Input('slider', 'value'),
     Input('full-slice', 'data')],
    [State('small-slices', 'data')])
def update_figure(n_slider, full_cut, slices):
    if n_slider is None or full_cut is None:
        return dash.no_update
    ctx = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if ctx == 'slider.value':
        return make_figure(slices[int(n_slider)], width=100, height=100), 'coarse'
    if ctx == 'full-slice.data':
        return make_figure(full_cut['cut'], width=512, height=512), 'fine'
    else:
        return dash.no_update, dash.no_update


@app.callback(
    Output('full-slice', 'data'),
    [Input('interval', 'n_intervals')],
    [State('slider', 'value'),
     State('full-slice', 'data'),
     State('resolution-state', 'data')])
def load_slice(n, n_slider, full_cut, res_state):
    if n_slider is None:
        return dash.no_update
    if full_cut is not None:
        print(full_cut['index'])
    if full_cut is not None and full_cut['index'] == n_slider and res_state == 'coarse':
        return dash.no_update
    return dict(cut=array_to_data_url(img[int(n_slider)]), index=int(n_slider))


if __name__ == '__main__':
    app.run_server(debug=True)

